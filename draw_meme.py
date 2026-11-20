#!/usr/bin/env python3
"""Render the gta6-meme-x-01 entry meme (1024x1024 PNG) with PIL.

Scene: a Vice City-style sunset in Leonida — gradient sky, low sun, skyline
and palm silhouettes, a convertible sports car on the coast road, and the
make.fun white ghost in the driver's seat wearing sunglasses and holding a
money bag. Five GTA wanted stars sit in the top-right corner, a roadside
billboard reads "make.fun", and the meme text jokes about GTA 6's 13-year
wait versus an AI agent earning money on make.fun in 3 days.

Everything is drawn procedurally: no external assets, no downloads,
fully deterministic.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = Path(__file__).with_name("meme.png")

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Palette
SKY_STOPS = [
    (0.00, (38, 16, 74)),    # deep violet at the top
    (0.35, (122, 44, 117)),  # magenta band
    (0.62, (235, 94, 93)),   # coral
    (0.82, (255, 154, 61)),  # orange
    (1.00, (255, 209, 102)), # warm yellow at the horizon
]
SUN = (255, 214, 110)
SUN_GLOW = (255, 170, 80)
SILHOUETTE = (30, 12, 48)     # skyline / palms
ROAD = (26, 18, 38)
ROAD_EDGE = (255, 209, 102)
CAR_BODY = (18, 16, 34)
CAR_TRIM = (255, 94, 120)     # neon pink trim
GHOST_WHITE = (255, 255, 255)
GHOST_SHADE = (214, 222, 240)
INK = (12, 10, 20)
GOLD = (255, 196, 0)
BAG_TAN = (222, 184, 110)
BAG_DARK = (150, 112, 52)
BILLBOARD_BG = (255, 250, 238)
BILLBOARD_INK = (38, 16, 74)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_color(t):
    """Interpolate the sunset gradient at t in [0, 1]."""
    for (t0, c0), (t1, c1) in zip(SKY_STOPS, SKY_STOPS[1:]):
        if t0 <= t <= t1:
            return lerp(c0, c1, (t - t0) / (t1 - t0))
    return SKY_STOPS[-1][1]


def font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def fit_font(draw, text, max_width, start_size, bold=True):
    """Largest font size (<= start_size) whose text fits max_width."""
    size = start_size
    while size > 10:
        f = font(size, bold)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 2
    return font(10, bold)


def draw_sky(d):
    horizon = 600
    for y in range(horizon):
        d.line([(0, y), (W, y)], fill=sky_color(y / horizon))
    # sea strip just under the horizon line
    for y in range(horizon, 660):
        t = (y - horizon) / 60
        d.line([(0, y), (W, y)], fill=lerp((255, 170, 90), (90, 40, 90), t))


def draw_sun(d):
    cx, cy, r = 400, 520, 150
    for rr, col in [(r + 60, (255, 140, 80)), (r + 34, (255, 170, 90)),
                    (r + 16, (255, 196, 100))]:
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN)
    # retro scan-line cuts across the lower half of the sun, clipped to the disc
    for i, yy in enumerate(range(cy + 34, cy + r - 6, 26)):
        half = math.sqrt(max(0, r * r - (yy - cy) ** 2))
        d.line([(cx - half, yy), (cx + half, yy)],
               fill=(255, 150, 70), width=5 + i * 2)


def draw_skyline(d):
    horizon = 660
    buildings = [
        (0, 120, 70), (64, 170, 52), (112, 96, 44), (152, 140, 60),
        (660, 150, 56), (712, 104, 46), (754, 180, 64), (814, 118, 50),
        (860, 156, 58), (914, 100, 48), (958, 138, 66),
    ]
    for x, h, w in buildings:
        d.rectangle([x, horizon - h, x + w, horizon], fill=SILHOUETTE)
        # a few lit windows
        for wy in range(horizon - h + 14, horizon - 12, 26):
            for wx in range(x + 8, x + w - 8, 18):
                if (wx * 7 + wy * 13) % 5 == 0:
                    d.rectangle([wx, wy, wx + 7, wy + 10], fill=(255, 214, 110))


def palm(d, x, base_y, height, lean, flip=1):
    """One palm-tree silhouette: curved trunk plus drooping fronds."""
    top_x = x + lean * flip
    top_y = base_y - height
    # trunk as stacked segments along a quadratic curve
    pts = []
    for i in range(21):
        t = i / 20
        px = (1 - t) ** 2 * x + 2 * (1 - t) * t * (x + lean * 0.3 * flip) + t ** 2 * top_x
        py = (1 - t) ** 2 * base_y + 2 * (1 - t) * t * (base_y - height * 0.55) + t ** 2 * top_y
        pts.append((px, py))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d.line([(x0, y0), (x1, y1)], fill=SILHOUETTE, width=16)
    # fronds
    for ang in (-160, -125, -95, -60, -25, 5):
        a = math.radians(ang if flip > 0 else 180 - ang)
        length = height * 0.52
        tip = (top_x + length * math.cos(a), top_y + length * math.sin(a) * 0.55 + length * 0.22)
        mid = (top_x + length * 0.55 * math.cos(a),
               top_y + length * 0.55 * math.sin(a) * 0.55 - length * 0.10)
        frond = []
        for i in range(13):
            t = i / 12
            px = (1 - t) ** 2 * top_x + 2 * (1 - t) * t * mid[0] + t ** 2 * tip[0]
            py = (1 - t) ** 2 * top_y + 2 * (1 - t) * t * mid[1] + t ** 2 * tip[1]
            frond.append((px, py))
        d.line(frond, fill=SILHOUETTE, width=9, joint="curve")
    # coconuts
    for dx, dy in [(-10, 8), (8, 12), (0, 18)]:
        d.ellipse([top_x + dx - 9, top_y + dy - 9, top_x + dx + 9, top_y + dy + 9],
                  fill=SILHOUETTE)


def draw_road(d):
    top = 660
    d.rectangle([0, top, W, H], fill=ROAD)
    # glowing horizon edge
    d.line([(0, top), (W, top)], fill=ROAD_EDGE, width=4)
    # centre dashes converging to a vanishing point
    vx, vy = 470, top
    for i in range(6):
        t0 = i / 6
        t1 = t0 + 0.055
        y0 = vy + (H - vy) * (t0 ** 1.6)
        y1 = vy + (H - vy) * (t1 ** 1.6)
        w0 = 3 + 26 * t0
        w1 = 3 + 26 * t1
        cx0 = vx + (512 - vx) * t0
        cx1 = vx + (512 - vx) * t1
        d.polygon([(cx0 - w0, y0), (cx0 + w0, y0), (cx1 + w1, y1), (cx1 - w1, y1)],
                  fill=(255, 214, 110))


def star_points(cx, cy, r):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    return pts


def draw_wanted_stars(d):
    # five GTA-style wanted stars, right side below the top text
    for i in range(5):
        cx = 1024 - 52 - i * 62
        d.polygon(star_points(cx, 252, 27), fill=GOLD, outline=INK, width=3)


def draw_billboard(d):
    # roadside billboard on the right, mid-ground
    x0, y0, x1, y1 = 700, 470, 1000, 610
    for px in (742, 952):
        d.rectangle([px, y1, px + 14, 700], fill=SILHOUETTE)
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=BILLBOARD_BG,
                        outline=INK, width=6)
    # mini ghost logo on the billboard
    gx, gy = 748, 505
    d.pieslice([gx - 26, gy - 26, gx + 26, gy + 26], 180, 360, fill=GHOST_WHITE,
               outline=INK, width=4)
    d.rectangle([gx - 26, gy, gx + 26, gy + 30], fill=GHOST_WHITE)
    for sx in (-26, -9, 9):
        d.pieslice([gx + sx, gy + 20, gx + sx + 17, gy + 38], 0, 180,
                   fill=GHOST_WHITE)
    d.line([(gx - 26, gy), (gx - 26, gy + 30)], fill=INK, width=4)
    d.line([(gx + 26, gy), (gx + 26, gy + 30)], fill=INK, width=4)
    for ex in (-11, 11):
        d.ellipse([gx + ex - 4, gy - 6, gx + ex + 4, gy + 4], fill=INK)
    d.arc([gx - 9, gy + 4, gx + 9, gy + 18], 15, 165, fill=INK, width=3)
    f = fit_font(d, "make.fun", 190, 54)
    d.text((792, 540), "make.fun", font=f, fill=BILLBOARD_INK, anchor="lm")


def draw_car(d):
    """Side-view convertible sports car, centred low in the frame."""
    dy = -55  # lift the car so the bottom meme text clears the wheels
    # body silhouette (low nose left, cabin hump, short deck right)
    body = [
        (120, 790), (150, 752), (300, 736), (420, 700), (520, 688),
        (640, 694), (760, 724), (880, 742), (916, 772), (910, 812),
        (840, 824), (700, 828), (420, 828), (220, 824), (132, 816),
    ]
    body = [(x, y + dy) for x, y in body]
    d.polygon(body, fill=CAR_BODY, outline=INK, width=5)
    # neon trim line along the flank
    d.line([(150, 786 + dy), (420, 768 + dy), (700, 772 + dy), (900, 790 + dy)],
           fill=CAR_TRIM, width=6)
    # open cockpit the ghost sits in
    d.polygon([(430, 706 + dy), (520, 692 + dy), (640, 698 + dy),
               (700, 722 + dy), (470, 728 + dy)],
              fill=(52, 36, 74), outline=INK, width=4)
    # headlight + taillight
    d.polygon([(128, 778 + dy), (176, 768 + dy), (180, 782 + dy), (134, 790 + dy)],
              fill=(255, 240, 170))
    d.polygon([(884, 766 + dy), (912, 776 + dy), (908, 790 + dy), (880, 782 + dy)],
              fill=(255, 80, 90))
    # wheels
    for wx in (268, 772):
        d.ellipse([wx - 58, 772 + dy, wx + 58, 888 + dy], fill=(10, 8, 16),
                  outline=INK, width=4)
        d.ellipse([wx - 28, 802 + dy, wx + 28, 858 + dy], fill=(200, 205, 220),
                  outline=INK, width=3)
        d.ellipse([wx - 9, 821 + dy, wx + 9, 839 + dy], fill=CAR_TRIM,
                  outline=INK, width=2)
    # ground shadow
    d.ellipse([110, 884 + dy, 930, 922 + dy], fill=(12, 8, 22))


def draw_ghost(d):
    """The make.fun ghost: white, sunglasses, money bag, in the driver's seat."""
    cx, top, w = 520, 435, 108
    bottom = top + 195
    # body: dome top, straight sides, wavy hem
    d.pieslice([cx - w, top, cx + w, top + 2 * w], 180, 360, fill=GHOST_WHITE)
    d.rectangle([cx - w, top + w, cx + w, bottom], fill=GHOST_WHITE)
    wave = []
    steps = 24
    for i in range(steps + 1):
        x = cx - w + (2 * w) * i / steps
        y = bottom + 14 * math.sin(i / steps * math.pi * 4)
        wave.append((x, y))
    d.polygon([(cx - w, bottom)] + wave + [(cx + w, bottom)], fill=GHOST_WHITE)
    # outline (sides + dome arc)
    d.arc([cx - w, top, cx + w, top + 2 * w], 180, 360, fill=INK, width=7)
    d.line([(cx - w, top + w), (cx - w, bottom)], fill=INK, width=7)
    d.line([(cx + w, top + w), (cx + w, bottom)], fill=INK, width=7)
    d.line(wave, fill=INK, width=6, joint="curve")
    # sunglasses
    sy = top + 100
    d.rounded_rectangle([cx - 82, sy - 22, cx - 11, sy + 22], radius=14,
                        fill=INK)
    d.rounded_rectangle([cx + 11, sy - 22, cx + 82, sy + 22], radius=14,
                        fill=INK)
    d.rectangle([cx - 13, sy - 7, cx + 13, sy + 3], fill=INK)
    d.line([(cx - 82, sy - 13), (cx - w + 4, sy - 24)], fill=INK, width=8)
    d.line([(cx + 82, sy - 13), (cx + w - 4, sy - 24)], fill=INK, width=8)
    # lens glints
    d.line([(cx - 70, sy + 10), (cx - 46, sy - 12)], fill=(255, 255, 255), width=5)
    d.line([(cx + 30, sy + 10), (cx + 54, sy - 12)], fill=(255, 255, 255), width=5)
    # smug smile + blush
    d.arc([cx - 28, sy + 34, cx + 28, sy + 76], 20, 160, fill=INK, width=6)
    for bx in (cx - 92, cx + 62):
        d.ellipse([bx, sy + 36, bx + 30, sy + 52], fill=(255, 170, 180))
    # money bag held up on the left, clear of the billboard
    bx, by = cx - 188, top + 152
    d.ellipse([bx - 58, by - 38, bx + 58, by + 80], fill=BAG_TAN, outline=INK, width=6)
    d.polygon([(bx - 24, by - 32), (bx + 24, by - 32), (bx + 11, by - 62),
               (bx - 11, by - 62)], fill=BAG_TAN, outline=INK, width=5)
    d.line([(bx - 24, by - 32), (bx + 24, by - 32)], fill=BAG_DARK, width=8)
    f = font(60)
    d.text((bx, by + 21), "$", font=f, fill=BAG_DARK, anchor="mm",
           stroke_width=2, stroke_fill=INK)
    # arm reaching to the bag, with a little round hand on it
    d.line([(cx - w + 8, top + 150), (bx + 46, by + 6)], fill=GHOST_WHITE, width=24)
    d.ellipse([bx + 30, by - 8, bx + 62, by + 24], fill=GHOST_WHITE, outline=INK, width=3)


