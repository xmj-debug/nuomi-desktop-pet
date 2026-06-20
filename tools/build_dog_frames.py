from __future__ import annotations

import math
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "dog-sprite-atlas-source.png"
OUT = ASSETS / "dog_frames"
PREVIEW = ASSETS / "nuomi-action-pack-preview.png"
SIZE = 512


def remove_green(cell: Image.Image) -> Image.Image:
    rgba = cell.convert("RGBA")
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            if g > 150 and r < 110 and b < 110:
                pixels[x, y] = (r, g, b, 0)
            elif g > 115 and g > r * 1.35 and g > b * 1.35:
                alpha = max(0, min(255, int((max(r, b) / max(g, 1)) * 245)))
                pixels[x, y] = (r, g, b, alpha)
    return rgba


def alpha_bbox(image: Image.Image):
    return image.getchannel("A").getbbox()


def keep_largest_component(image: Image.Image, threshold=20) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    pixels = alpha.load()
    width, height = rgba.size
    seen = bytearray(width * height)
    best = []
    for y in range(height):
        for x in range(width):
            pos = y * width + x
            if seen[pos] or pixels[x, y] <= threshold:
                continue
            seen[pos] = 1
            queue = deque([(x, y)])
            component = []
            while queue:
                cx, cy = queue.popleft()
                component.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if nx < 0 or ny < 0 or nx >= width or ny >= height:
                        continue
                    npos = ny * width + nx
                    if seen[npos] or pixels[nx, ny] <= threshold:
                        continue
                    seen[npos] = 1
                    queue.append((nx, ny))
            if len(component) > len(best):
                best = component
    if not best:
        return rgba
    keep = bytearray(width * height)
    for x, y in best:
        keep[y * width + x] = 1
    data = rgba.load()
    for y in range(height):
        for x in range(width):
            if not keep[y * width + x]:
                r, g, b, _a = data[x, y]
                data[x, y] = (r, g, b, 0)
    return rgba


