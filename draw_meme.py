#!/usr/bin/env python3
"""64-bit pixel-art GTA 6 x make.fun meme.

Draws the scene on a 256x256 pixel grid with a limited saturated palette,
then upscales to 1024x1024 with nearest-neighbor for chunky crisp pixels.
Deterministic, PIL only, no external assets.
"""

import math

from PIL import Image, ImageDraw, ImageFont

GRID = 256
OUT = 1024
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# --- palette -------------------------------------------------------------
SKY_BANDS = [
    "#1e0538", "#33095c", "#4d0f7d", "#6d1596", "#9319a3", "#b81e96",
    "#d92b7f", "#f04a5e", "#ff6b3d", "#ff8f2e", "#ffb52e", "#ffd23f",
]
SUN_OUTER = "#ff9e2c"
SUN_INNER = "#ffd23f"
SILHOUETTE = "#160a2b"
ROAD = "#0d0518"
NEON_LINE = "#ff2e88"
WINDOW = "#ffd23f"
CAR_BODY = "#e91e8c"
CAR_DARK = "#a30f5f"
CAR_GLASS = "#7be7ff"
CAR_STRIPE = "#ffe66d"
TIRE = "#0a0a12"
HUBCAP = "#c9cede"
GHOST_WHITE = "#ffffff"
INK = "#0d0d14"
CHEEK = "#ff9ec6"
BAG = "#e8c15a"
BAG_DARK = "#b98a2e"
BAG_INK = "#6b4a12"
STAR = "#ffd23f"
BOARD = "#fff6e0"
BOARD_INK = "#3b1163"
TEXT_FILL = "#ffffff"

HORIZON = 178


def sky_color(y):
    """Band color of the sky at row y (for sun stripes)."""
    if y >= HORIZON:
        return ROAD
    idx = min(len(SKY_BANDS) - 1, y * len(SKY_BANDS) // HORIZON)
    return SKY_BANDS[idx]


def draw_sky(d):
    band_h = HORIZON / len(SKY_BANDS)
    for i, color in enumerate(SKY_BANDS):
        y0 = int(i * band_h)
        y1 = int((i + 1) * band_h) + 1
        d.rectangle([0, y0, GRID, y1], fill=color)


def draw_sun(d):
    cx, cy, r = 104, 116, 50
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN_OUTER)
    r2 = 38
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=SUN_INNER)
    # synthwave stripes across the lower sun, in sky colors
    for sy, sh in ((140, 3), (150, 4), (161, 5)):
        d.rectangle([cx - r, sy, cx + r, sy + sh], fill=sky_color(sy + sh // 2))


def draw_skyline(d):
    buildings = [
        (0, 22, 34), (20, 16, 52), (34, 24, 28), (56, 14, 44),
        (150, 18, 38), (166, 14, 26), (196, 20, 48), (214, 16, 32),
        (228, 28, 56),
    ]
    for bi, (x, w, h) in enumerate(buildings):
        d.rectangle([x, HORIZON - h, x + w, HORIZON], fill=SILHOUETTE)
        # lit windows: deterministic arithmetic pattern
        for row in range(2, h - 4, 7):
            for col in range(3, w - 3, 6):
                if (bi * 7 + row * 3 + col * 5) % 4 == 0:
                    wx, wy = x + col, HORIZON - h + row
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=WINDOW)


def draw_palm(d, base_x, top_x, top_y):
    # leaning trunk: stacked segments
    steps = 8
    prev = (base_x, HORIZON)
    for i in range(1, steps + 1):
        t = i / steps
        x = base_x + (top_x - base_x) * t
        y = HORIZON + (top_y - HORIZON) * t
        d.line([prev, (x, y)], fill=SILHOUETTE, width=4)
        prev = (x, y)
    # fronds: two-segment drooping lines
    for ang_deg, length in ((-170, 26), (-140, 30), (-110, 30), (-80, 28),
                            (-50, 30), (-20, 26), (10, 22)):
        ang = math.radians(ang_deg)
        mx = top_x + length * 0.6 * math.cos(ang)
        my = top_y + length * 0.6 * math.sin(ang)
        ex = top_x + length * math.cos(ang)
        ey = top_y + length * math.sin(ang) + 10
        d.line([(top_x, top_y), (mx, my)], fill=SILHOUETTE, width=3)
        d.line([(mx, my), (ex, ey)], fill=SILHOUETTE, width=3)
    # coconuts
    d.ellipse([top_x - 5, top_y + 1, top_x - 1, top_y + 5], fill=SILHOUETTE)
    d.ellipse([top_x + 1, top_y + 1, top_x + 5, top_y + 5], fill=SILHOUETTE)


def star_points(cx, cy, r_out, r_in):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        ang = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def draw_stars(d):
    for cx in (158, 178, 198, 218, 238):
        d.polygon(star_points(cx, 62, 9.5, 4.2), fill=INK)
        d.polygon(star_points(cx, 62, 8, 3.5), fill=STAR)


def fit_font(text, max_width, start_size=30):
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    size = start_size
    while size > 8:
        font = ImageFont.truetype(FONT_PATH, size)
        if probe.textlength(text, font=font) <= max_width:
            return font
        size -= 1
    return ImageFont.truetype(FONT_PATH, 8)


def draw_pixel_text(img, xy, text, font, fill, outline=None, outline_width=2,
                    anchor="mm"):
    """Crisp pixel text: render to a mask, threshold away anti-aliasing."""
    if outline is not None:
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).text(
            xy, text, font=font, fill=255, anchor=anchor,
            stroke_width=outline_width, stroke_fill=255)
        mask = mask.point(lambda p: 255 if p > 100 else 0)
        img.paste(Image.new("RGB", img.size, outline), (0, 0), mask)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=font, fill=255, anchor=anchor)
    mask = mask.point(lambda p: 255 if p > 100 else 0)
    img.paste(Image.new("RGB", img.size, fill), (0, 0), mask)


