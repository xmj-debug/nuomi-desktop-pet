import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

import ai_moe_pet as app


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    config = dict(app.DEFAULT_CONFIG)
    config.update(
        {
            "VoiceEnabled": True,
            "AmbientVoiceCooldownMinutes": 15,
            "FullscreenReminderOnly": True,
            "QuietMode": False,
        }
    )

    require(
        app.voice_policy_allows(config, "ambient", False, 0, now=10_000),
        "first ambient voice should be allowed",
    )
    require(
        not app.voice_policy_allows(config, "ambient", False, 9_500, now=10_000),
        "ambient cooldown did not suppress repeated speech",
    )
    require(
        app.voice_policy_allows(config, "interaction", False, 9_500, now=10_000),
        "foreground interaction should not use ambient cooldown",
    )
    require(
        not app.voice_policy_allows(config, "ambient", True, 0, now=10_000),
        "fullscreen ambient speech was not suppressed",
    )
    require(
        not app.voice_policy_allows(config, "interaction", True, 0, now=10_000),
        "fullscreen interaction speech was not suppressed",
    )
    require(
        app.voice_policy_allows(config, "reminder", True, 9_900, now=10_000),
        "fullscreen reminder should be allowed",
    )

    quiet = dict(config, QuietMode=True)
    require(
        not app.voice_policy_allows(quiet, "ambient", False, 0, now=10_000),
        "quiet mode ambient speech was not suppressed",
    )
    require(
        app.voice_policy_allows(quiet, "reminder", True, 0, now=10_000),
        "quiet mode should preserve necessary reminders",
    )

    disabled = dict(config, VoiceEnabled=False)
    require(
        not app.voice_policy_allows(disabled, "reminder", True, 0, now=10_000),
        "disabled voice still allowed reminders",
    )

    print(
        {
            "ambient_cooldown_minutes": config["AmbientVoiceCooldownMinutes"],
            "fullscreen_ambient": "blocked",
            "fullscreen_interaction": "blocked",
            "fullscreen_reminder": "allowed",
            "quiet_reminder": "allowed",
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
