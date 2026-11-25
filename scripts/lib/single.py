import math, random, subprocess, sys, os, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FACTS = []

W, H, FPS = 1080, 1920, 30
DUR = 13.0
import os as _os
FD = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "fonts") + "/"
EMOJI = FD + "NotoColorEmoji.ttf"
NAVY = (8, 5, 32)
YEL = (250, 222, 50)
BLK = (12, 10, 20)
WHITE = (255, 255, 255)
HANDLE = "SOCMED311"

def F(name, size):
    return ImageFont.truetype(FD + name, size)

def baloo(size, weight="Bold"):
    f = ImageFont.truetype(FD + "Baloo2.ttf", size)
    try: f.set_variation_by_name(weight)
    except Exception: pass
    return f

# ---------- easing ----------
def clamp(x): return max(0.0, min(1.0, x))
def prog(t, a, b): return clamp((t - a) / (b - a))
def ease_out(x): return 1 - (1 - x) ** 3
def ease_in_out(x): return 3 * x * x - 2 * x * x * x
def back(x, s=1.8):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1

# ---------- helpers ----------
def emoji_img(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox())
    r = size / max(im.size)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)

def planet_img(size):
    s = size * 2
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    c = s / 2; r = s * 0.42
    d = np.sqrt((xx - c) ** 2 + (yy - c) ** 2)
    lx, ly = (xx - c * 0.75) / r, (yy - c * 0.7) / r
    shade = np.clip(1.15 - np.sqrt(lx ** 2 + ly ** 2) * 0.75, 0.25, 1.1)
    band = 0.88 + 0.12 * np.sin((yy / s) * 26 + np.sin(xx / s * 6) * 1.5)
    base = np.array([240, 170, 80], np.float32)
    rgb = np.clip(base[None, None, :] * (shade * band)[..., None], 0, 255)
    a = np.clip((r - d) * 1.5, 0, 1) * 255
    arr = np.dstack([rgb, a]).astype(np.uint8)
    p = Image.fromarray(arr, "RGBA")
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    g = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([c - r * 1.12, c - r * 1.12, c + r * 1.12, c + r * 1.12], fill=(255, 190, 90, 110))
    out.alpha_composite(g.filter(ImageFilter.GaussianBlur(s * 0.04)))
    out.alpha_composite(p)
    return out.resize((size, size), Image.LANCZOS)

def text_layer(txt, font, fill, stroke=0, sfill=BLK, pad=40):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    im = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - l, pad - t), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return im

def place(canvas, im, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.003 or scale <= 0.01: return
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if abs(scale - 1) > 0.002:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 0.999:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy(); im.putalpha(a)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# ---------- static art ----------
def title_art():
    f = F("LuckiestGuy-Regular.ttf", 250)
    fq = F("LuckiestGuy-Regular.ttf", 560)
    im = Image.new("RGBA", (1100, 1000), (0, 0, 0, 0))
    lines = [("DID", 70, 40), ("YOU", 150, 300), ("KNOW", 60, 560)]
    for dx, dy, col, sw in [(16, 16, YEL, 16), (0, 0, WHITE, 16)]:
        d = ImageDraw.Draw(im)
        for txt, x, y in lines:
            d.text((x + dx, y + dy), txt, font=f, fill=col, stroke_width=sw, stroke_fill=BLK)
        d.text((740 + dx, 60 + dy), "?", font=fq, fill=col, stroke_width=sw + 2, stroke_fill=BLK)
    # swoosh underline
    d = ImageDraw.Draw(im)
    for dx, col in [(14, YEL), (0, WHITE)]:
        d.line([(120 + dx, 880 + dx), (420 + dx, 860 + dx), (760 + dx, 800 + dx)], fill=BLK, width=58, joint="curve")
        d.line([(120 + dx, 880 + dx), (420 + dx, 860 + dx), (760 + dx, 800 + dx)], fill=col, width=34, joint="curve")
    im = im.crop(im.getbbox())
    im = im.rotate(9, resample=Image.BICUBIC, expand=True)
    r = 760 / im.width
    return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)