def draw_billboard(img, d):
    # posts
    d.rectangle([182, 130, 186, HORIZON], fill=SILHOUETTE)
    d.rectangle([236, 130, 240, HORIZON], fill=SILHOUETTE)
    # board with dark border
    d.rectangle([168, 94, 252, 132], fill=INK)
    d.rectangle([171, 97, 249, 129], fill=BOARD)
    # mini ghost
    d.ellipse([177, 101, 193, 117], fill=INK)
    d.rectangle([177, 109, 193, 124], fill=INK)
    d.ellipse([179, 103, 191, 115], fill=GHOST_WHITE)
    d.rectangle([179, 110, 191, 122], fill=GHOST_WHITE)
    d.rectangle([181, 108, 185, 111], fill=INK)   # sunglasses L
    d.rectangle([186, 108, 190, 111], fill=INK)   # sunglasses R
    d.arc([182, 112, 189, 118], start=15, end=165, fill=INK, width=1)
    # wordmark
    font = fit_font("make.fun", 52, start_size=16)
    draw_pixel_text(img, (222, 113), "make.fun", font, BOARD_INK)


def ghost_body_points(cx, top, bottom, half_w):
    """Ghost silhouette: straight sides, zigzag bottom edge."""
    pts = [(cx - half_w, top), (cx + half_w, top), (cx + half_w, bottom - 6)]
    steps = 6
    for i in range(steps, -1, -1):
        x = cx - half_w + (2 * half_w) * i / steps
        y = bottom if i % 2 == 0 else bottom - 6
        pts.append((x, y))
    return pts


def draw_ghost(d):
    cx = 104
    # black outline pass (slightly larger), then white pass
    d.ellipse([cx - 28, 90, cx + 28, 136], fill=INK)
    d.polygon(ghost_body_points(cx, 114, 164, 28), fill=INK)
    d.ellipse([cx - 26, 92, cx + 26, 134], fill=GHOST_WHITE)
    d.polygon(ghost_body_points(cx, 116, 162, 26), fill=GHOST_WHITE)
    # arm reaching left to grip the money bag's tie (outline then white)
    d.line([(cx - 22, 128), (62, 120)], fill=INK, width=8)
    d.line([(cx - 22, 128), (62, 120)], fill=GHOST_WHITE, width=5)
    d.ellipse([54, 112, 66, 124], fill=INK)
    d.ellipse([56, 114, 64, 122], fill=GHOST_WHITE)
    # sunglasses
    d.rectangle([cx - 21, 107, cx - 3, 118], fill=INK)
    d.rectangle([cx + 3, 107, cx + 21, 118], fill=INK)
    d.rectangle([cx - 3, 110, cx + 3, 113], fill=INK)
    d.line([(cx - 17, 116), (cx - 10, 109)], fill=GHOST_WHITE, width=2)
    d.line([(cx + 7, 116), (cx + 14, 109)], fill=GHOST_WHITE, width=2)
    # cheeks + smile
    d.ellipse([cx - 23, 120, cx - 13, 126], fill=CHEEK)
    d.ellipse([cx + 13, 120, cx + 23, 126], fill=CHEEK)
    d.arc([cx - 8, 119, cx + 8, 131], start=15, end=165, fill=INK, width=2)


