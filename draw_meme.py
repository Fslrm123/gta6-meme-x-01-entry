#!/usr/bin/env python3
"""GTA 6 x make.fun meme, Harvest Moon style.

Draws a cozy farm scene on a 256x256 pixel grid with a soft pastel palette,
then upscales x4 with nearest-neighbour to 1024x1024. Fully procedural:
no external assets, deterministic output.
"""

from PIL import Image, ImageDraw, ImageFont

GRID = 256          # low-res pixel grid
SCALE = 4           # upscale factor -> 1024x1024
OUT = "meme.png"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# --- soft pastel palette -------------------------------------------------
SKY_TOP   = (135, 206, 250)   # light sky blue
SKY_LOW   = (198, 232, 255)   # pale horizon blue
CLOUD     = (255, 255, 255)
CLOUD_SH  = (222, 238, 250)
HILL_FAR  = (168, 220, 150)   # distant rolling hill
HILL_NEAR = (126, 199, 110)   # near hill
FIELD_A   = (110, 190,  95)   # crop field light row
FIELD_B   = ( 88, 168,  80)   # crop field dark row
SPROUT    = ( 60, 140,  60)   # crop sprouts
SOIL      = (150, 108,  72)   # dirt path
SOIL_DK   = (120,  84,  54)
WOOD      = (170, 120,  75)   # fence / sign wood
WOOD_DK   = (130,  88,  50)
ROOF      = (200,  70,  60)   # barn red roof
WALL      = (245, 235, 210)   # barn cream wall
WHITE     = (255, 255, 255)
GHOST_SH  = (225, 232, 245)   # ghost soft shading
STRAW     = (240, 205, 105)   # straw hat
STRAW_DK  = (205, 168,  70)
CHEEK     = (255, 160, 175)   # rosy cheeks
INK       = ( 45,  40,  55)   # outlines / eyes
GOLD      = (250, 200,  60)   # coins / stars
GOLD_DK   = (205, 150,  30)
SACK      = (214, 176, 110)   # coin sack
SACK_DK   = (168, 132,  76)
COW_SPOT  = ( 90,  75,  70)
PINK      = (255, 180, 190)   # cow nose
TEXT_FILL = (255, 255, 255)
TEXT_EDGE = ( 40,  55,  45)   # dark green text outline


def px_rect(d, box, fill):
    d.rectangle(box, fill=fill)


def draw_cloud(d, x, y, s):
    """Fluffy cloud made of overlapping circles + soft shadow base."""
    d.ellipse([x, y + 3 * s, x + 16 * s, y + 8 * s], fill=CLOUD_SH)
    d.ellipse([x + 1 * s, y + 2 * s, x + 9 * s, y + 7 * s], fill=CLOUD)
    d.ellipse([x + 5 * s, y, x + 14 * s, y + 6 * s], fill=CLOUD)
    d.ellipse([x + 10 * s, y + 2 * s, x + 16 * s, y + 7 * s], fill=CLOUD)


def draw_background(d):
    # sky: gentle two-band gradient
    for y in range(0, 120):
        t = y / 119.0
        c = tuple(int(SKY_TOP[i] + (SKY_LOW[i] - SKY_TOP[i]) * t) for i in range(3))
        d.line([(0, y), (GRID - 1, y)], fill=c)
    # sun: soft warm disc top-left
    d.ellipse([14, 10, 46, 42], fill=(255, 236, 150))
    d.ellipse([19, 15, 41, 37], fill=(255, 246, 190))
    # clouds
    draw_cloud(d, 60, 14, 2)
    draw_cloud(d, 150, 8, 2)
    draw_cloud(d, 205, 30, 1)
    draw_cloud(d, 100, 34, 1)
    # rolling hills (layered ellipses)
    d.ellipse([-60, 78, 150, 160], fill=HILL_FAR)
    d.ellipse([90, 84, 330, 170], fill=HILL_FAR)
    d.ellipse([-80, 104, 170, 200], fill=HILL_NEAR)
    d.ellipse([120, 110, 360, 210], fill=HILL_NEAR)
    # crop field: alternating rows with sprouts, bottom half
    row_h = 9
    y = 150
    i = 0
    while y < 216:
        px_rect(d, [0, y, GRID - 1, y + row_h - 1], FIELD_A if i % 2 == 0 else FIELD_B)
        # sprouts along the row
        for x in range(6 + (i % 2) * 5, GRID - 4, 11):
            d.line([(x, y + row_h - 2), (x, y + 3)], fill=SPROUT)
            d.point((x - 1, y + 3), fill=SPROUT)
            d.point((x + 1, y + 3), fill=SPROUT)
        y += row_h
        i += 1
    # dirt path at the very bottom (under the bottom text band)
    px_rect(d, [0, 216, GRID - 1, GRID - 1], SOIL)
    for x in range(4, GRID - 4, 13):
        d.point((x, 226), fill=SOIL_DK)
        d.point((x + 6, 238), fill=SOIL_DK)
        d.point((x + 2, 249), fill=SOIL_DK)


