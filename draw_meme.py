#!/usr/bin/env python3
"""GTA 6 x make.fun meme, Roblox style. Procedural PIL, deterministic."""

import math
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# --- palette (bright Roblox-ish) ---
SKY_TOP = (63, 169, 245)
SKY_BOT = (174, 233, 255)
SUN = (255, 217, 61)
SUN_EDGE = (255, 184, 0)
CLOUD = (255, 255, 255)
CLOUD_EDGE = (190, 220, 240)
INK = (26, 26, 46)
WHITE = (255, 255, 255)
PLATE = (88, 179, 104)
PLATE_DARK = (62, 140, 78)
STUD = (126, 212, 145)
STUD_RIM = (70, 150, 85)
ROAD = (99, 110, 114)
ROAD_EDGE = (70, 78, 82)
TRUNK = (176, 137, 104)
TRUNK_DARK = (146, 109, 79)
FROND = (46, 204, 113)
FROND_DARK = (39, 174, 96)
CAP_RED = (230, 57, 70)
CAP_DARK = (190, 35, 50)
CHEEK = (255, 150, 168)
BAG = (233, 196, 106)
BAG_DARK = (199, 160, 74)
DOLLAR = (42, 120, 70)
PANTS = (52, 73, 94)
SHOE = (26, 26, 46)
STAR_Y = (255, 200, 0)
STAR_EDGE = (200, 140, 0)


def font(size):
    return ImageFont.truetype(FONT_PATH, size)


def fit_font(draw, text, max_w, start=110):
    size = start
    while size > 10:
        f = font(size)
        box = draw.textbbox((0, 0), text, font=f, stroke_width=8)
        if box[2] - box[0] <= max_w:
            return f
        size -= 4
    return font(10)


def outlined_text(draw, cx, y, text, f, fill=WHITE, stroke=INK, sw=9):
    box = draw.textbbox((0, 0), text, font=f, stroke_width=sw)
    w = box[2] - box[0]
    draw.text((cx - w / 2 - box[0], y), text, font=f, fill=fill,
              stroke_width=sw, stroke_fill=stroke)
    return box[3] - box[1]


