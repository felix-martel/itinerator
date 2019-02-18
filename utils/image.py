import math
from PIL import Image, ImageDraw, ImageFont

DEFAULT_COLOR = (56, 201, 255, 100)
DEFAULT_LINE_WIDTH = 12

def crop(im, size=None):
    if size is None:
        return im
    else:
        w, h = size
        width, height = im.size

        dh = math.floor((height - h) / 2)
        dw = math.floor((width - w) / 2)

        im.crop((dw, dh, width - dw, height - dh)),
        return im

def add_border(im, border=None, color="white"):
    if border is None:
        return im
    if isinstance(border, tuple) and len(border) == 2:
        bw, bh = border
    elif isinstance(border, int):
        bw = border
        bh = border
    else:
        raise TypeError("Invalid type for argument 'border'. Must be int or tuple(int, int)")
    w, h = im.size
    image = Image.new("RGB", (w + 2*bw, h + 2*bh), color)
    image.paste(im, (bw, bh))
    return image

def draw_line(im, line, color=DEFAULT_COLOR, lwidth=DEFAULT_LINE_WIDTH):
    draw = ImageDraw.Draw(im, "RGBA")
    draw.line(line, color, lwidth)
    return im

def draw_points(im, points, color=DEFAULT_COLOR, font_size=15, step=5):
    font = ImageFont.truetype("arial.ttf", font_size)
    draw = ImageDraw.Draw(im, "RGBA")

    for i, tick in enumerate(points):
        x, y = tick
        w, h = font.getsize(str(i * step))
        padding = 4
        x_center, y_center = (x + 0.5 * w, y + 0.5 * h)
        d = max(w, h) / 2 + padding
        bbox = [(x_center - d, y_center - d), (x_center + d, y_center + d)]
        draw.ellipse(bbox, fill=color)
        draw.text(tick, str(i * step), fill="black", font=font)
    return im

def draw(im, line=[], points=[], color=DEFAULT_COLOR, font_size=15, step=5, lwidth=DEFAULT_LINE_WIDTH):
    im = draw_line(im, line, color=color, lwidth=lwidth)
    im = draw_points(im, points, color=color, font_size=font_size, step=step)
    return im

def merge(main, secondary, corner):
    w, h = main.size
    lw, lh = secondary.size

    pos = {
        "topleft": (0, 0),
        "topright": (w - lw, 0),
        "bottomright": (w - lw, h - lh),
        "bottomleft": (0 ,h - lh),
    }

    main.paste(secondary, pos[corner])
    return main
