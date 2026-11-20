#!/usr/bin/env python3
"""GTA 6 meme in the trending 'fictional casting announcement' format.

Fake Hollywood casting-news graphic: the make.fun ghost has officially
been cast as everything. Deterministic PIL drawing, 1024x1024.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"

WHITE = (255, 255, 255)
BLACK = (15, 12, 30)
GOLD = (255, 200, 40)
GOLD_D = (214, 160, 20)
RED = (200, 30, 45)
CREAM = (255, 246, 220)


def F(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# --------------------------------------------------------------- background
img = Image.new("RGB", (W, H))
px = img.load()
# Vice City sunset: deep purple -> magenta -> pink -> orange
stops = [(0.0, (38, 16, 74)), (0.35, (122, 30, 110)), (0.62, (230, 70, 130)),
         (0.82, (255, 120, 90)), (1.0, (255, 170, 80))]
for y in range(H):
    t = y / H
    for i in range(len(stops) - 1):
        if stops[i][0] <= t <= stops[i + 1][0]:
            tt = (t - stops[i][0]) / (stops[i + 1][0] - stops[i][0])
            col = lerp(stops[i][1], stops[i + 1][1], tt)
            break
    for x in range(W):
        px[x, y] = col

d = ImageDraw.Draw(img, "RGBA")

# retro sun disc with scanline gaps, upper right area behind text panel
sun_cx, sun_cy, sun_r = 760, 330, 210
for yy in range(sun_cy - sun_r, sun_cy + sun_r):
    dy = yy - sun_cy
    half = int(math.sqrt(max(0, sun_r * sun_r - dy * dy)))
    if half <= 0:
        continue
    if yy > sun_cy and (yy // 14) % 2 == 0:
        continue  # scanline gaps on lower half
    t = (yy - (sun_cy - sun_r)) / (2 * sun_r)
    d.line([(sun_cx - half, yy), (sun_cx + half, yy)],
           fill=lerp((255, 220, 110), (255, 90, 120), t) + (255,))

# palm silhouettes along the bottom edge
def palm(x, base_y, hgt, flip=1):
    top_x = x + 26 * flip
    top_y = base_y - hgt
    d.line([(x, base_y), (top_x, top_y)], fill=(20, 10, 40, 255), width=9)
    for ang in (-150, -110, -70, -30, 10):
        a = math.radians(ang if flip > 0 else 180 - ang)
        ex = top_x + int(70 * math.cos(a))
        ey = top_y + int(46 * math.sin(a)) + 26
        mx = top_x + int(38 * math.cos(a))
        my = top_y + int(20 * math.sin(a))
        d.line([(top_x, top_y), (mx, my), (ex, ey)], fill=(20, 10, 40, 255), width=6)


palm(40, 1024, 210, 1)
palm(990, 1024, 240, -1)
palm(920, 1024, 150, -1)

# ------------------------------------------------------------------- banner
d.rectangle([0, 0, W, 118], fill=RED)
d.rectangle([0, 118, W, 126], fill=GOLD)
banner_font = F(SANS_B, 62)
bt = "CASTING NEWS"
bw = d.textlength(bt, font=banner_font)
d.text((222 + (806 - 222 - bw) / 2, 28), bt, font=banner_font, fill=WHITE)
# EXCLUSIVE tag, left
tag_font = F(SANS_B, 26)
d.rectangle([28, 38, 208, 82], fill=GOLD)
d.text((44, 46), "EXCLUSIVE", font=tag_font, fill=BLACK)

# five gold wanted stars, top right
def star(cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill, outline=(120, 80, 0, 255))


for i in range(5):
    star(838 + i * 38, 59, 17, GOLD)

# ------------------------------------------------------------- ghost portrait
PX0, PY0, PX1, PY1 = 48, 168, 448, 620
# gold frame + inner studio backdrop
d.rectangle([PX0 - 8, PY0 - 8, PX1 + 8, PY1 + 8], fill=GOLD_D)
d.rectangle([PX0, PY0, PX1, PY1], fill=(30, 20, 70))
# backdrop glow stripes
for i in range(6):
    yy = PY0 + 30 + i * 68
    d.line([(PX0 + 14, yy), (PX1 - 14, yy)], fill=(70, 45, 130, 255), width=3)
# spotlight ellipse behind ghost
d.ellipse([PX0 + 55, PY0 + 40, PX1 - 55, PY1 - 40], fill=(255, 240, 200, 70))

# ghost body: dome top, wavy bottom edge
gx0, gy0, gx1 = PX0 + 78, PY0 + 78, PX1 - 78
body_h = 330
pts = []
# left side up
pts.append((gx0, gy0 + body_h - 46))
pts.append((gx0, gy0 + 120))
# dome arc
cx = (gx0 + gx1) // 2
for i in range(21):
    a = math.pi - i * math.pi / 20
    pts.append((cx + (gx1 - gx0) / 2 * math.cos(a), gy0 + 120 - 118 * math.sin(a)))
pts.append((gx1, gy0 + body_h - 46))
# wavy bottom, right to left
steps = 48
for i in range(steps + 1):
    t = i / steps
    x = gx1 - t * (gx1 - gx0)
    y = gy0 + body_h - 46 + 26 * abs(math.sin(t * math.pi * 4))
    pts.append((x, y))
d.polygon(pts, fill=WHITE, outline=(200, 200, 215, 255))

# sunglasses
eye_y = gy0 + 150
lens_w, lens_h = 76, 56
for lx in (cx - 88, cx + 12):
    d.rounded_rectangle([lx, eye_y, lx + lens_w, eye_y + lens_h], radius=16,
                        fill=(18, 18, 28, 255))
    d.line([(lx + 10, eye_y + lens_h - 8), (lx + 34, eye_y + 10)],
           fill=(120, 180, 255, 255), width=5)
d.line([(cx - 12, eye_y + 16), (cx + 12, eye_y + 16)], fill=(18, 18, 28, 255), width=8)
d.line([(cx - 88, eye_y + 14), (gx0 + 6, eye_y + 4)], fill=(18, 18, 28, 255), width=7)
d.line([(cx + 88, eye_y + 14), (gx1 - 6, eye_y + 4)], fill=(18, 18, 28, 255), width=7)

# smile + cheeks
d.arc([cx - 34, eye_y + 62, cx + 34, eye_y + 104], 15, 165, fill=BLACK, width=7)
d.ellipse([cx - 108, eye_y + 72, cx - 78, eye_y + 92], fill=(255, 170, 190, 255))
d.ellipse([cx + 78, eye_y + 72, cx + 108, eye_y + 92], fill=(255, 170, 190, 255))
# little arms waving
d.line([(gx0 + 4, gy0 + 240), (gx0 - 34, gy0 + 196)], fill=WHITE, width=20)
d.line([(gx1 - 4, gy0 + 240), (gx1 + 34, gy0 + 196)], fill=WHITE, width=20)

# nameplate under portrait
NPY = PY1 + 18
d.rectangle([PX0 - 8, NPY, PX1 + 8, NPY + 58], fill=GOLD)
np_font = F(SANS_B, 30)
np_text = "THE MAKE.FUN GHOST"
npw = d.textlength(np_text, font=np_font)
d.text(((PX0 + PX1 - npw) / 2, NPY + 10), np_text, font=np_font, fill=BLACK)
sub_font = F(SANS_B, 20)
sub = "★ make.fun's #1 star ★"
sw = d.textlength(sub, font=sub_font)
d.text(((PX0 + PX1 - sw) / 2, NPY + 66), sub, font=sub_font, fill=WHITE)

# ------------------------------------------------------- announcement + roles
TX0 = 500
# dark panel behind the right-hand text for readability
d.rectangle([TX0 - 22, 168, 992, 772], fill=(16, 10, 44, 205))
d.rectangle([TX0 - 22, 168, 992, 772], outline=GOLD, width=3)

def wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


ann_font = F(SERIF_B, 47)
ann = "The make.fun ghost has officially been cast as…"
y = 196
for ln in wrap(ann, ann_font, 452):
    d.text((TX0, y), ln, font=ann_font, fill=CREAM)
    y += 56

roles = [
    "the GTA 6 protagonist",
    "the CEO of make.fun",
    "the AI agent that made money in 3 days",
]
role_font = F(SANS_B, 37)
y += 18
for role in roles:
    star(TX0 + 20, y + 22, 17, GOLD)
    lines = wrap(role, role_font, 408)
    for ln in lines:
        d.text((TX0 + 52, y), ln, font=role_font, fill=WHITE)
        y += 46
    y += 16

# ------------------------------------------------------------- punchline strip
d.rectangle([0, 868, W, H], fill=(14, 10, 38, 255))
d.rectangle([0, 868, W, 876], fill=GOLD)
p1_font = F(SANS_B, 50)
p1 = "Meanwhile, GTA 6 took"
p1w = d.textlength(p1, font=p1_font)
d.text(((W - p1w) / 2, 888), p1, font=p1_font, fill=WHITE)
p2_font = F(SANS_B, 60)
p2a, p2b = "13 YEARS", " to drop."
w2a = d.textlength(p2a, font=p2_font)
w2b = d.textlength(p2b, font=p2_font)
x2 = (W - w2a - w2b) / 2
d.text((x2, 948), p2a, font=p2_font, fill=GOLD)
d.text((x2 + w2a, 948), p2b, font=p2_font, fill=WHITE)

img.save(os.path.join(BASE, "meme.png"), optimize=True)
print("wrote meme.png")
