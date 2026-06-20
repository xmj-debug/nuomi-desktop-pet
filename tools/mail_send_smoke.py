import json
import re
import smtplib
import sys
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
CONFIG = BASE / "pet-config.json"


def load_config():
    return json.loads(CONFIG.read_text(encoding="utf-8-sig"))


def accounts_from_config(config):
    accounts = []
    for item in config.get("MailAccounts", []) or []:
        if isinstance(item, dict) and item.get("Enabled") is not False:
            accounts.append(item)
    return accounts


def provider_account(accounts, provider):
    for account in accounts:
        if account.get("Provider") == provider:
            return account
    return None


def smtp_settings(provider):
    if provider == "gmail":
        return "smtp.gmail.com", 465
    if provider == "qq":
        return "smtp.qq.com", 465
    raise ValueError(f"unsupported provider: {provider}")


def send(account, to_addr, tag):
    provider = account.get("Provider")
    host, port = smtp_settings(provider)
    user = account.get("User", "")
    password = account.get("Password", "")
    subject = f"桌宠发件测试 {tag} {datetime.now():%Y-%m-%d %H:%M:%S}"
    body = (
        "这是一封桌宠 SMTP 发件测试邮件。\n"
        f"方向：{tag}\n"
        f"时间：{datetime.now().isoformat(timespec='seconds')}\n"
    )
    message = EmailMessage()
    message["From"] = user
    message["To"] = to_addr
    message["Subject"] = subject
    message.set_content(body)
    with smtplib.SMTP_SSL(host, port, timeout=25) as client:
        client.login(user, password)
        client.send_message(message)
    return subject


def main():
    config = load_config()
    accounts = accounts_from_config(config)
    qq = provider_account(accounts, "qq")
    gmail = provider_account(accounts, "gmail")
    if not qq or not gmail:
        print("FAIL missing qq or gmail account")
        return 2
    tests = [
        (qq, gmail.get("User", ""), "QQ -> Gmail"),
        (gmail, qq.get("User", ""), "Gmail -> QQ"),
    ]
    failed = False
    for account, to_addr, tag in tests:
        try:
            subject = send(account, to_addr, tag)
            print(f"OK {tag}: {subject}")
        except Exception as exc:
            failed = True
            clean = re.sub(r"(?i)(password|auth|token|key)[^\\n]*", "[hidden]", str(exc))
            print(f"FAIL {tag}: {clean}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
