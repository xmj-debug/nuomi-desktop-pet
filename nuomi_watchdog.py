import ctypes
import ctypes.wintypes
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil


BASE = Path(__file__).resolve().parent
APP = BASE / "ai_moe_pet.py"
SHUTDOWN_FLAG = BASE / "pet-shutdown.flag"
UPDATE_LOCK = BASE / "pet-update.lock"
LOG = BASE / "pet-runtime.log"
MUTEX_NAME = "Local\\NuomiPetWatchdog"
ERROR_ALREADY_EXISTS = 183


def log(message):
    try:
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"[{datetime.now().isoformat(timespec='seconds')}] watchdog: {message}\n")
    except Exception:
        pass


def pythonw_executable():
    current = Path(sys.executable)
    if current.name.lower() == "python.exe":
        candidate = current.with_name("pythonw.exe")
        if candidate.exists():
            return str(candidate)
    if current.name.lower() == "pythonw.exe" and current.exists():
        return str(current)
    candidate = Path.home() / "AppData" / "Local" / "Programs" / "Python" / "Python312" / "pythonw.exe"
    if candidate.exists():
        return str(candidate)
    return sys.executable


def acquire_mutex():
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.restype = ctypes.wintypes.HANDLE
    kernel32.CreateMutexW(None, True, MUTEX_NAME)
    return kernel32.GetLastError() != ERROR_ALREADY_EXISTS


def app_is_running():
    marker = str(APP).lower()
    for proc in psutil.process_iter(["pid", "cmdline"]):
        try:
            if proc.pid == os.getpid():
                continue
        except Exception:
            pass
        try:
            cmdline = " ".join(proc.info.get("cmdline") or []).lower()
        except Exception:
            continue
        if marker in cmdline or "ai_moe_pet.py" in cmdline:
            return True
    return False


def start_app():
    subprocess.Popen(
        [pythonw_executable(), str(APP)],
        cwd=str(BASE),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=0x08000000,
    )
    log("pet started")


def main():
    if not acquire_mutex():
        return
    log("started")
    while True:
        if SHUTDOWN_FLAG.exists():
            log("shutdown flag found, exiting")
            return
        if UPDATE_LOCK.exists():
            time.sleep(1)
            continue
        if not app_is_running():
            try:
                start_app()
            except Exception as exc:
                log(f"start failed: {exc}")
        time.sleep(5)


if __name__ == "__main__":
    main()