def normalize(frame: Image.Image, max_side=438, y_bias=20) -> Image.Image:
    frame = frame.convert("RGBA")
    bbox = alpha_bbox(frame)
    if bbox:
        frame = frame.crop(bbox)
    ratio = min(max_side / max(frame.width, 1), max_side / max(frame.height, 1))
    new_size = (max(1, int(frame.width * ratio)), max(1, int(frame.height * ratio)))
    frame = frame.resize(new_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    x = (SIZE - frame.width) // 2
    y = max(0, SIZE - frame.height - y_bias)
    canvas.alpha_composite(frame, (x, y))
    return canvas


def soft_shadow(frame: Image.Image, strength=70) -> Image.Image:
    bbox = alpha_bbox(frame)
    if not bbox:
        return frame
    x1, y1, x2, y2 = bbox
    shadow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.ellipse(
        (x1 + 28, y2 - 32, x2 - 28, y2 + 8),
        fill=(22, 28, 38, strength),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    shadow.alpha_composite(frame)
    return shadow


def crop_atlas() -> dict[tuple[int, int], Image.Image]:
    atlas = Image.open(SOURCE).convert("RGB")
    cell_w = atlas.width // 4
    cell_h = atlas.height // 4
    cells = {}
    for row in range(4):
        for col in range(4):
            box = (col * cell_w, row * cell_h, (col + 1) * cell_w, (row + 1) * cell_h)
            cleaned = keep_largest_component(remove_green(atlas.crop(box)))
            cells[(row, col)] = soft_shadow(normalize(cleaned))
    return cells


def shifted(frame: Image.Image, dx=0, dy=0, angle=0, scale=1.0) -> Image.Image:
    src = frame
    if scale != 1.0:
        new_size = (max(1, int(SIZE * scale)), max(1, int(SIZE * scale)))
        src = src.resize(new_size, Image.Resampling.LANCZOS)
    if angle:
        src = src.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    x = (SIZE - src.width) // 2 + dx
    y = (SIZE - src.height) // 2 + dy
    canvas.alpha_composite(src, (x, y))
    return canvas


def make_study(frame: Image.Image) -> Image.Image:
    image = frame.copy()
    draw = ImageDraw.Draw(image)
    # Keep overlays simple and low so the original face stays recognizable.
    draw.rounded_rectangle((185, 182, 237, 220), radius=14, outline=(26, 48, 82, 230), width=5)
    draw.rounded_rectangle((275, 182, 327, 220), radius=14, outline=(26, 48, 82, 230), width=5)
    draw.line((237, 202, 275, 202), fill=(26, 48, 82, 230), width=5)
    book = Image.new("RGBA", image.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(book)
    bd.rounded_rectangle((166, 306, 346, 384), radius=20, fill=(79, 164, 255, 235))
    bd.line((256, 312, 256, 378), fill=(255, 255, 255, 210), width=4)
    bd.line((192, 338, 238, 332), fill=(255, 255, 255, 175), width=4)
    bd.line((275, 338, 321, 332), fill=(255, 255, 255, 175), width=4)
    image.alpha_composite(book)
    return image


def make_angry(frame: Image.Image) -> Image.Image:
    image = frame.copy()
    draw = ImageDraw.Draw(image)
    draw.line((193, 180, 232, 196), fill=(87, 43, 25, 230), width=8)
    draw.line((320, 180, 281, 196), fill=(87, 43, 25, 230), width=8)
    return shifted(image, dx=-8, dy=4, angle=-2)


def make_surprised(frame: Image.Image, dx=0, dy=0, angle=0) -> Image.Image:
    image = shifted(frame, dx=dx, dy=dy, angle=angle, scale=0.99)
    draw = ImageDraw.Draw(image)
    # Use full-head base frames; only add small alert marks so the head is never cropped.
    draw.line((360, 79, 383, 43), fill=(255, 255, 255, 235), width=8)
    draw.line((393, 105, 429, 86), fill=(255, 255, 255, 235), width=8)
    draw.line((137, 83, 115, 48), fill=(255, 255, 255, 220), width=7)
    return image


def make_blink(open_frame: Image.Image, closed_frame: Image.Image) -> list[Image.Image]:
    return [
        open_frame,
        shifted(closed_frame, dy=1),
        closed_frame,
        shifted(closed_frame, dy=1),
        open_frame,
    ]


def save_action(name: str, frames: list[Image.Image]):
    for index, frame in enumerate(frames):
        frame.save(OUT / f"{name}_{index}.png")


def make_preview(actions: list[str]):
    cols = 6
    thumb = 128
    rows = math.ceil(len(actions) / cols)
    preview = Image.new("RGBA", (cols * thumb, rows * thumb), (248, 250, 252, 255))
    for index, action in enumerate(actions):
        path = OUT / f"{action}_0.png"
        if not path.exists():
            continue
        frame = Image.open(path).resize((thumb, thumb), Image.Resampling.LANCZOS)
        preview.alpha_composite(frame, ((index % cols) * thumb, (index // cols) * thumb))
    preview.save(PREVIEW)


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()

    cells = crop_atlas()
    idle = [cells[(0, 0)], cells[(0, 1)], cells[(0, 2)], cells[(0, 3)], shifted(cells[(0, 0)], dy=2), shifted(cells[(0, 2)], dy=-2)]
    happy = [cells[(1, 0)], cells[(1, 1)], cells[(1, 2)], cells[(1, 3)], shifted(cells[(1, 2)], dy=-10), shifted(cells[(1, 1)], dy=-6)]
    side = [
        cells[(2, 0)],
        cells[(2, 1)],
        cells[(2, 2)],
        shifted(cells[(2, 2)], dx=-6, dy=5, scale=0.99),
        shifted(cells[(2, 1)], dy=-4),
        shifted(cells[(2, 0)], dy=2),
    ]
    sleep = [cells[(3, 0)], cells[(3, 1)], cells[(3, 2)], shifted(cells[(3, 0)], dy=2), shifted(cells[(3, 1)], dy=3), cells[(3, 2)]]
    alert = make_surprised(cells[(0, 0)])

    save_action("idle", idle)
    save_action("sit", idle[:4])
    save_action("blink", make_blink(cells[(0, 0)], cells[(0, 1)]))
    save_action("look_center", [cells[(0, 0)], shifted(cells[(0, 0)], dy=1), cells[(0, 2)]])
    save_action("look_left", [shifted(cells[(0, 2)], dx=-9, angle=-3), shifted(cells[(0, 0)], dx=-6, angle=-2), shifted(cells[(0, 0)], dx=-4, angle=-1)])
    save_action("look_right", [shifted(cells[(0, 2)], dx=9, angle=3), shifted(cells[(0, 0)], dx=6, angle=2), shifted(cells[(0, 0)], dx=4, angle=1)])
    save_action("happy", happy)
    save_action(
        "surprised",
        [
            alert,
            make_surprised(cells[(0, 2)], dy=-8, angle=-3),
            make_surprised(cells[(0, 0)], dx=-5, angle=-2),
            make_surprised(cells[(0, 0)], dx=5, angle=2),
            alert,
        ],
    )
    save_action("angry", [make_angry(cells[(0, 0)]), make_angry(cells[(3, 3)]), make_angry(cells[(0, 2)]), make_angry(cells[(3, 3)]), make_angry(cells[(0, 0)])])
    save_action("sleep", sleep)
    save_action("study", [make_study(frame) for frame in idle[:6]])
    save_action("sniff", side)
    save_action("sniff_right", [ImageOps.mirror(frame) for frame in side])
    save_action("stretch", [side[2], shifted(side[2], dx=-8, dy=6), cells[(3, 2)], shifted(cells[(3, 2)], dy=4), side[3], side[0]])
    save_action("walk_left", [side[0], side[1], side[2], side[1], side[0], side[4], side[3], side[5]])
    save_action("walk_right", [ImageOps.mirror(frame) for frame in [side[0], side[1], side[2], side[1], side[0], side[4], side[3], side[5]]])

    actions = [
        "idle",
        "blink",
        "look_left",
        "look_right",
        "happy",
        "surprised",
        "angry",
        "sleep",
        "study",
        "sniff",
        "sniff_right",
        "stretch",
        "walk_left",
        "walk_right",
    ]
    make_preview(actions)
    (OUT / "README.md").write_text(
        "Nuomi atlas-derived action pack\n\n"
        "Generated from assets/dog-sprite-atlas-source.png to preserve the fluffy red-clothes Nuomi style.\n"
        "The runtime loads every PNG named action_0.png, action_1.png, ...\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
