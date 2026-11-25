import math, random, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from content import CATS
from quizzy import quizzy

W, H, FPS, DUR = 1080, 1920, 30, 31.0
import os as _os
FD = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "fonts") + "/"
EMOJI = FD + "NotoColorEmoji.ttf"
K = (10, 8, 20)
WHITE = (255, 255, 255)
YEL = (250, 222, 50)
GOLD = (255, 196, 40)
HANDLE = "SOCMED311"
SWIPES = [3.0, 8.0, 13.0, 18.0, 23.0, 28.0]
FACT_T = [3.0, 8.0, 13.0, 18.0, 23.0]

def LG(s): return ImageFont.truetype(FD + "LuckiestGuy-Regular.ttf", s)
def BG_(s): return ImageFont.truetype(FD + "Bangers-Regular.ttf", s)
def POP(s, w="SemiBold"): return ImageFont.truetype(FD + f"Poppins-{w}.ttf", s)

def clamp(x): return max(0.0, min(1.0, x))
def prog(t, a, b): return clamp((t - a) / (b - a))
def eo(x): return 1 - (1 - x) ** 3
def eio(x): return 3 * x * x - 2 * x * x * x
def back(x, s=1.9):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1
def lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

# ---------------- sprites ----------------
_ecache = {}
def emoji_img(ch, size):
    key = (ch, size)
    if key in _ecache: return _ecache[key]
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((90, 90), ch, font=f, embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox())
    r = size / max(im.size)
    im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    _ecache[key] = im
    return im

def planet_img(size):
    s = size * 2
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    c = s / 2; r = s * 0.46
    d = np.sqrt((xx - c) ** 2 + (yy - c) ** 2)
    lx, ly = (xx - c * 0.75) / r, (yy - c * 0.7) / r
    shade = np.clip(1.15 - np.sqrt(lx ** 2 + ly ** 2) * 0.7, 0.3, 1.1)
    band = 0.88 + 0.12 * np.sin((yy / s) * 26 + np.sin(xx / s * 6) * 1.5)
    rgb = np.clip(np.array([242, 172, 82], np.float32)[None, None] * (shade * band)[..., None], 0, 255)
    a = np.clip((r - d) * 1.5, 0, 1) * 255
    p = Image.fromarray(np.dstack([rgb, a]).astype(np.uint8), "RGBA")
    return p.resize((size, size), Image.LANCZOS)

def cell_img(size):
    s = size * 2
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([10, 10, s - 10, s - 10], outline=(255, 255, 255, 255), width=int(s * 0.06))
    d.ellipse([s * 0.38, s * 0.34, s * 0.66, s * 0.6], fill=(255, 255, 255, 255))
    return im.resize((size, size), Image.LANCZOS)

def silhouette(im, alpha):
    a = im.getchannel("A").point(lambda v: int(v * alpha))
    out = Image.new("RGBA", im.size, (255, 255, 255, 0))
    out.putalpha(a)
    return out

def cartoonize(im, ow=12, shadow=(16, 18)):
    """thick black outline + soft drop shadow"""
    pad = ow + 30
    big = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    big.alpha_composite(im, (pad, pad))
    a = big.getchannel("A").point(lambda v: 255 if v > 90 else 0)
    ol = a.filter(ImageFilter.MaxFilter(ow * 2 + 1)).filter(ImageFilter.GaussianBlur(1))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", big.size, (0, 0, 0, 0))
    sh.putalpha(ol.point(lambda v: int(v * 0.35)))
    out.alpha_composite(sh, shadow)
    blk = Image.new("RGBA", big.size, K + (0,))
    blk.putalpha(ol)
    out.alpha_composite(blk)
    out.alpha_composite(big)
    return out