def draw_fence(d, y):
    """Wooden farm fence running across the field."""
    # horizontal rails
    px_rect(d, [0, y + 3, GRID - 1, y + 5], WOOD)
    px_rect(d, [0, y + 9, GRID - 1, y + 11], WOOD)
    # posts
    for x in range(4, GRID - 4, 22):
        px_rect(d, [x, y, x + 4, y + 15], WOOD_DK)
        px_rect(d, [x, y, x + 4, y + 1], WOOD)


def draw_barn(d, x, y):
    """Small barn with red roof. (x, y) = top-left of the roof."""
    # walls
    px_rect(d, [x + 4, y + 16, x + 44, y + 44], WALL)
    # roof: stepped pixel gable
    for i in range(9):
        inset = i * 2
        px_rect(d, [x + inset, y + i * 2, x + 48 - inset, y + i * 2 + 1], ROOF)
    px_rect(d, [x + 16, y, x + 32, y + 1], ROOF)
    # door with cross brace
    px_rect(d, [x + 17, y + 26, x + 31, y + 44], WOOD_DK)
    d.line([(x + 17, y + 26), (x + 31, y + 44)], fill=WOOD)
    d.line([(x + 31, y + 26), (x + 17, y + 44)], fill=WOOD)
    # window
    px_rect(d, [x + 8, y + 22, x + 13, y + 27], (150, 200, 235))
    px_rect(d, [x + 35, y + 22, x + 40, y + 27], (150, 200, 235))


def draw_cow(d, x, y):
    """Tiny chibi cow. (x, y) = top-left of the body."""
    # body
    px_rect(d, [x, y + 4, x + 26, y + 16], WHITE)
    d.ellipse([x + 5, y + 6, x + 13, y + 12], fill=COW_SPOT)
    d.ellipse([x + 16, y + 10, x + 23, y + 15], fill=COW_SPOT)
    # head
    px_rect(d, [x + 24, y, x + 36, y + 12], WHITE)
    d.ellipse([x + 27, y + 1, x + 32, y + 5], fill=COW_SPOT)
    # ears + horns
    px_rect(d, [x + 22, y + 2, x + 25, y + 5], PINK)
    px_rect(d, [x + 35, y + 2, x + 38, y + 5], PINK)
    d.point((x + 26, y - 1), fill=(240, 230, 200))
    d.point((x + 34, y - 1), fill=(240, 230, 200))
    # muzzle
    px_rect(d, [x + 28, y + 8, x + 36, y + 12], PINK)
    d.point((x + 30, y + 10), fill=COW_SPOT)
    d.point((x + 34, y + 10), fill=COW_SPOT)
    # eye
    d.point((x + 29, y + 5), fill=INK)
    # legs
    for lx in (x + 2, x + 8, x + 18, x + 23):
        px_rect(d, [lx, y + 16, lx + 3, y + 21], WHITE)
        px_rect(d, [lx, y + 20, lx + 3, y + 21], COW_SPOT)
    # tail
    d.line([(x, y + 5), (x - 3, y + 13)], fill=COW_SPOT)