def draw_windshield(d):
    """Small windshield in front of the ghost, drawn over the cockpit edge."""
    d.polygon([(628, 640), (700, 668), (664, 672), (606, 652)],
              fill=(170, 220, 255), outline=INK, width=3)


def draw_meme_text(d):
    top_lines = ["GTA 6 TOOK 13 YEARS", "TO DROP"]
    bottom_lines = ["MY AI AGENT MADE MONEY", "IN 3 DAYS ON make.fun"]
    max_w = 980
    y = 26
    for line in top_lines:
        f = fit_font(d, line, max_w, 76)
        d.text((W // 2, y), line, font=f, fill=(255, 255, 255), anchor="ma",
               stroke_width=8, stroke_fill=INK)
        y += f.size + 14
    y = H - 26
    for line in reversed(bottom_lines):
        f = fit_font(d, line, max_w, 76)
        d.text((W // 2, y), line, font=f, fill=(255, 255, 255), anchor="md",
               stroke_width=8, stroke_fill=INK)
        y -= f.size + 14


def main():
    img = Image.new("RGB", (W, H), (38, 16, 74))
    d = ImageDraw.Draw(img)
    draw_sky(d)
    draw_sun(d)
    draw_skyline(d)
    palm(d, 70, 700, 330, 70, flip=1)
    palm(d, 962, 700, 290, 64, flip=-1)
    palm(d, 176, 690, 220, 46, flip=1)
    draw_road(d)
    draw_billboard(d)
    draw_car(d)
    draw_ghost(d)
    draw_windshield(d)
    draw_wanted_stars(d)
    draw_meme_text(d)
    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