def text_img(txt, font, fill, stroke=0, sfill=K, shadow=None, pad=30):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    so = shadow[1] if shadow else 0
    im = Image.new("RGBA", (r - l + pad * 2 + so, b - t + pad * 2 + so), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    if shadow:
        dd.text((pad - l + so, pad - t + so), txt, font=font, fill=shadow[0], stroke_width=stroke, stroke_fill=K)
    dd.text((pad - l, pad - t), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return im

def pill(txt, font, bg, fg, padx=40, pady=14, border=6, stroke=0, icon=None, h_min=0):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    th = b - t
    h = max(th + pady * 2, h_min)
    iw = 0
    if icon is not None: iw = icon.width + 14
    w = r - l + padx * 2 + iw
    im = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([18, 18, 18 + w, 18 + h], radius=h // 2, fill=(0, 0, 0, 90))
    dd.rounded_rectangle([6, 6, 6 + w, 6 + h], radius=h // 2, fill=bg, outline=K, width=border)
    x = 6 + padx
    if icon is not None:
        im.alpha_composite(icon, (x, 6 + (h - icon.height) // 2)); x += iw
    dd.text((x - l, 6 + (h - th) // 2 - t), txt, font=font, fill=fg, stroke_width=stroke, stroke_fill=K)
    return im

def place(cv, im, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.003 or scale <= 0.01: return
    if abs(scale - 1) > 0.002:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    cv.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def handle_badge(accent):
    f = BG_(84)
    circ = 120
    c = Image.new("RGBA", (circ, circ), (0, 0, 0, 0))
    ImageDraw.Draw(c).ellipse([3, 3, circ - 4, circ - 4], fill=(245, 243, 232), outline=K, width=6)
    e = emoji_img("💡", 78)
    c.alpha_composite(e, ((circ - e.width) // 2, (circ - e.height) // 2))
    p = pill(HANDLE, f, YEL, K, padx=60, pady=6, h_min=96)
    im = Image.new("RGBA", (p.width + circ - 40, max(p.height, circ) + 6), (0, 0, 0, 0))
    im.alpha_composite(p, (circ - 46, (im.height - p.height) // 2))
    im.alpha_composite(c, (0, (im.height - circ) // 2))
    return im

# ---------------- background ----------------
class Background:
    def __init__(self, cat, seed):
        g1, g2 = np.array(cat["g1"], np.float32), np.array(cat["g2"], np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        tt = np.clip((yy / H) * 0.85 + (xx / W) * 0.15, 0, 1)[..., None]
        rgb = g1 + (g2 - g1) * tt
        d = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
        vig = np.clip(1 - (d - 0.35) * 0.9, 0.62, 1)[..., None]
        rgb = rgb * vig
        self.base = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.full((H, W), 255)]).astype(np.uint8), "RGBA")
        rng = np.random.default_rng(seed)
        self.grain = [rng.normal(0, 7, (H // 2, W // 2)).astype(np.float32) for _ in range(4)]
        self.grain = [np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None].astype(np.int16) for g in self.grain]
        random.seed(seed)
        self.sprites = []
        for i in range(13):
            key = cat["float"][i % len(cat["float"])]
            sz = random.randint(90, 210)
            if key == "CELL": src = cell_img(sz)
            else: src = emoji_img(key, sz)
            self.sprites.append(dict(im=silhouette(src, 0.16 if cat["slug"] != "space" else 0.13),
                                     x=random.uniform(-40, W + 40), y=random.uniform(0, H + 300),
                                     sp=random.uniform(14, 34), rot=random.uniform(-30, 30),
                                     rs=random.uniform(-12, 12), ph=random.uniform(0, 6.28)))
        self.stars = None
        if cat["slug"] == "space":
            self.stars = [(random.uniform(0, W), random.uniform(0, H), random.uniform(1.5, 4.5), random.uniform(0, 6.28), random.uniform(1, 3)) for _ in range(110)]

    def frame(self, t):
        c = self.base.copy()
        if self.stars:
            d = ImageDraw.Draw(c)
            for x, y, r, ph, sp in self.stars:
                a = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * sp + ph))
                rr = r * (0.7 + 0.5 * a)
                col = (255, 255, 255, int(255 * a))
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col)
                if r > 3.8:
                    d.line([x - rr * 3, y, x + rr * 3, y], fill=(255, 255, 255, int(150 * a)), width=2)
                    d.line([x, y - rr * 3, x, y + rr * 3], fill=(255, 255, 255, int(150 * a)), width=2)
        for s in self.sprites:
            y = (s["y"] - t * s["sp"]) % (H + 400) - 200
            x = s["x"] + math.sin(t * 0.5 + s["ph"]) * 30
            place(c, s["im"], x, y, rot=s["rot"] + t * s["rs"])
        return c

# ---------------- text layout ----------------
def wrap_words(words, font, maxw):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    sp = d.textlength(" ", font=font)
    lines, cur, cw = [], [], 0
    for w, hl in words:
        ww = d.textlength(w, font=font)
        if cur and cw + sp + ww > maxw:
            lines.append(cur); cur, cw = [], 0
        cur.append((w, hl, ww)); cw += (sp if len(cur) > 1 else 0) + ww
    if cur: lines.append(cur)
    return lines, sp

def parse_hl(text):
    out, hl = [], False
    for w in text.split(" "):
        if w.startswith("*"): hl = True
        is_hl = hl
        if "*" in w[1:]: hl = False
        out.append((w.replace("*", ""), is_hl))
    return out

class Headline:
    def __init__(self, text, accent, maxw=870, size=80):
        f = LG(size)
        self.lh = int(size * 1.12)
        self.lines, sp = wrap_words(parse_hl(text), f, maxw)
        while len(self.lines) > 3 and size > 60:
            size -= 6; f = LG(size); self.lh = int(size * 1.12)
            self.lines, sp = wrap_words(parse_hl(text), f, maxw)
        kw_fill = K if lum(accent) > 140 else WHITE
        self.imgs, self.rects = [], []
        for li, ln in enumerate(self.lines):
            tw = sum(w for _, _, w in ln) + sp * (len(ln) - 1)
            im = Image.new("RGBA", (maxw + 60, self.lh + 40), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            x = 30 + (maxw - tw) / 2
            run = None
            for w, hl, ww in ln:
                if hl:
                    d.text((x, 14), w, font=f, fill=kw_fill, stroke_width=0 if kw_fill == K else 5, stroke_fill=K)
                    bb = d.textbbox((x, 14), w, font=f)
                    run = [run[0] if run else x, x + ww, bb[1], bb[3]]
                else:
                    if run: self.rects.append((li,) + tuple(run)); run = None
                    d.text((x, 14), w, font=f, fill=WHITE, stroke_width=5, stroke_fill=K)
                x += ww + sp
            if run: self.rects.append((li,) + tuple(run))
            self.imgs.append(im)
        self.w = maxw + 60
        self.h = len(self.lines) * self.lh

class Expl:
    def __init__(self, text, maxw=860, size=47):
        self.f = POP(size)
        lines, sp = wrap_words([(w, False) for w in text.split(" ")], self.f, maxw)
        self.lines = [" ".join(w for w, _, _ in ln) for ln in lines]
        d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        self.widths = [d.textlength(s, font=self.f) for s in self.lines]
        self.lh = int(size * 1.42)
        self.n = sum(len(s) for s in self.lines)
        self.h = len(self.lines) * self.lh

def marker(d, x0, y0, x1, y1, p, col):
    if p <= 0: return
    xe = x0 - 12 + (x1 - x0 + 26) * p
    pts = [(x0 - 12, y0 + 10), (xe, y0 + 2), (xe + 5, y0 + (y1 - y0) * 0.5), (xe - 3, y1 - 4), (x0 - 16, y1 + 2), (x0 - 10, y0 + (y1 - y0) * 0.55)]
    d.polygon(pts, fill=col)

# ---------------- glass ----------------
def glass(cv, x0, y0, w, h, alpha):
    if alpha <= 0.01: return
    x0, y0, w, h = int(x0), int(y0), int(w), int(h)
    box = (max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h))
    if box[2] <= box[0] or box[3] <= box[1]: return
    reg = cv.crop(box)
    small = reg.resize((max(1, reg.width // 4), max(1, reg.height // 4)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5))
    reg = small.resize(reg.size, Image.BILINEAR)
    tint = Image.new("RGBA", reg.size, (12, 10, 30, 105))
    reg.alpha_composite(tint)
    hi = Image.new("RGBA", reg.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.rounded_rectangle([0, 0, reg.width - 1, reg.height - 1], radius=44, outline=(255, 255, 255, 150), width=4)
    hd.rounded_rectangle([8, 8, reg.width - 9, 60], radius=30, fill=(255, 255, 255, 22))
    reg.alpha_composite(hi)
    mask = Image.new("L", reg.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, reg.width - 1, reg.height - 1], radius=44, fill=int(255 * alpha))
    sh = Image.new("RGBA", (reg.width + 40, reg.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 30, reg.width + 20, reg.height + 30], radius=44, fill=(0, 0, 0, int(70 * alpha)))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    cv.alpha_composite(sh, (box[0] - 20, box[1] - 20))
    cv.paste(reg, box[:2], mask)

# ---------------- confetti ----------------
class Confetti:
    def __init__(self, cols, seed=3):
        rng = random.Random(seed)
        self.p = []
        for _ in range(170):
            a = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
            v = rng.uniform(700, 1700)
            self.p.append(dict(vx=math.cos(a) * v * 0.8, vy=math.sin(a) * v, c=rng.choice(cols), w=rng.uniform(14, 26), h=rng.uniform(8, 14),
                               r0=rng.uniform(0, 6.28), rs=rng.uniform(-10, 10), fl=rng.uniform(4, 12), x0=540 + rng.uniform(-60, 60), y0=760))
    def draw(self, cv, t):
        if t < 0: return
        d = ImageDraw.Draw(cv)
        for p in self.p:
            drag = 1.6
            k = (1 - math.exp(-drag * t)) / drag
            x = p["x0"] + p["vx"] * k + math.sin(t * 3 + p["r0"]) * 30 * min(1, t)
            y = p["y0"] + p["vy"] * k + 380 * t * t * 0.5 + 260 * t
            if y > H + 50: continue
            ang = p["r0"] + p["rs"] * t
            sq = abs(math.cos(t * p["fl"] + p["r0"]))
            hw, hh = p["w"] / 2, p["h"] / 2 * (0.25 + 0.75 * sq)
            ca, sa = math.cos(ang), math.sin(ang)
            pts = [(x + ca * dx - sa * dy, y + sa * dx + ca * dy) for dx, dy in [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]]
            d.polygon(pts, fill=p["c"])

# ---------------- video ----------------
def build(cat, out, preview=None):
    acc = cat["accent"]
    acc_txt = K if lum(acc) > 140 else WHITE
    bg = Background(cat, seed=cat["key"] * 11 + 5)
    # hook letters
    hf = LG(205)
    letters = []
    for li, word in enumerate(["DID YOU", "KNOW?"]):
        d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        tw = d.textlength(word, font=hf)
        x = (W - tw) / 2
        for ch in word:
            cw = d.textlength(ch, font=hf)
            if ch != " ":
                shadow_col = acc if cat["slug"] != "human_body" else (150, 30, 70)
                im = text_img(ch, hf, WHITE, stroke=13, shadow=(shadow_col, 14), pad=20)
                letters.append((im, x + cw / 2, 560 + li * 225))
            x += cw
    LAND = [0.3 + i * 0.085 for i in range(len(letters))]
    sub1 = text_img(cat["hook"], LG(96), acc, stroke=9, sfill=K)
    sub2 = text_img("that sound FAKE (but aren't)", POP(58, "Bold"), WHITE, stroke=5)
    badge = handle_badge(acc)
    bell = cartoonize(emoji_img("🔔", 90), ow=5, shadow=(6, 8))
    chip = pill(cat["name"], BG_(60), acc, acc_txt, padx=30, pady=4, border=5, stroke=0, icon=emoji_img(cat["icon"], 56), h_min=78)
    nums = [text_img(f"#{i+1}", LG(330), acc, stroke=14, shadow=(WHITE if cat["slug"] != "human_body" else (150, 30, 70), 16)) for i in range(5)]
    best = text_img("SAVED THE BEST FOR LAST", LG(58), GOLD, stroke=6)
    best_glow = Image.new("RGBA", (best.width + 80, best.height + 80), (0, 0, 0, 0))
    best_glow.alpha_composite(best, (40, 40))
    gl = best_glow.getchannel("A").filter(ImageFilter.GaussianBlur(18))
    best_glow = Image.new("RGBA", best_glow.size, GOLD + (0,)); best_glow.putalpha(gl.point(lambda v: min(255, v * 2)))
    halo = Image.new("RGBA", (560, 560), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([80, 80, 480, 480], fill=GOLD + (170,))
    halo = halo.filter(ImageFilter.GaussianBlur(60))
    facts = []
    for (ill, head, expl, react, mouth) in cat["facts"]:
        src = planet_img(330) if ill == "PLANET" else emoji_img(ill, 330)
        hd = Headline(head, acc)
        ex = Expl(expl)
        ch = 56 + hd.h + 26 + ex.h + 50
        top = min(975, 1360 - ch)
        ill_im = cartoonize(src)
        avail = top - 30 - 480
        isc = min(0.95, avail / ill_im.height)
        facts.append(dict(ill=ill_im, top=top, iy=480 + avail / 2, isc=isc, hd=hd, ex=ex, ch=ch, react=[emoji_img(e, 110) for e in _split_emoji(react)], mouth=mouth))
    sparkle = emoji_img("✨", 90)
    q1 = text_img("WHICH ONE SHOCKED", LG(84), WHITE, stroke=8)
    q1b = text_img("YOU MOST?", LG(84), WHITE, stroke=8)
    q2 = text_img("Comment 1–5!", LG(124), acc, stroke=10)
    point = emoji_img("👇", 100)
    follow = pill("FOLLOW  +", BG_(78), acc, acc_txt, padx=60, pady=6, h_min=110)
    nf = text_img("New facts every day  •  Follow!", POP(48, "SemiBold"), WHITE, stroke=3)
    thumbs = cartoonize(emoji_img("👍", 120), ow=5, shadow=(6, 8))
    conf = Confetti([acc + (255,), tuple(cat["g1"]) + (255,), tuple(cat["g2"]) + (255,), (255, 255, 255, 255), (255, 212, 0, 255), (255, 80, 140, 255)], seed=cat["key"])

    def shake(t):
        ev = [(LAND[i], 5) for i in range(len(LAND) - 1)] + [(LAND[-1], 24)] + [(ft + 0.42, 12) for ft in FACT_T]
        a = sum(am * math.exp(-(t - te) * 13) for te, am in ev if 0 <= t - te < 0.4)
        return a * math.sin(t * 97), a * math.cos(t * 71)

    def quizzy_at(cv, t, x, y, scale, mode, fi=None):
        blink = 1.0 if (t % 2.9) < 0.12 else 0.0
        kw = dict(blink=blink, look=(-0.9, 0.2))
        jump = 0
        if mode == "wink":
            kw.update(wink=True, mouth="grin", blink=0, look=(-0.5, 0))
        elif mode == "react":
            m = facts[fi]["mouth"]
            kw.update(mouth=m, eye=1.35 if m == "jaw" else 1.18, blink=0, look=(0, -0.6))
        elif mode == "happy":
            kw.update(mouth="grin", look=(-0.6, -0.3))
        q = quizzy(**kw)
        bob = math.sin(t * 3.1) * 8
        place(cv, q, x, y + bob, scale=scale)

    def frame(t):
        cv = bg.frame(t)
        d = ImageDraw.Draw(cv)
        seg = sum(1 for s in SWIPES if t >= s)  # 0 hook, 1..5 facts, 6 outro
        # ---------- HOOK ----------
        if seg == 0:
            for i, (im, x, y) in enumerate(letters):
                p = prog(t, LAND[i] - 0.13, LAND[i])
                if p <= 0: continue
                s = 3.2 - 2.2 * eio(p) if p < 1 else 1 + 0.12 * math.exp(-(t - LAND[i]) * 10) * math.sin((t - LAND[i]) * 30)
                rot = (1 - p) * (-20 if i % 2 else 20)
                place(cv, im, x, y + math.sin(t * 2 + i) * 4 * (p >= 1), scale=s, alpha=p ** 0.5, rot=rot)
            p1 = back(prog(t, 1.35, 1.7), 2.3)
            place(cv, sub1, W / 2, 1000, scale=p1, rot=-3 * p1)
            p2 = eo(prog(t, 1.55, 1.9))
            place(cv, sub2, W / 2, 1105 + (1 - p2) * 40, alpha=p2)
            pb = back(prog(t, 1.85, 2.25))
            place(cv, badge, 430, 1400 + (1 - pb) * 260, alpha=clamp(pb))
            place(cv, bell, 430 + badge.width / 2 + 50, 1400 + (1 - pb) * 260, alpha=clamp(pb), rot=math.sin(t * 22) * 22 * clamp(1 - prog(t, 2.3, 3)))
            pq = back(prog(t, 1.6, 2.05), 2.2)
            if pq > 0:
                qx = 1180 - 290 * pq; qy = 1720 - 300 * pq
                quizzy_at(cv, t, qx, qy, 0.78, "wink" if 2.15 < t < 2.75 else "idle")
        # ---------- FACTS ----------
        elif seg <= 5:
            i = seg - 1
            fd = facts[i]
            tau = t - FACT_T[i]
            # top bar
            place(cv, chip, 70 + chip.width / 2, 315)
            for j in range(5):
                cx = 790 + j * 54; cy = 315
                r = 15 + (4 * (0.5 + 0.5 * math.sin(t * 6)) if j == i else 0)
                if j <= i:
                    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=acc, outline=K, width=5)
                else:
                    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 60), outline=(255, 255, 255, 230), width=4)
            # best-for-last extras
            if i == 4:
                pb = back(prog(tau, 0.5, 0.85))
                place(cv, halo, 540, fd["iy"], scale=1 + 0.06 * math.sin(t * 4), alpha=clamp(prog(tau, 0.8, 1.2)) * (0.75 + 0.25 * math.sin(t * 5)))
            # illustration
            pi_ = back(prog(tau, 0.85, 1.3), 2.3)
            if pi_ > 0:
                wig = math.sin(t * 2.3) * 5
                br = 1 + 0.035 * math.sin(t * 4.6)
                place(cv, fd["ill"], 540, fd["iy"] + math.sin(t * 2.7) * 14, scale=fd["isc"] * pi_ * br, rot=wig)
            if i == 4:
                place(cv, best_glow, 540, 452, alpha=pb * (0.6 + 0.4 * math.sin(t * 5)) if pb > 0 else 0, scale=max(pb, 0.01))
                place(cv, best, 540, 452, scale=max(pb, 0.01))
            # number stamp -> corner
            ps = prog(tau, 0.15, 0.42)
            pm = eio(prog(tau, 0.75, 1.05))
            if ps > 0:
                s_in = 2.6 - 1.6 * eio(ps)
                sc = s_in * (1 - pm) + 0.3 * pm
                x = 540 * (1 - pm) + 975 * pm
                y = 690 * (1 - pm) + 425 * pm
                place(cv, nums[i], x, y, scale=sc, alpha=ps ** 0.5, rot=-6 * (1 - pm) - 4 * pm)
            # card
            pc = eo(prog(tau, 1.0, 1.35))
            if pc > 0:
                ch = fd["ch"]; top = fd["top"] + (1 - pc) * 220
                glass(cv, 60, top, 960, ch, pc)
                d = ImageDraw.Draw(cv)
                hd, ex = fd["hd"], fd["ex"]
                hy = top + 40
                pm2 = eo(prog(tau, 1.6, 1.9))
                il = 540 - hd.w / 2
                for (li, x0, x1, yt, yb) in hd.rects:
                    it = hy + li * hd.lh - 14
                    marker(d, il + x0 - 4, it + yt - 10, il + x1 + 4, it + yb + 10, pm2, acc + (255,))
                for li, im in enumerate(hd.imgs):
                    pl = eo(prog(tau, 1.2 + li * 0.1, 1.5 + li * 0.1))
                    place(cv, im, 540, hy + li * hd.lh + im.height / 2 - 14 + (1 - pl) * 24, alpha=pl * pc)
                if hd.rects:
                    li, x0, x1, yt, yb = hd.rects[-1]
                    psp = prog(tau, 1.85, 2.4)
                    if 0 < psp < 1:
                        place(cv, sparkle, il + x1 + 14, hy + li * hd.lh - 14 + yt, scale=0.5 + 0.7 * math.sin(psp * math.pi), alpha=math.sin(psp * math.pi), rot=psp * 90)
                # typewriter
                n = int(max(0, tau - 1.95) / 0.017)
                ey = hy + hd.h + 26
                for li, s in enumerate(ex.lines):
                    if n <= 0: break
                    part = s[:n]; n -= len(s)
                    xw = 540 - ex.widths[li] / 2
                    d.text((xw, ey + li * ex.lh), part, font=ex.f, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(10, 8, 30))
            # mascot + reaction
            react = 4.15 < tau < 4.95
            if react:
                pr = prog(tau, 4.15, 4.35)
                quizzy_at(cv, t, 925, 1480 - 40 * math.sin(pr * math.pi), 0.7 * (1 + 0.12 * math.sin(pr * math.pi)), "react", i)
                for k, e in enumerate(fd["react"]):
                    pe = prog(tau, 4.2 + k * 0.08, 4.95)
                    if pe <= 0: continue
                    ang = math.pi * (0.97 + k * 0.075)
                    rr = 90 + 250 * eo(pe)
                    place(cv, e, 900 + math.cos(ang) * rr, 1470 + math.sin(ang) * rr, scale=0.5 + 0.6 * back(min(1, pe * 2.5)), alpha=1 - prog(pe, 0.7, 1.0))
            else:
                quizzy_at(cv, t, 925, 1480, 0.7, "idle")
        # ---------- OUTRO ----------
        else:
            to = t - 28.0
            conf.draw(cv, to - 0.15)
            p = back(prog(to, 0.25, 0.6))
            place(cv, q1, W / 2, 470, scale=p)
            place(cv, q1b, W / 2, 575, scale=back(prog(to, 0.35, 0.7)))
            p2 = back(prog(to, 0.55, 0.95), 2.4)
            place(cv, q2, W / 2, 730, scale=p2 * (1 + 0.03 * math.sin(t * 5)), rot=-3)
            place(cv, point, W / 2, 875 + abs(math.sin(t * 6)) * -22, alpha=prog(to, 0.8, 1.0))
            pb = back(prog(to, 0.8, 1.2))
            place(cv, badge, W / 2, 1060, scale=1.1 * pb)
            pf = back(prog(to, 1.0, 1.4))
            place(cv, follow, W / 2, 1220, scale=pf * (1 + 0.06 * max(0, math.sin(t * 7))))
            pn = eo(prog(to, 1.2, 1.6))
            place(cv, nf, W / 2, 1360 + (1 - pn) * 30, alpha=pn)
            quizzy_at(cv, t, 925, 1480, 0.7, "happy")
            place(cv, thumbs, 800, 1500, scale=back(prog(to, 0.5, 0.9)), rot=math.sin(t * 8) * 10)
        # ---------- swipe transitions ----------
        for s in SWIPES:
            if abs(t - s) < 0.24:
                pp = (t - s + 0.24) / 0.48
                cx = -900 + pp * (W + 1800)
                for off, col, wd in [(-120, K, 1500), (0, acc, 1400), (180, WHITE, 70)]:
                    x = cx + off
                    poly = [(x - wd / 2 - 300, H + 50), (x - wd / 2 + 300, -50), (x + wd / 2 + 300, -50), (x + wd / 2 - 300, H + 50)]
                    ImageDraw.Draw(cv).polygon(poly, fill=col + (255,))
        # shake
        sx, sy = shake(t)
        if abs(sx) + abs(sy) > 0.5:
            s = 1.04
            cv = cv.transform(cv.size, Image.AFFINE, (1 / s, 0, (W - W / s) / 2 - sx, 0, 1 / s, (H - H / s) / 2 - sy), resample=Image.BILINEAR)
        arr = np.asarray(cv.convert("RGB")).astype(np.int16)
        arr = arr + bg.grain[int(t * 12) % 4]
        # black flash at start / fade to black at end (seamless loop)
        fl = max(1 - prog(t, 0.04, 0.28), prog(t, DUR - 0.3, DUR - 0.03))
        if fl > 0: arr = arr * (1 - fl)
        return np.clip(arr, 0, 255).astype(np.uint8)

    if preview:
        for tt in preview:
            Image.fromarray(frame(tt)).save(f"{out}_t{tt:05.2f}.jpg", quality=88)
        return
    tmp = out + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for k in range(int(DUR * FPS)):
        p.stdin.write(frame(k / FPS).tobytes())
    p.stdin.close()
    assert p.wait() == 0
    os.replace(tmp, out)

def _split_emoji(s):
    out, cur = [], ""
    for ch in s:
        if cur and ord(ch) >= 0x1F000 or (cur and (0x2600 <= ord(ch) < 0x27C0 or 0x2300 <= ord(ch) < 0x2400)):
            out.append(cur); cur = ch
        else:
            cur += ch
    if cur: out.append(cur)
    return out[:3]

if __name__ == "__main__":
    os.makedirs("/home/claude/v2/out", exist_ok=True)
    which = [int(x) for x in sys.argv[2].split(",")]
    for k in which:
        cat = CATS[k]
        base = f"/home/claude/v2/out/{cat['slug']}"
        if sys.argv[1] == "preview":
            build(cat, base, preview=[float(x) for x in sys.argv[3].split(",")])
        else:
            build(cat, base + "_v.mp4")
            print("video done", cat["slug"], flush=True)