def draw_chicken(d, x, y):
    """Tiny chicken. (x, y) = top-left of the body."""
    d.ellipse([x, y + 3, x + 11, y + 11], fill=WHITE)
    d.ellipse([x + 7, y, x + 13, y + 6], fill=WHITE)          # head
    px_rect(d, [x + 9, y - 2, x + 11, y], (235, 80, 80))      # comb
    d.point((x + 13, y + 3), fill=GOLD)                        # beak
    d.point((x + 10, y + 3), fill=INK)                         # eye
    d.line([(x + 4, y + 11), (x + 4, y + 14)], fill=GOLD_DK)  # legs
    d.line([(x + 8, y + 11), (x + 8, y + 14)], fill=GOLD_DK)


def draw_ghost_farmer(d, cx, cy):
    """The make.fun ghost as a cute farmer with straw hat + coin sack.

    (cx, cy) = centre of the ghost body. Body ~44px wide, 46px tall.
    """
    x0, y0 = cx - 22, cy - 23
    x1, y1 = cx + 22, cy + 23
    # coin sack first (behind the arm, at ghost's left hand)
    sx, sy = x0 - 16, cy + 2
    d.ellipse([sx, sy, sx + 24, sy + 26], fill=SACK)
    px_rect(d, [sx + 8, sy - 5, sx + 16, sy + 2], SACK_DK)      # tied top
    d.ellipse([sx + 4, sy + 4, sx + 12, sy + 12], fill=(232, 200, 140))  # shine
    # gold coins spilling from the sack top
    for (gx, gy) in [(sx + 6, sy - 8), (sx + 12, sy - 10), (sx + 17, sy - 7)]:
        d.ellipse([gx, gy, gx + 5, gy + 5], fill=GOLD)
        d.point((gx + 2, gy + 2), fill=GOLD_DK)
    # $ on the sack
    font = ImageFont.truetype(FONT_PATH, 13)
    d.text((sx + 7, sy + 7), "$", font=font, fill=GOLD_DK)
    # ghost body: rounded top, wavy bottom hem
    d.pieslice([x0, y0, x1, y0 + 44], 180, 360, fill=WHITE)
    px_rect(d, [x0, y0 + 22, x1, y1 - 6], WHITE)
    for i in range(4):  # wavy hem bumps
        bx = x0 + i * 11
        d.pieslice([bx, y1 - 12, bx + 11, y1], 0, 180, fill=WHITE)
    # soft shading on the right side
    d.pieslice([x1 - 12, y0 + 2, x1 - 1, y0 + 40], 270, 360, fill=GHOST_SH)
    # outline
    d.arc([x0, y0, x1, y0 + 44], 180, 360, fill=INK)
    d.line([(x0, y0 + 22), (x0, y1 - 6)], fill=INK)
    d.line([(x1, y0 + 22), (x1, y1 - 6)], fill=INK)
    # straw hat: brim + crown, tilted on top of the head
    d.ellipse([cx - 26, y0 - 3, cx + 26, y0 + 6], fill=STRAW)
    d.ellipse([cx - 26, y0 - 3, cx + 26, y0 + 6], outline=STRAW_DK)
    d.pieslice([cx - 13, y0 - 13, cx + 13, y0 + 5], 180, 360, fill=STRAW)
    d.arc([cx - 13, y0 - 13, cx + 13, y0 + 5], 180, 360, fill=STRAW_DK)
    px_rect(d, [cx - 13, y0 - 2, cx + 13, y0 + 1], (200, 90, 80))  # hat band
    # face: happy closed eyes, smile, rosy cheeks
    d.arc([cx - 13, cy - 8, cx - 5, cy - 1], 200, 340, fill=INK)
    d.arc([cx + 5, cy - 8, cx + 13, cy - 1], 200, 340, fill=INK)
    d.arc([cx - 5, cy - 2, cx + 5, cy + 6], 20, 160, fill=INK)
    d.ellipse([cx - 17, cy - 1, cx - 10, cy + 4], fill=CHEEK)
    d.ellipse([cx + 10, cy - 1, cx + 17, cy + 4], fill=CHEEK)
    # little arm reaching to the sack
    d.line([(x0 + 2, cy + 8), (sx + 20, sy + 8)], fill=WHITE, width=4)
    d.line([(x0 + 2, cy + 8), (sx + 20, sy + 8)], fill=INK, width=1)
    d.ellipse([sx + 17, sy + 5, sx + 23, sy + 11], fill=WHITE, outline=INK)