def panel_art(w=860, h=560):
    pad = 40
    S = Image.new("RGBA", (w + pad * 2, h + 120 + pad * 2), (0, 0, 0, 0))
    def shape(draw, ox, oy, **kw):
        draw.rounded_rectangle([pad + ox, pad + oy, pad + w + ox, pad + h + oy], radius=70, **kw)
    # outline echo (offset)
    d = ImageDraw.Draw(S)
    shape(d, 22, 18, outline=BLK, width=9)
    tail = [(pad + w * 0.40 + 22, pad + h - 5 + 18), (pad + w * 0.47 + 22, pad + h + 90 + 18), (pad + w * 0.58 + 22, pad + h - 5 + 18)]
    d.line(tail, fill=BLK, width=9, joint="curve")
    # fill + grid via mask
    mask = Image.new("L", S.size, 0)
    md = ImageDraw.Draw(mask)
    shape(md, 0, 0, fill=255)
    tail0 = [(pad + w * 0.40, pad + h - 30), (pad + w * 0.47, pad + h + 90), (pad + w * 0.60, pad + h - 30)]
    md.polygon(tail0, fill=255)
    fill = Image.new("RGBA", S.size, YEL + (255,))
    gd = ImageDraw.Draw(fill)
    for k in range(-S.height, S.width + S.height, 95):
        gd.line([(k, 0), (k + S.height, S.height)], fill=(214, 186, 30), width=4)
        gd.line([(k, 0), (k - S.height, S.height)], fill=(214, 186, 30), width=4)
    S.paste(fill, (0, 0), mask)
    # outline of main shape
    edge = mask.filter(ImageFilter.MaxFilter(15))
    ring = Image.new("RGBA", S.size, BLK + (255,))
    ringmask = Image.fromarray(np.clip(np.array(edge, np.int16) - np.array(mask, np.int16), 0, 255).astype(np.uint8))
    S.paste(ring, (0, 0), ringmask)
    return S

def card_art(w, h):
    pad = 30
    im = Image.new("RGBA", (w + pad * 2 + 24, h + pad * 2 + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad + 22, pad + 22, pad + w + 22, pad + h + 22], radius=48, fill=YEL, outline=BLK, width=8)
    d.rounded_rectangle([pad, pad, pad + w, pad + h], radius=48, fill=(255, 252, 240), outline=BLK, width=8)
    return im

