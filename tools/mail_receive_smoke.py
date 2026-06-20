import imaplib
import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
CONFIG = BASE / "pet-config.json"


def load_accounts():
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return [
        item
        for item in config.get("MailAccounts", []) or []
        if isinstance(item, dict) and item.get("Enabled") is not False
    ]


def check(account):
    host = account.get("Host")
    port = int(account.get("Port", 993))
    user = account.get("User")
    password = account.get("Password")
    with imaplib.IMAP4_SSL(host, port, timeout=18) as client:
        client.login(user, password)
        client.select("INBOX")
        _, unseen = client.search(None, "UNSEEN")
        unread = len(unseen[0].split()) if unseen and unseen[0] else 0
        return unread


def main():
    failed = False
    for account in load_accounts():
        label = account.get("Label") or account.get("User") or account.get("Provider")
        try:
            unread = check(account)
            print(f"OK {label}: unread={unread}")
        except Exception as exc:
            failed = True
            print(f"FAIL {label}: {exc}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