def rrect(draw, box, r, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def star(draw, cx, cy, r, fill=STAR_Y, outline=STAR_EDGE, width=4):
    pts = []
    for i in range(10):
        rad = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    draw.polygon(pts, fill=fill, outline=outline, width=width)


def blocky_cloud(draw, cx, cy, s=1.0):
    # cluster of rectangles = blocky Roblox cloud
    boxes = [(-70, -18, 70, 22), (-45, -38, 10, -10), (5, -30, 55, -6), (-30, 8, 40, 26)]
    for (x0, y0, x1, y1) in boxes:
        rrect(draw, (cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s), 10 * s,
              CLOUD, outline=CLOUD_EDGE, width=3)


def building(draw, x, base_y, w, h, color, edge):
    rrect(draw, (x, base_y - h, x + w, base_y), 6, color, outline=edge, width=5)
    # window grid
    cols = max(2, w // 34)
    rows = max(2, h // 40)
    for c in range(cols):
        for r in range(rows):
            wx = x + 10 + c * ((w - 20) / cols)
            wy = base_y - h + 12 + r * ((h - 24) / rows)
            lit = (c * 7 + r * 3) % 3 != 0
            draw.rectangle((wx, wy, wx + 16, wy + 20),
                           fill=(255, 243, 176) if lit else (45, 52, 54),
                           outline=edge, width=2)


def palm(draw, x, base_y, h=210, flip=1):
    # segmented blocky trunk leaning slightly
    seg = 6
    seg_h = h / seg
    lean = 26 * flip
    for i in range(seg):
        t = i / seg
        cx = x + lean * t * t
        wdt = 30 - 10 * t
        y0 = base_y - (i + 1) * seg_h
        y1 = base_y - i * seg_h
        rrect(draw, (cx - wdt / 2, y0, cx + wdt / 2, y1 + 2), 5,
              TRUNK if i % 2 == 0 else TRUNK_DARK, outline=INK, width=3)
    top_x = x + lean
    top_y = base_y - h
    # flat fronds as tapered polygons
    for ang, ln in [(-160, 105), (-115, 120), (-70, 125), (-25, 115), (15, 100), (55, 80)]:
        a = math.radians(ang)
        tip = (top_x + ln * math.cos(a), top_y + ln * math.sin(a) + 18)
        mid = (top_x + ln * 0.55 * math.cos(a), top_y + ln * 0.55 * math.sin(a) - 14)
        perp = a + math.pi / 2
        w0 = 13
        p1 = (top_x + w0 * math.cos(perp), top_y + w0 * math.sin(perp))
        p2 = (top_x - w0 * math.cos(perp), top_y - w0 * math.sin(perp))
        draw.polygon([p1, mid, tip, p2], fill=FROND, outline=FROND_DARK, width=3)
    # coconuts
    for dx, dy in [(-10, 8), (12, 10), (0, 18)]:
        draw.ellipse((top_x + dx - 9, top_y + dy - 9, top_x + dx + 9, top_y + dy + 9),
                     fill=(120, 85, 50), outline=INK, width=3)


def baseplate(draw, y0, y1):
    draw.rectangle((0, y0, W, y1), fill=PLATE)
    draw.rectangle((0, y0, W, y0 + 8), fill=PLATE_DARK)
    # studs with simple perspective: rows grow toward the viewer
    rows = 5
    for r in range(rows):
        t = r / (rows - 1)
        cy = y0 + 26 + t * (y1 - y0 - 44)
        rad = 9 + 9 * t
        step = 64 + 26 * t
        offset = (r % 2) * step / 2
        x = -step + offset
        while x < W + step:
            draw.ellipse((x - rad, cy - rad * 0.62, x + rad, cy + rad * 0.62),
                         fill=STUD, outline=STUD_RIM, width=3)
            draw.ellipse((x - rad * 0.55, cy - rad * 0.38, x + rad * 0.55, cy + rad * 0.1),
                         fill=(170, 232, 184))
            x += step


def road(draw, y0, y1):
    draw.rectangle((0, y0, W, y1), fill=ROAD)
    draw.rectangle((0, y0, W, y0 + 6), fill=ROAD_EDGE)
    draw.rectangle((0, y1 - 6, W, y1), fill=ROAD_EDGE)
    cy = (y0 + y1) / 2
    x = 20
    while x < W:
        rrect(draw, (x, cy - 7, x + 64, cy + 7), 6, WHITE)
        x += 118


def money_bag(draw, cx, cy, s=1.0):
    # tied sack
    draw.polygon([(cx - 20 * s, cy - 62 * s), (cx + 20 * s, cy - 62 * s),
                  (cx + 8 * s, cy - 34 * s), (cx - 8 * s, cy - 34 * s)],
                 fill=BAG_DARK, outline=INK, width=4)
    draw.ellipse((cx - 52 * s, cy - 40 * s, cx + 52 * s, cy + 62 * s),
                 fill=BAG, outline=INK, width=5)
    draw.rectangle((cx - 26 * s, cy - 44 * s, cx + 26 * s, cy - 30 * s),
                   fill=BAG_DARK, outline=INK, width=3)
    f = font(int(62 * s))
    box = draw.textbbox((0, 0), "$", font=f)
    draw.text((cx - (box[2] - box[0]) / 2 - box[0], cy - 26 * s), "$",
              font=f, fill=DOLLAR)


def mini_ghost(draw, cx, cy, s=1.0):
    # small ghost logo mark: dome head, wavy bottom
    wdt, hgt = 56 * s, 64 * s
    x0, y0, x1, y1 = cx - wdt / 2, cy - hgt / 2, cx + wdt / 2, cy + hgt / 2
    draw.pieslice((x0, y0, x1, y0 + wdt), 180, 360, fill=WHITE, outline=INK, width=4)
    draw.rectangle((x0, y0 + wdt / 2, x1, y1 - 8 * s), fill=WHITE)
    draw.line((x0, y0 + wdt / 2, x0, y1 - 8 * s), fill=INK, width=4)
    draw.line((x1, y0 + wdt / 2, x1, y1 - 8 * s), fill=INK, width=4)
    # wavy bottom
    wave = []
    n = 24
    for i in range(n + 1):
        t = i / n
        wave.append((x0 + t * wdt, y1 - 8 * s + 8 * s * abs(math.sin(t * math.pi * 2))))
    draw.line(wave, fill=INK, width=4)
    # face: two eyes + smile
    for dx in (-13 * s, 13 * s):
        draw.ellipse((cx + dx - 4 * s, cy - 8 * s, cx + dx + 4 * s, cy + 2 * s), fill=INK)
    draw.arc((cx - 11 * s, cy - 2 * s, cx + 11 * s, cy + 14 * s), 15, 165, fill=INK, width=4)


def billboard(draw, x, y, w, h):
    # poles
    for px in (x + 40, x + w - 62):
        draw.rectangle((px, y + h, px + 22, y + h + 110), fill=(120, 85, 50),
                       outline=INK, width=4)
    rrect(draw, (x, y, x + w, y + h), 10, WHITE, outline=INK, width=7)
    rrect(draw, (x + 10, y + 10, x + w - 10, y + h - 10), 8, None,
          outline=(230, 57, 70), width=4)
    mini_ghost(draw, x + 62, y + h / 2, s=1.35)
    f = fit_font(draw, "make.fun", w - 150, start=64)
    box = draw.textbbox((0, 0), "make.fun", font=f)
    th = box[3] - box[1]
    draw.text((x + 118, y + h / 2 - th / 2 - box[1]), "make.fun", font=f, fill=INK)


def avatar(draw, cx, feet_y):
    """Blocky Roblox-style ghost avatar. Returns hand position (raised right hand)."""
    # legs (blocky) + shoes
    leg_w, leg_h = 52, 96
    for dx in (-58, 6):
        rrect(draw, (cx + dx, feet_y - leg_h, cx + dx + leg_w, feet_y - 18), 6,
              PANTS, outline=INK, width=5)
        rrect(draw, (cx + dx - 4, feet_y - 22, cx + dx + leg_w + 4, feet_y), 6,
              SHOE, outline=INK, width=4)
    # torso: blocky white with wavy ghost bottom
    torso_top = feet_y - leg_h - 138
    torso_bot = feet_y - leg_h + 14
    tx0, tx1 = cx - 82, cx + 82
    rrect(draw, (tx0, torso_top, tx1, torso_bot - 16), 10, WHITE, outline=INK, width=6)
    wave = []
    n = 40
    for i in range(n + 1):
        t = i / n
        wave.append((tx0 + t * (tx1 - tx0),
                     torso_bot - 16 + 14 * abs(math.sin(t * math.pi * 3))))
    draw.polygon([(tx0, torso_bot - 18), (tx1, torso_bot - 18)] + wave[::-1], fill=WHITE)
    draw.line(wave, fill=INK, width=5)
    draw.line((tx0, torso_bot - 18, tx0, torso_bot - 16), fill=WHITE, width=8)
    draw.line((tx1, torso_bot - 18, tx1, torso_bot - 16), fill=WHITE, width=8)

    # left arm hanging down (blocky, slight angle)
    draw.polygon([(tx0 - 6, torso_top + 8), (tx0 + 34, torso_top + 14),
                  (tx0 + 16, torso_top + 128), (tx0 - 26, torso_top + 120)],
                 fill=WHITE, outline=INK, width=5)
    # right arm raised up-out holding the bag
    hand = (cx + 168, torso_top - 66)
    draw.polygon([(tx1 - 30, torso_top + 6), (tx1 + 8, torso_top + 16),
                  (hand[0] + 16, hand[1] + 26), (hand[0] - 22, hand[1] + 8)],
                 fill=WHITE, outline=INK, width=5)
    # hand nub
    draw.ellipse((hand[0] - 17, hand[1] - 17, hand[0] + 17, hand[1] + 17),
                 fill=WHITE, outline=INK, width=5)

    # head: blocky rounded square
    head_w, head_h = 168, 152
    hx0, hy0 = cx - head_w / 2, torso_top - head_h - 6
    hx1, hy1 = cx + head_w / 2, torso_top - 6
    rrect(draw, (hx0, hy0, hx1, hy1), 26, WHITE, outline=INK, width=7)

    # cap: dome + brim
    draw.pieslice((hx0 - 4, hy0 - 34, hx1 + 4, hy0 + 52), 180, 360,
                  fill=CAP_RED, outline=INK, width=5)
    rrect(draw, (hx0 - 26, hy0 + 2, hx1 + 26, hy0 + 22), 9, CAP_DARK,
          outline=INK, width=5)
    draw.ellipse((cx - 11, hy0 - 40, cx + 11, hy0 - 20), fill=CAP_DARK,
                 outline=INK, width=4)

    # sunglasses
    sy = hy0 + 62
    for gx0 in (cx - 66, cx + 12):
        rrect(draw, (gx0, sy, gx0 + 54, sy + 40), 10, INK)
        draw.line((gx0 + 10, sy + 30, gx0 + 26, sy + 10), fill=(120, 200, 255), width=6)
    draw.rectangle((cx - 12, sy + 12, cx + 12, sy + 22), fill=INK)
    draw.line((hx0 + 2, sy + 8, cx - 66, sy + 12), fill=INK, width=7)
    draw.line((cx + 66, sy + 12, hx1 - 2, sy + 8), fill=INK, width=7)

    # cheeks + smile
    for dx in (-56, 40):
        draw.ellipse((cx + dx, hy0 + 104, cx + dx + 30, hy0 + 122), fill=CHEEK)
    draw.arc((cx - 24, hy0 + 96, cx + 24, hy0 + 134), 15, 165, fill=INK, width=6)
    return hand


def main():
    img = Image.new("RGB", (W, H), SKY_TOP)
    draw = ImageDraw.Draw(img)

    # sky gradient
    for y in range(0, 660):
        t = y / 660
        c = tuple(int(SKY_TOP[i] + (SKY_BOT[i] - SKY_TOP[i]) * t) for i in range(3))
        draw.line((0, y, W, y), fill=c)

    # square-ish sun (top-left, behind text zone edge)
    rrect(draw, (36, 196, 150, 310), 22, SUN, outline=SUN_EDGE, width=7)
    rrect(draw, (56, 216, 130, 290), 16, (255, 231, 120))

    # blocky clouds
    blocky_cloud(draw, 300, 250, 1.0)
    blocky_cloud(draw, 560, 215, 0.8)
    blocky_cloud(draw, 880, 300, 0.9)
    blocky_cloud(draw, 150, 380, 0.7)

    # background buildings along the horizon
    horizon = 660
    building(draw, 8, horizon, 120, 210, (255, 107, 107), (200, 60, 60))
    building(draw, 140, horizon, 96, 150, (78, 205, 196), (40, 160, 150))
    building(draw, 770, horizon, 110, 190, (255, 217, 61), (210, 170, 20))
    building(draw, 892, horizon, 120, 240, (167, 139, 250), (120, 90, 220))

    # palms
    palm(draw, 270, horizon, h=230, flip=1)
    palm(draw, 730, horizon, h=205, flip=-1)

    # ground: studded baseplate + road
    baseplate(draw, horizon, 806)
    road(draw, 716, 790)

    # billboard (right side, above horizon line)
    billboard(draw, 636, 356, 348, 150)

    # main character standing on the road
    hand = avatar(draw, 400, 792)
    money_bag(draw, hand[0] + 6, hand[1] - 34, s=1.05)

    # wanted stars, top-right under the headline
    for i in range(5):
        star(draw, 782 + i * 54, 224, 26)

    # --- meme text ---
    f1 = fit_font(draw, "GTA 6 TOOK 13 YEARS", 980, start=104)
    outlined_text(draw, W / 2, 14, "GTA 6 TOOK 13 YEARS", f1)
    f2 = fit_font(draw, "TO DROP", 980, start=104)
    outlined_text(draw, W / 2, 122, "TO DROP", f2)

    f3 = fit_font(draw, "MY AI AGENT MADE MONEY", 980, start=96)
    outlined_text(draw, W / 2, 828, "MY AI AGENT MADE MONEY", f3)
    f4 = fit_font(draw, "IN 3 DAYS ON make.fun", 980, start=96)
    outlined_text(draw, W / 2, 924, "IN 3 DAYS ON make.fun", f4)

    img.save("meme.png", optimize=True)
    print("wrote meme.png")


if __name__ == "__main__":
    main()