def draw_money_bag(img, d):
    # tied top
    d.polygon([(52, 120), (64, 120), (60, 110), (56, 110)], fill=BAG_DARK)
    d.rectangle([51, 118, 65, 123], fill=BAG_DARK)
    # sack body with dark outline
    d.ellipse([42, 120, 74, 154], fill=BAG_DARK)
    d.ellipse([44, 122, 72, 152], fill=BAG)
    font = fit_font("$", 20, start_size=20)
    draw_pixel_text(img, (58, 137), "$", font, BAG_INK)


def draw_car(d):
    # convertible side profile, facing right; covers the ghost's lower body
    body = [
        (16, 160), (24, 150), (58, 148), (132, 148), (168, 152),
        (196, 160), (198, 172), (196, 180), (18, 180), (15, 170),
    ]
    d.polygon(body, fill=CAR_BODY)
    # darker lower band + neon stripe
    d.rectangle([17, 172, 197, 180], fill=CAR_DARK)
    d.line([(18, 166), (196, 166)], fill=CAR_STRIPE, width=3)
    # windshield
    d.polygon([(134, 150), (150, 132), (160, 150)], fill=CAR_GLASS)
    d.line([(134, 150), (150, 132)], fill=INK, width=2)
    # headlight + taillight
    d.rectangle([190, 161, 197, 166], fill=CAR_STRIPE)
    d.rectangle([16, 161, 22, 166], fill="#ff3355")
    # wheels
    for wx in (52, 160):
        d.ellipse([wx - 12, 168, wx + 12, 192], fill=TIRE)
        d.ellipse([wx - 6, 174, wx + 6, 186], fill=HUBCAP)
        d.ellipse([wx - 2, 178, wx + 2, 182], fill=CAR_BODY)


def main():
    img = Image.new("RGB", (GRID, GRID), ROAD)
    d = ImageDraw.Draw(img)

    draw_sky(d)
    draw_sun(d)
    draw_skyline(d)
    draw_palm(d, base_x=26, top_x=34, top_y=96)
    draw_billboard(img, d)

    # road + neon horizon line
    d.rectangle([0, HORIZON, GRID, GRID], fill=ROAD)
    d.rectangle([0, HORIZON, GRID, HORIZON + 2], fill=NEON_LINE)

    draw_money_bag(img, d)
    draw_ghost(d)
    draw_car(d)
    draw_stars(d)

    # meme text
    top1 = fit_font("GTA 6 TOOK 13 YEARS", 248)
    top2 = fit_font("TO DROP", 248)
    draw_pixel_text(img, (128, 17), "GTA 6 TOOK 13 YEARS", top1,
                    TEXT_FILL, outline=INK, outline_width=2)
    draw_pixel_text(img, (128, 41), "TO DROP", top2,
                    TEXT_FILL, outline=INK, outline_width=2)

    bot1 = fit_font("MY AI AGENT MADE MONEY", 248)
    bot2 = fit_font("IN 3 DAYS ON make.fun", 248)
    draw_pixel_text(img, (128, 214), "MY AI AGENT MADE MONEY", bot1,
                    TEXT_FILL, outline=INK, outline_width=2)
    draw_pixel_text(img, (128, 240), "IN 3 DAYS ON make.fun", bot2,
                    TEXT_FILL, outline=INK, outline_width=2)

    out = img.resize((OUT, OUT), Image.NEAREST)
    out.save("meme.png", optimize=True)
    print("wrote meme.png")


if __name__ == "__main__":
    main()