def draw_star(d, cx, cy, r, fill=GOLD, edge=GOLD_DK):
    """Five-pointed star (GTA wanted star)."""
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill, outline=edge)


def draw_sign(d, x, y):
    """Wooden farm sign with mini ghost + 'make.fun'. (x, y) = board top-left."""
    # posts
    px_rect(d, [x + 6, y + 26, x + 10, y + 44], WOOD_DK)
    px_rect(d, [x + 62, y + 26, x + 66, y + 44], WOOD_DK)
    # board with plank lines
    px_rect(d, [x, y, x + 72, y + 28], (196, 150, 96))
    d.rectangle([x, y, x + 72, y + 28], outline=WOOD_DK)
    d.line([(x, y + 9), (x + 72, y + 9)], fill=WOOD_DK)
    d.line([(x, y + 19), (x + 72, y + 19)], fill=WOOD_DK)
    # mini ghost on the left of the board
    gx, gy = x + 5, y + 5
    d.pieslice([gx, gy, gx + 14, gy + 14], 180, 360, fill=WHITE)
    px_rect(d, [gx, gy + 7, gx + 14, gy + 16], WHITE)
    for i in range(2):
        d.pieslice([gx + i * 7, gy + 12, gx + i * 7 + 7, gy + 18], 0, 180, fill=WHITE)
    d.arc([gx, gy, gx + 14, gy + 14], 180, 360, fill=INK)
    d.point((gx + 4, gy + 8), fill=INK)
    d.point((gx + 10, gy + 8), fill=INK)
    d.arc([gx + 4, gy + 8, gx + 10, gy + 13], 20, 160, fill=INK)
    # text
    font = ImageFont.truetype(FONT_PATH, 10)
    d.text((x + 19, y + 9), "make.fun", font=font, fill=(70, 45, 25))


def pixel_text(img, text, cx, y, size, fill=TEXT_FILL, edge=TEXT_EDGE):
    """Render text as crisp pixel lettering via a thresholded mask.

    Returns the height consumed (in grid pixels).
    """
    font = ImageFont.truetype(FONT_PATH, size)
    mask = Image.new("L", (GRID, GRID), 0)
    md = ImageDraw.Draw(mask)
    tw = md.textlength(text, font=font)
    md.text((cx - tw / 2, y), text, font=font, fill=255)
    mask = mask.point(lambda p: 255 if p > 110 else 0)
    # outline: paste the mask shifted in 8 directions in the edge colour
    edge_img = Image.new("RGBA", (GRID, GRID), edge + (255,))
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)]:
        img.paste(edge_img, (dx, dy), mask)
    fill_img = Image.new("RGBA", (GRID, GRID), fill + (255,))
    img.paste(fill_img, (0, 0), mask)
    bbox = font.getbbox(text)
    return bbox[3] - bbox[1] + 2


def main():
    img = Image.new("RGB", (GRID, GRID), SKY_TOP)
    d = ImageDraw.Draw(img)

    draw_background(d)
    draw_barn(d, 10, 96)
    draw_fence(d, 138)
    draw_cow(d, 196, 128)
    draw_chicken(d, 168, 146)
    draw_chicken(d, 52, 150)
    draw_sign(d, 170, 62)
    draw_ghost_farmer(d, 128, 158)

    # five wanted stars, top-right corner (below the top text)
    for i in range(5):
        draw_star(d, 192 + i * 13, 54, 6)

    # meme text
    pixel_text(img, "GTA 6 TOOK 13 YEARS", GRID // 2, 4, 17)
    pixel_text(img, "TO DROP", GRID // 2, 24, 17)
    pixel_text(img, "MY AI AGENT MADE MONEY", GRID // 2, 218, 15)
    pixel_text(img, "IN 3 DAYS ON make.fun", GRID // 2, 236, 15)

    big = img.resize((GRID * SCALE, GRID * SCALE), Image.NEAREST)
    big.save(OUT, optimize=True)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
