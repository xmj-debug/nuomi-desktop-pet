import importlib
import json
import os
import shutil
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
CONFIG = BASE / "pet-config.json"
RUNTIME_LOG = BASE / "pet-runtime.log"
WORDBOOK = BASE / "pet-wordbook.json"
DOG_FRAMES = BASE / "assets" / "dog_frames"
STARTER = BASE / "start_ai_moe_pet.bat"
USERPROFILE = Path(os.environ.get("USERPROFILE", ""))
TOOLBOX_ROOT_CANDIDATES = [
    USERPROFILE / "OneDrive" / "文档" / "New project 3",
    USERPROFILE / "OneDrive" / "Documents" / "New project 3",
    USERPROFILE / "Documents" / "New project 3",
    BASE,
]
BUNDLED_NODE = (
    USERPROFILE
    / ".cache"
    / "codex-runtimes"
    / "codex-primary-runtime"
    / "dependencies"
    / "node"
    / "bin"
    / "node.exe"
)


def ok(name, detail=""):
    print(f"OK {name}{': ' + detail if detail else ''}")


def fail(name, detail):
    print(f"FAIL {name}: {detail}")
    return False


def path_exists(path):
    try:
        return Path(path).exists()
    except OSError:
        return False


def path_is_file(path):
    try:
        candidate = Path(path)
        return candidate.exists() and candidate.is_file()
    except OSError:
        return False


def check_json(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return fail(path.name, str(exc)), None
    ok(path.name)
    return True, data


def unique_paths(paths):
    unique = []
    seen = set()
    for path in paths:
        candidate = Path(path)
        key = str(candidate).casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def find_toolbox_server():
    for root in unique_paths(TOOLBOX_ROOT_CANDIDATES):
        server = root / "server.js"
        if path_exists(server):
            return server
    return None


def node_candidates():
    candidates = []
    path_node = shutil.which("node")
    if path_node:
        candidates.append(Path(path_node))
    for env_name in ("PROGRAMFILES", "PROGRAMFILES(X86)"):
        env_value = os.environ.get(env_name)
        if env_value:
            candidates.append(Path(env_value) / "nodejs" / "node.exe")
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        local_root = Path(local_app_data)
        candidates.extend(
            [
                local_root / "Programs" / "nodejs" / "node.exe",
                local_root / "nodejs" / "node.exe",
            ]
        )
    candidates.append(BUNDLED_NODE)
    return unique_paths(candidates)


def find_node():
    for candidate in node_candidates():
        if path_is_file(candidate):
            return candidate
    return None


def main():
    success = True
    if not CONFIG.exists():
        success = fail("config", "pet-config.json missing")
        config = {}
    else:
        passed, config = check_json(CONFIG)
        success = success and passed

    for module in ("PySide6", "psutil", "httpx", "PIL"):
        try:
            importlib.import_module(module)
            ok(f"dependency {module}")
        except Exception as exc:
            success = fail(f"dependency {module}", str(exc)) and success

    pythonw = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python312" / "pythonw.exe"
    if path_exists(pythonw):
        ok("pythonw", str(pythonw))
    else:
        success = fail("pythonw", str(pythonw)) and success

    if path_exists(STARTER):
        ok("starter", STARTER.name)
    else:
        success = fail("starter", "start_ai_moe_pet.bat missing") and success

    toolbox_server = find_toolbox_server()
    if toolbox_server:
        ok("toolbox server", str(toolbox_server))
    else:
        success = fail("toolbox server", "server.js missing") and success

    node = find_node()
    if node:
        ok("node", str(node))
    else:
        success = fail("node", "node.exe not found in PATH/common installs/bundled runtime") and success

    frames = list(DOG_FRAMES.glob("*.png")) if DOG_FRAMES.exists() else []
    if len(frames) >= 20:
        ok("dog frames", str(len(frames)))
    else:
        success = fail("dog frames", f"only {len(frames)} png files") and success

    accounts = [
        item
        for item in config.get("MailAccounts", []) or []
        if isinstance(item, dict) and item.get("Enabled") is not False
    ]
    providers = {item.get("Provider") for item in accounts}
    if {"qq", "gmail"}.issubset(providers):
        ok("mail accounts", ", ".join(sorted(providers)))
    else:
        success = fail("mail accounts", f"providers={sorted(providers)}") and success

    if config.get("AiEndpoint") and config.get("AiModel") and config.get("AiApiKey"):
        ok("AI config", config.get("AiModel", ""))
    else:
        success = fail("AI config", "endpoint/model/key incomplete") and success

    if WORDBOOK.exists():
        try:
            words = json.loads(WORDBOOK.read_text(encoding="utf-8-sig"))
            ok("wordbook", f"{len(words) if isinstance(words, list) else 0} words")
        except Exception as exc:
            success = fail("wordbook", str(exc)) and success
    else:
        success = fail("wordbook", "pet-wordbook.json missing") and success

    if RUNTIME_LOG.exists():
        lines = RUNTIME_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
        tail = lines[-1] if lines else "empty"
        ok("runtime log", tail)
    else:
        success = fail("runtime log", "missing") and success

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
