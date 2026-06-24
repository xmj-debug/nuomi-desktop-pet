import sys
from pathlib import Path
from types import SimpleNamespace


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

import ai_moe_pet as app


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def fake_battery(percent, plugged, seconds):
    return lambda: SimpleNamespace(percent=percent, power_plugged=plugged, secsleft=seconds)


class FakeStatus:
    def __init__(self):
        self.text = ""
        self.visible = None

    def setText(self, value):
        self.text = value

    def setVisible(self, value):
        self.visible = bool(value)


def main():
    config = dict(app.DEFAULT_CONFIG)
    config.update(
        {
            "BatteryAlertsEnabled": True,
            "BatteryLowPercent": 20,
            "BatteryFullPercent": 95,
        }
    )

    unsupported = app.battery_snapshot(provider=lambda: None)
    require(not unsupported["available"], "no-battery device was not handled")

    low = app.battery_snapshot(provider=fake_battery(15, False, 2 * 3600 + 5 * 60))
    require(low["available"] and low["seconds_left"] == 7500, "battery runtime parsing failed")
    low_issues = app.battery_alert_issues(config, low)
    require(low_issues and low_issues[0][0] == "battery_low", "low battery alert missing")
    require("2 小时 5 分钟" in low_issues[0][1], "remaining time missing from low alert")

    full = app.battery_snapshot(provider=fake_battery(96, True, app.psutil.POWER_TIME_UNLIMITED))
    full_issues = app.battery_alert_issues(config, full)
    require(full["seconds_left"] is None, "plugged battery should not show discharge runtime")
    require(full_issues and full_issues[0][0] == "battery_full", "full battery alert missing")

    normal = app.battery_snapshot(provider=fake_battery(55, False, 3 * 3600))
    require(not app.battery_alert_issues(config, normal), "normal battery produced an alert")
    require("正在使用电池" in app.battery_status_lines(config, normal)[0], "battery status text is wrong")

    old_calls = (app.psutil.cpu_percent, app.psutil.virtual_memory, app.psutil.net_io_counters)
    blocker = lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("expensive metric called"))
    app.psutil.cpu_percent = blocker
    app.psutil.virtual_memory = blocker
    app.psutil.net_io_counters = blocker
    try:
        dummy = SimpleNamespace(
            config={"PetName": "糯米", "ShowStatus": True},
            focus_active=False,
            state="待机",
            status=FakeStatus(),
        )
        app.PetWindow.update_status(dummy)
        require(dummy.status.text.startswith("糯米"), "desktop status did not refresh")
        require(dummy.status.visible is True, "desktop status visibility did not refresh")
    finally:
        app.psutil.cpu_percent, app.psutil.virtual_memory, app.psutil.net_io_counters = old_calls

    reminder_calls = []
    saved_snapshot = app.system_health_snapshot
    saved_load = app.load_pet_memory
    saved_save = app.save_pet_memory
    try:
        app.system_health_snapshot = lambda _config: {
            "issues": [("battery_low", "电池仅剩 15%，请及时接通电源")]
        }
        app.load_pet_memory = lambda: {}
        saved_memory = {}
        app.save_pet_memory = lambda data: saved_memory.update(data)
        dummy = SimpleNamespace(
            config={"SystemHealthWatchEnabled": True, "HealthAlertCooldownMinutes": 15},
            health_bad_counts={},
            health_last_alert={},
            notify_due_reminder=lambda title, message, icon=None, duration=0: reminder_calls.append(
                (title, message, duration)
            ),
        )
        app.PetWindow.check_system_health(dummy)
        require(reminder_calls and reminder_calls[0][0] == "低电量提醒", "low battery did not use reminder path")
        require(reminder_calls[0][2] == 12000, "low battery reminder duration changed")
        require("health_last_alert" in saved_memory, "health alert timestamps were not persisted")
    finally:
        app.system_health_snapshot = saved_snapshot
        app.load_pet_memory = saved_load
        app.save_pet_memory = saved_save

    print(
        {
            "unsupported_device": "handled",
            "low_battery": low_issues[0][1],
            "full_battery": full_issues[0][1],
            "normal_battery": "no alert",
            "status_refresh_expensive_metrics": "not called",
            "low_battery_reminder_path": "necessary reminder",
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