def pill(txt, font, bg, fg, padx=50, pady=18, sw=0, border=7):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=font, stroke_width=sw)
    w, h = r - l + padx * 2, b - t + pady * 2
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([10, 10, 10 + w, 10 + h], radius=h // 2, fill=bg, outline=BLK, width=border)
    dd.text((10 + padx - l, 10 + pady - t), txt, font=font, fill=fg, stroke_width=sw, stroke_fill=BLK)
    return im

def handle_badge(scale=1.0):
    f = F("Bangers-Regular.ttf", int(84 * scale))
    p = pill(HANDLE, f, YEL, BLK, padx=int(80 * scale), pady=int(10 * scale), border=int(6 * scale))
    circ = int(190 * scale)
    c = Image.new("RGBA", (circ, circ), (0, 0, 0, 0))
    ImageDraw.Draw(c).ellipse([0, 0, circ - 1, circ - 1], fill=(240, 238, 228), outline=BLK, width=int(6 * scale))
    e = emoji_img("💡", int(circ * 0.62))
    c.alpha_composite(e, ((circ - e.width) // 2, (circ - e.height) // 2))
    im = Image.new("RGBA", (max(p.width, circ), circ + p.height - int(18 * scale)), (0, 0, 0, 0))
    im.alpha_composite(c, ((im.width - circ) // 2, 0))
    im.alpha_composite(p, ((im.width - p.width) // 2, circ - int(18 * scale)))
    return im

# ---------- rich-text layout ----------
def layout_rich(text, font, maxw, line_h):
    words = text.split(" ")
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    space = d.textlength(" ", font=font)
    lines, cur, curw = [], [], 0
    hl = False
    for w in words:
        if w.startswith("*"): hl = True
        is_hl = hl
        if "*" in w[1:]: hl = False
        clean = w.replace("*", "")
        ww = d.textlength(clean, font=font)
        if cur and curw + space + ww > maxw:
            lines.append(cur); cur, curw = [], 0
        cur.append((clean, is_hl, ww)); curw += (space if len(cur) > 1 else 0) + ww
    if cur: lines.append(cur)
    return lines, space

def render_lines(lines, space, font, color, hlcolor, maxw, line_h, stroke=0):
    imgs = []
    for ln in lines:
        tw = sum(w for _, _, w in ln) + space * (len(ln) - 1)
        im = Image.new("RGBA", (maxw + 40, line_h + 30), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        x = 20 + (maxw - tw) / 2
        for word, hl, ww in ln:
            if hl:
                d.text((x, 10), word, font=font, fill=hlcolor, stroke_width=6, stroke_fill=BLK)
            else:
                d.text((x, 10), word, font=font, fill=color, stroke_width=stroke, stroke_fill=BLK)
            x += ww + space
        imgs.append(im)
    return imgs

# ---------- background ----------
random.seed(7)
QM = [(random.uniform(0, W), random.uniform(0, H), random.uniform(60, 200), random.uniform(-25, 25), random.uniform(18, 45), random.uniform(0, 6.28)) for _ in range(16)]

def background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - W / 2) ** 2 + (yy - H * 0.42) ** 2) / H
    g = np.clip(1 - d * 1.6, 0, 1)
    base = np.array(NAVY, np.float32)
    glow = np.array([40, 30, 110], np.float32)
    rgb = base + (glow - base) * (g[..., None] ** 2) * 0.8
    return Image.fromarray(np.dstack([rgb, np.full((H, W), 255, np.float32)]).astype(np.uint8), "RGBA")

QGLYPH = {}
def qglyph(size):
    size = int(size)
    if size not in QGLYPH:
        QGLYPH[size] = text_layer("?", F("LuckiestGuy-Regular.ttf", size), (60, 50, 140, 255), pad=10)
    return QGLYPH[size]

# ---------- per-video ----------
def build(fact, outpath, preview_times=None):
    BG = background()
    TITLE = title_art()
    PANEL = panel_art()
    col = fact["color"]
    FUN = text_layer("Fun Fact", F("Lobster-Regular.ttf", 130), BLK, stroke=8, sfill=WHITE)
    catf = F("Bangers-Regular.ttf", 210 if len(fact["category"]) < 9 else 160)
    CAT = text_layer(fact["category"], catf, col, stroke=10, sfill=BLK)
    CAT = CAT.transform(CAT.size, Image.AFFINE, (1, 0.12, -CAT.height * 0.06, 0, 1, 0), resample=Image.BICUBIC)
    MEGA = emoji_img("📣", 170)
    BADGE = handle_badge(1.0)
    BELL = emoji_img("🔔", 90)
    CHIP = pill(fact["category"], F("Bangers-Regular.ttf", 74), col, WHITE, padx=46, pady=8, sw=5)
    ILL = planet_img(330) if fact["emoji"] == "PLANET" else emoji_img(fact["emoji"], 280)

    # fact card content
    cw = 940
    hf = F("LuckiestGuy-Regular.ttf", 76)
    hlines, hsp = layout_rich(fact["headline"], hf, cw - 90, 86)
    HIMG = render_lines(hlines, hsp, hf, BLK, col, cw - 90, 86)
    df = baloo(50, "Bold")
    dlines, dsp = layout_rich(fact["detail"], df, cw - 110, 62)
    DIMG = render_lines(dlines, dsp, df, (40, 36, 70), col, cw - 110, 62)
    ch = 70 + len(HIMG) * 88 + 40 + len(DIMG) * 64 + 60
    CARD = card_art(cw, ch)

    # outro
    Q1 = text_layer("Did you know that?", F("LuckiestGuy-Regular.ttf", 84), WHITE, stroke=8)
    Q2 = text_layer("Comment YES or NO", baloo(64, "ExtraBold"), YEL, stroke=0)
    PT = emoji_img("👇", 90)
    NF = text_layer("New facts every day  •  Follow!", baloo(52, "Bold"), (200, 195, 240))

    def frame(t):
        c = BG.copy()
        # drifting question marks
        for (x, y, s, rot, sp, ph) in QM:
            yy = (y - t * sp) % (H + 300) - 150
            place(c, qglyph(s), x + math.sin(t * 0.6 + ph) * 20, yy, rot=rot + math.sin(t + ph) * 6, alpha=0.38)

        # --- title: big intro -> small header ---
        tin = back(prog(t, 0.0, 0.55))
        tm = ease_in_out(prog(t, 2.8, 3.35))
        ts = (0.2 + 0.8 * tin) * (1 - tm) + 0.46 * tm
        ty = 430 * (1 - tm) + 215 * tm
        wob = math.sin(t * 2.2) * 1.5
        place(c, TITLE, W / 2, ty, scale=ts, alpha=prog(t, 0, 0.15), rot=wob)

        # --- intro panel ---
        if t < 3.4:
            out = 1 - ease_in_out(prog(t, 2.8, 3.25))
            pin = ease_out(prog(t, 0.3, 0.8))
            py = 1130 + (1 - pin) * 500 + (1 - out) * 120
            place(c, PANEL, W / 2, py, alpha=pin * out)
            mi = back(prog(t, 0.55, 0.9))
            place(c, MEGA, W / 2 + 10, py - 330, scale=mi, alpha=out, rot=math.sin(t * 6) * 6 * mi)
            fi = back(prog(t, 0.7, 1.05))
            place(c, FUN, W / 2, py - 145, scale=fi, alpha=out * prog(t, 0.7, 0.8))
            ci = back(prog(t, 0.95, 1.3), 2.6)
            place(c, CAT, W / 2, py + 40, scale=0.3 + 0.7 * ci + 0.04 * math.sin(t * 5), alpha=out * prog(t, 0.95, 1.05))
            bi = back(prog(t, 1.3, 1.7))
            place(c, BADGE, W / 2, 1640 + (1 - out) * 80, scale=bi, alpha=out)
            place(c, BELL, W / 2, 1830 + (1 - out) * 80, scale=bi, alpha=out, rot=math.sin(t * 12) * 18 * clamp(1 - prog(t, 1.7, 2.6)))

        # --- fact scene ---
        if 3.0 < t < 10.6:
            o = 1 - ease_in_out(prog(t, 9.9, 10.4))
            ci = back(prog(t, 3.2, 3.55))
            place(c, CHIP, W / 2, 440, scale=ci, alpha=o)
            ii = back(prog(t, 3.35, 3.85), 2.2)
            bob = math.sin(t * 2.6) * 14
            place(c, ILL, W / 2, 700 + bob, scale=ii * (1 + 0.03 * math.sin(t * 5.2)), alpha=o, rot=math.sin(t * 1.7) * 5)
            ki = ease_out(prog(t, 3.5, 3.95))
            top = 930
            cy = top + CARD.height / 2 + (1 - ki) * 300
            place(c, CARD, W / 2, cy, alpha=ki * o)
            y = cy - CARD.height / 2 + 30 + 70 + 43
            for i, im in enumerate(HIMG):
                li = ease_out(prog(t, 3.9 + i * 0.3, 4.25 + i * 0.3))
                place(c, im, W / 2 - 11, y + (1 - li) * 30, alpha=li * o, scale=0.9 + 0.1 * back(prog(t, 3.9 + i * 0.3, 4.3 + i * 0.3)))
                y += 88
            y += 40 - 88 / 2 + 64 / 2 - 10
            d0 = 3.9 + len(HIMG) * 0.3 + 0.35
            for i, im in enumerate(DIMG):
                li = ease_out(prog(t, d0 + i * 0.22, d0 + i * 0.22 + 0.35))
                place(c, im, W / 2 - 11, y + (1 - li) * 24, alpha=li * o)
                y += 64

        # --- outro ---
        if t > 9.9:
            q = back(prog(t, 10.2, 10.6))
            place(c, Q1, W / 2, 600, scale=q)
            q2 = ease_out(prog(t, 10.5, 10.9))
            place(c, Q2, W / 2, 740 + (1 - q2) * 30, alpha=q2)
            place(c, PT, W / 2, 860 + math.sin(t * 7) * 12, alpha=prog(t, 10.7, 10.9))
            bi = back(prog(t, 10.6, 11.1))
            place(c, BADGE, W / 2, 1220, scale=1.25 * bi + 0.03 * math.sin(t * 4))
            place(c, BELL, W / 2, 1470, scale=1.4 * bi, rot=math.sin(t * 13) * 20 * clamp(1 - prog(t, 11.6, 12.6)))
            nf = ease_out(prog(t, 11.0, 11.4))
            place(c, NF, W / 2, 1620 + (1 - nf) * 30, alpha=nf)
        # fade to/from black edges
        fo = prog(t, DUR - 0.35, DUR)
        if fo > 0:
            c = Image.blend(c, Image.new("RGBA", c.size, NAVY + (255,)), fo)
        return c.convert("RGB")

    if preview_times:
        for tt in preview_times:
            frame(tt).save(f"{outpath}_t{tt:.1f}.jpg", quality=88)
        return
    tmp = outpath + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    assert p.wait() == 0
    os.replace(tmp, outpath)

# ---------- sound ----------
SR = 44100
def sfx(fact, path, nhead, ndet):
    n = int(DUR * SR)
    a = np.zeros(n, np.float32)
    def add(t0, sig):
        i = int(t0 * SR); j = min(n, i + len(sig)); a[i:j] += sig[: j - i]
    def pop(f0=600, f1=1400, d=0.09, v=0.35):
        tt = np.arange(int(d * SR)) / SR
        fr = np.linspace(f0, f1, len(tt))
        return (np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 40) * v).astype(np.float32)
    def whoosh(d=0.45, v=0.18):
        m = int(d * SR); nz = np.random.default_rng(1).standard_normal(m).astype(np.float32)
        k = np.ones(40) / 40; nz = np.convolve(nz, k, "same")
        env = np.sin(np.linspace(0, np.pi, m)) ** 2
        return nz * env * v * 3
    def ding(f=1320, d=1.2, v=0.25):
        tt = np.arange(int(d * SR)) / SR
        s = np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.01 * tt) + 0.2 * np.sin(2 * np.pi * f * 3.0 * tt)
        return (s * np.exp(-tt * 4) * v).astype(np.float32)
    add(0.05, pop(300, 900, 0.14, 0.45))
    add(0.35, whoosh())
    add(0.6, pop(700, 1500)); add(0.75, pop(800, 1700))
    add(0.98, pop(200, 600, 0.18, 0.55))
    add(1.35, ding(1568, 0.8, 0.18))
    add(2.8, whoosh(0.5, 0.2))
    add(3.2, pop(600, 1300)); add(3.4, pop(300, 1000, 0.15, 0.45))
    for i in range(nhead): add(3.9 + i * 0.3, pop(900 + i * 120, 1600 + i * 120, 0.07, 0.25))
    add(9.9, whoosh(0.5, 0.2))
    add(10.2, pop(500, 1200, 0.12, 0.4))
    add(10.6, ding(1046, 1.0, 0.2)); add(10.75, ding(1568, 1.4, 0.2))
    a = np.tanh(a * 1.2) * 0.8
    pcm = (a * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

if __name__ == "__main__":
    os.makedirs("/home/claude/out", exist_ok=True)
    mode = sys.argv[1]
    idx = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else range(len(FACTS))
    for k in idx:
        fct = FACTS[k]
        base = f"/home/claude/out/{fct['slug']}"
        if mode == "preview":
            build(fct, base, preview_times=[1.8, 3.1, 8.0, 12.0])
        else:
            build(fct, base + "_v.mp4")
            # headline line count for sfx
            hf = F("LuckiestGuy-Regular.ttf", 76)
            nh = len(layout_rich(fct["headline"], hf, 850, 86)[0])
            sfx(fct, base + ".wav", nh, 0)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base + "_v.mp4", "-i", base + ".wav", "-map", "0:v", "-map", "1:a",
                            "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", f"/home/claude/out/DidYouKnow_{fct['slug']}.mp4"], check=True)
            print("done", fct["slug"])
