import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

import ai_moe_pet as app


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def config_secret_state(config):
    accounts = [item for item in config.get("MailAccounts", []) or [] if isinstance(item, dict)]
    return {
        "ai": bool(config.get("AiApiKey")),
        "qq": bool(config.get("MailPassword")),
        "gmail": bool(config.get("GmailPassword")),
        "accounts": [bool(item.get("Password")) for item in accounts],
    }


def inspect_zip(path):
    with zipfile.ZipFile(path, "r") as archive:
        require(archive.testzip() is None, f"bad zip entry in {path.name}")
        names = [name for name in archive.namelist() if not name.endswith("/")]
        require(len(names) == len(set(names)), f"duplicate paths in {path.name}")
        require(
            not any(Path(name).is_absolute() or ".." in Path(name).parts for name in names),
            f"unsafe path in {path.name}",
        )
        return names


def test_backup(work):
    target = work / "backup-no-secrets.zip"
    app.create_backup_archive(target, include_secrets=False, include_clipboard=True)
    inspect_zip(target)
    with zipfile.ZipFile(target, "r") as archive:
        config = json.loads(archive.read("data/pet-config.json").decode("utf-8-sig"))
    state = config_secret_state(config)
    require(not state["ai"] and not state["qq"] and not state["gmail"], "no-secrets backup still contains a top-level secret")
    require(not any(state["accounts"]), "no-secrets backup still contains a mail account password")
    return target


def test_update_package(work):
    target = BASE / "dist" / f"nuomi-update-v{app.APP_VERSION}.zip"
    app.create_update_package(target)
    names = inspect_zip(target)
    require("update-manifest.json" in names, "update manifest missing")
    stage = work / "update-stage"
    stage.mkdir(parents=True, exist_ok=True)
    manifest = app.validate_and_extract_update(target, stage)
    require(manifest.get("version") == app.APP_VERSION, "update version mismatch")

    apply_root = work / "update-apply-root"
    apply_root.mkdir(parents=True, exist_ok=True)
    private_config = '{"AiApiKey":"keep-private","GmailPassword":"keep-private"}'
    (apply_root / "pet-config.json").write_text(private_config, encoding="utf-8")
    for name in ("ai_moe_pet.py", "_kaoyan_data.py", "nuomi_watchdog.py"):
        (apply_root / name).write_text("old", encoding="utf-8")
    app.apply_staged_update(stage, apply_root)
    require((apply_root / "pet-config.json").read_text(encoding="utf-8") == private_config, "update overwrote private config")
    require((apply_root / "ai_moe_pet.py").stat().st_size > 100000, "core app was not updated")
    return target


def test_portable(work, target):
    source_config = app.load_config()
    source_secret_state = config_secret_state(source_config)
    app.create_portable_package(target, include_secrets=True, include_clipboard=True)
    names = inspect_zip(target)
    required = {
        "ai_moe_pet.py",
        "nuomi_watchdog.py",
        "pet-config.json",
        "START_HERE.bat",
        "Install-Nuomi.ps1",
        "manifest.json",
        "runtime/python312/python.exe",
        "runtime/python312/pythonw.exe",
    }
    require(required.issubset(set(names)), f"portable package missing: {sorted(required - set(names))}")
    with zipfile.ZipFile(target, "r") as archive:
        manifest = json.loads(archive.read("manifest.json").decode("utf-8-sig"))
        config = json.loads(archive.read("pet-config.json").decode("utf-8-sig"))
        install_script = archive.read("Install-Nuomi.ps1").decode("utf-8-sig")
    require(manifest.get("include_secrets") is True, "private migration manifest lost include_secrets")
    require(manifest.get("include_python_runtime") is True, "portable Python runtime was not included")
    require(config_secret_state(config) == source_secret_state, "private migration secret state differs from source")
    require("--update-before-start" in install_script, "installer does not check online updates")

    extract_root = work / "portable-extracted"
    with zipfile.ZipFile(target, "r") as archive:
        archive.extractall(extract_root)
    python = extract_root / "runtime" / "python312" / "python.exe"
    probe = subprocess.run(
        [
            str(python),
            "-c",
            (
                "import PySide6, psutil, httpx, PIL, ai_moe_pet; "
                "print(ai_moe_pet.APP_VERSION, ai_moe_pet.DEFAULT_UPDATE_REPO)"
            ),
        ],
        cwd=extract_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    require(probe.returncode == 0, f"portable runtime import failed: {probe.stderr.strip()}")
    return target, probe.stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--portable",
        default=str(BASE / "backups" / f"nuomi-portable-private-v{app.APP_VERSION}.zip"),
    )
    args = parser.parse_args()

    work = BASE / "migration-test"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    backup = test_backup(work)
    update = test_update_package(work)
    portable, probe = test_portable(work, Path(args.portable))
    print(
        json.dumps(
            {
                "backup": str(backup),
                "update": str(update),
                "portable": str(portable),
                "portable_mb": round(portable.stat().st_size / (1024 * 1024), 1),
                "runtime_probe": probe,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
