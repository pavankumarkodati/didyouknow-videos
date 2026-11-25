from PIL import Image, ImageDraw, ImageFont
import os as _os
FD = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "fonts") + "/"
_base = {}

def _glyph():
    if "g" in _base: return _base["g"]
    f = ImageFont.truetype(FD + "LuckiestGuy-Regular.ttf", 300)
    im = Image.new("RGBA", (420, 440), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((222, 232), "?", font=f, fill=(0, 0, 0, 90), stroke_width=12, stroke_fill=(0, 0, 0, 90), anchor="mm")  # shadow
    d.text((210, 220), "?", font=f, fill=(255, 212, 0), stroke_width=12, stroke_fill=(10, 8, 20), anchor="mm")
    # cheek shine
    d.ellipse([150, 82, 178, 96], fill=(255, 245, 170))
    _base["g"] = im
    return im

def quizzy(mouth="smile", blink=0.0, wink=False, eye=1.0, look=(0, 0)):
    """mouth: smile|grin|o|jaw|flat. blink 0..1 closes both eyes."""
    im = _glyph().copy()
    d = ImageDraw.Draw(im)
    K = (10, 8, 20)
    # eyes sit on the top of the bowl
    for i, (ex, ey) in enumerate([(178, 92), (250, 96)]):
        r = 34 * eye
        closed = blink > 0.5 or (wink and i == 1)
        if closed:
            d.arc([ex - r, ey - r * 0.6, ex + r, ey + r * 0.6], 10, 170, fill=K, width=8)
            continue
        h = r * (1 - blink)
        d.ellipse([ex - r, ey - h, ex + r, ey + h], fill="white", outline=K, width=7)
        pr = r * 0.45
        px, py = ex + look[0] * r * 0.35, ey + look[1] * r * 0.35
        d.ellipse([px - pr, py - pr * (1 - blink), px + pr, py + pr * (1 - blink)], fill=K)
        d.ellipse([px - pr * 0.35 + 5, py - pr * 0.6, px + pr * 0.25 + 5, py - pr * 0.05], fill="white")
    # mouth on the thick right part of the bowl
    mx, my = 228, 160
    if mouth == "smile":
        d.arc([mx - 30, my - 26, mx + 30, my + 18], 20, 160, fill=K, width=8)
    elif mouth == "grin":
        d.chord([mx - 32, my - 22, mx + 32, my + 26], 0, 180, fill=(120, 20, 40), outline=K, width=6)
    elif mouth == "o":
        d.ellipse([mx - 15, my - 12, mx + 15, my + 20], fill=(120, 20, 40), outline=K, width=6)
    elif mouth == "jaw":
        d.rounded_rectangle([mx - 20, my - 14, mx + 20, my + 52], radius=18, fill=(120, 20, 40), outline=K, width=6)
        d.ellipse([mx - 11, my + 26, mx + 11, my + 44], fill=(240, 100, 120))
    else:
        d.line([mx - 20, my, mx + 20, my], fill=K, width=8)
    return im

if __name__ == "__main__":
    row = Image.new("RGBA", (420 * 5, 440), (40, 120, 60, 255))
    for i, kw in enumerate([dict(), dict(wink=True, mouth="grin"), dict(mouth="o", eye=1.2), dict(mouth="jaw", eye=1.35), dict(mouth="grin", look=(1, -1))]):
        row.alpha_composite(quizzy(**kw), (i * 420, 0))
    row.save("/home/claude/v2/qtest.png")
