import os
import sys
from pathlib import Path


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

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

    bubble.close()
    print(
        {
            "screen_bounds": [bounds.left(), bounds.top(), bounds.width(), bounds.height()],
            "default_pos": [default_pos.x(), default_pos.y()],
            "bubble_tail": "merged_path_no_base_seam",
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
