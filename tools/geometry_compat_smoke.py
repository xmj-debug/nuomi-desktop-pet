import os
import sys
from pathlib import Path


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QWidget

import ai_moe_pet as app


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def color_distance(a, b):
    return abs(a.red() - b.red()) + abs(a.green() - b.green()) + abs(a.blue() - b.blue())


def rect_inside(outer, pos, size):
    rect = QRect(pos, size)
    return (
        rect.left() >= outer.left()
        and rect.right() <= outer.right()
        and rect.top() >= outer.top()
        and rect.bottom() <= outer.bottom()
    )


def main():
    qt_app = QApplication.instance() or QApplication([])
    screen = qt_app.primaryScreen()
    require(screen is not None, "Qt did not provide a primary screen")
    bounds = screen.availableGeometry()
    size = QSize(260, 180)

    for pos in (QPoint(-99999, -99999), QPoint(99999, 99999), QPoint(bounds.left() + 20, bounds.top() + 20)):
        safe = app.clamp_window_position(pos, size)
        require(rect_inside(bounds, safe, size), f"window position was not clamped: {safe}")

    default_pos = app.default_window_position(size)
    require(rect_inside(bounds, default_pos, size), "default window position is outside the screen")

    config = dict(app.DEFAULT_CONFIG)
    config.update(
        {
            "BubbleBackgroundColor": "#111827",
            "BubbleBorderColor": "#fbbf24",
            "BubbleBorderWidth": 3,
            "BubbleBorderRadius": 16,
            "BubbleFontSize": 18,
        }
    )
    bubble = app.Bubble(config)
    bubble.setText("气泡尖角融合测试")
    bubble.resize(320, 118)
    bubble.tail_tip_x = 160
    bubble.show()
    qt_app.processEvents()
    image = bubble.grab().toImage()
    require(not image.isNull(), "bubble render produced a null image")

    frame = app.bubble_frame(config)
    _tail_width, tail_height = app.bubble_tail_size(config)
    inset = frame["width"] / 2 + 0.5
    body_rect = bubble.rect().adjusted(int(inset), int(inset), -int(inset), -int(inset + tail_height))
    tip_x = app.bubble_tail_tip_x(bubble.width(), config, target_x=bubble.tail_tip_x)
    sample = image.pixelColor(tip_x, max(body_rect.top(), body_rect.bottom() - 1))
    background = QColor(config["BubbleBackgroundColor"])
    border = QColor(config["BubbleBorderColor"])
    require(
        color_distance(sample, background) < color_distance(sample, border),
        f"tail seam sample looked closer to border than fill: {sample.name()}",
    )

    for width in (150, 260, 520):
        min_tip, max_tip = app.bubble_tail_tip_bounds(width, config)
        for target in (-300, width // 2, width + 300):
            tip = app.bubble_tail_tip_x(width, config, target_x=target)
            require(min_tip <= tip <= max_tip, "tail tip escaped clamp bounds")

    pet_rect = QRect(280, 410, 220, 220)
    center_anchor = app.pet_bubble_anchor_x(pet_rect, avoid_center=False)
    word_anchor = app.pet_bubble_anchor_x(pet_rect, avoid_center=True, side_hint=1)
    left_word_anchor = app.pet_bubble_anchor_x(pet_rect, avoid_center=True, side_hint=-1)
    require(center_anchor == pet_rect.center().x(), "normal bubble no longer points at pet center")
    require(word_anchor > center_anchor + 16, "word bubble tail did not avoid pet center")
    require(left_word_anchor < center_anchor - 16, "left-side word bubble tail did not avoid pet center")

    long_word_text = (
        "考研英语词汇  单击换一批\n"
        "abbreviation  缩写词，缩略形式\n"
        "conscientious  认真的，尽责的，一丝不苟的\n"
        "infrastructure  基础设施，基础结构\n"
        "phenomenon  现象，特殊的人或事物\n"
        "substantial  大量的，实质性的，重要的"
    )
    _word_width, word_height = bubble.fitted_message_size(bubble.wrap_friendly_text(long_word_text), 440, 0)
    require(word_height > 220, "word bubble is still capped at the old fixed height")
    require(word_height <= 420, "word bubble grew beyond the safe dynamic height")

    long_weather = "上海 27°C 局部多云；明天 21~24°C 附近有零星小雨，午后短时阵风，湿度较高，体感偏闷"
    weather_lines = app.weather_card_text(long_weather).splitlines()
    require(1 <= len(weather_lines) <= 2, "weather card summary should fit two lines")
    require(all(len(line) <= 24 for line in weather_lines), "weather card line is too long")
    require(app.weather_card_text("天气查询失败：network timeout").splitlines() == ["天气查询失败", "点开重试"], "weather error summary changed")

    noop = lambda *_args, **_kwargs: None
    dummy = QWidget()
    dummy.config = dict(app.DEFAULT_CONFIG)
    dummy.config["PetName"] = "糯米"
    dummy.weather_text = long_weather
    for name in (
        "study_summary",
        "open_today_board",
        "open_todos",
        "open_calendar",
        "open_weather",
        "open_mail",
        "open_core_toolbox",
        "open_claude_code",
        "open_ai",
        "ocr_screenshot",
        "open_file_search",
        "open_performance",
        "open_desktop_organizer",
        "open_word_popup",
        "open_formula_search",
        "open_translate",
        "open_clipboard",
        "open_action_lab",
        "open_diagnostics",
        "open_notebook",
        "open_battery",
        "toggle_bubble_enabled",
        "toggle_word_popup",
        "open_feature_switch",
        "open_settings",
        "open_help",
        "hide_to_tray",
        "restart_pet",
        "exit_pet",
    ):
        setattr(dummy, name, noop)
    menu = app.PetSmartMenu(dummy)
    require(menu.scroll is None, "full smart menu should fit without scroll on the default geometry")
    require(menu.height() <= bounds.height(), "smart menu should stay within the screen height")
    menu.close()
    dummy.close()

    bubble.close()
    print(
        {
            "screen_bounds": [bounds.left(), bounds.top(), bounds.width(), bounds.height()],
            "default_pos": [default_pos.x(), default_pos.y()],
            "bubble_tail": "merged_path_no_base_seam",
            "word_tail": "shoulder_anchor",
            "word_height": word_height,
            "weather_lines": len(weather_lines),
            "smart_menu_scroll": False,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
