import sys, wave
import numpy as np
SR = 44100
DUR = 31.0
N = int(DUR * SR)
FACT_T = [3.0, 8.0, 13.0, 18.0, 23.0]
SWIPES = [3.0, 8.0, 13.0, 18.0, 23.0, 28.0]
LAND = [0.3 + i * 0.085 for i in range(11)]

def midi(m): return 440.0 * 2 ** ((m - 69) / 12)

_pl = {}
def pluck(f, d=0.9, bright=0.6):
    key = (round(f, 2), d)
    if key in _pl: return _pl[key]
    p = int(SR / f); n = int(d * SR)
    rng = np.random.default_rng(int(f * 10))
    buf = rng.uniform(-1, 1, p).astype(np.float32)
    buf = buf * bright + np.convolve(buf, [0.5, 0.5], "same") * (1 - bright)
    out = np.zeros(n + p, np.float32)
    out[:p] = buf
    i = p
    decay = 0.996
    while i < n:
        prev = out[i - p:i]
        nxt = np.empty_like(prev)
        nxt[1:] = 0.5 * (prev[1:] + prev[:-1])
        nxt[0] = 0.5 * (prev[0] + out[i - p - 1] if i - p - 1 >= 0 else prev[0])
        out[i:i + p] = nxt[: min(p, n + p - i)] * decay
        i += p
    out = out[:n] * np.exp(-np.arange(n) / SR * 2.2)
    _pl[key] = out
    return out

def music(transpose):
    a = np.zeros(N, np.float32)
    bpm = 116; beat = 60 / bpm; e = beat / 2
    prog = [(60, [0, 4, 7]), (55, [0, 4, 7]), (57, [0, 3, 7]), (53, [0, 4, 7])]  # C G Am F
    vel = [1, .45, .75, .5, .9, .45, .75, .6]
    t = 0.0; bar = 0
    while t < DUR:
        root, tri = prog[bar % 4]
        root += transpose
        notes = [root + x for x in tri] + [root + 12]
        for k in range(8):
            tt = t + k * e
            if tt >= DUR: break
            v = vel[k]
            order = notes if k % 2 == 0 else notes[::-1]
            for j, m in enumerate(order):
                s = pluck(midi(m), 0.7)
                i = int((tt + j * 0.012) * SR)
                L = min(len(s), N - i)
                if L > 0: a[i:i + L] += s[:L] * 0.16 * v
            # shaker on offbeats
            if k % 2 == 1:
                i = int(tt * SR); L = min(int(0.05 * SR), N - i)
                if L > 0:
                    nz = np.random.default_rng(k + bar * 8).standard_normal(L).astype(np.float32)
                    nz = nz - np.convolve(nz, np.ones(6) / 6, "same")
                    a[i:i + L] += nz * np.exp(-np.arange(L) / SR * 70) * 0.05
        # bass on beats 1 and 3
        for b in (0, 2):
            tt = t + b * beat
            i = int(tt * SR); L = min(int(beat * 1.6 * SR), N - i)
            if L > 0:
                f = midi(root - 24 if b == 0 else root - 24 + 7)
                x = np.arange(L) / SR
                a[i:i + L] += (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 3) * 0.22
        t += 4 * beat; bar += 1
    return a

def sfx():
    a = np.zeros(N, np.float32)
    rng = np.random.default_rng(5)
    def add(t0, s, g=1.0):
        i = int(t0 * SR)
        if i >= N: return
        L = min(len(s), N - i); a[i:i + L] += s[:L] * g
    def pop(f0=500, f1=1300, d=0.09, v=0.4):
        x = np.arange(int(d * SR)) / SR
        fr = np.linspace(f0, f1, len(x))
        return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-x * 38) * v
    def whoosh(d=0.5, v=0.35, up=True):
        L = int(d * SR); nz = rng.standard_normal(L).astype(np.float32)
        out = np.zeros(L, np.float32)
        # sweeping lowpass by varying moving-average width
        seg = 40
        for s in range(seg):
            i0, i1 = s * L // seg, (s + 1) * L // seg
            fr = s / seg if up else 1 - s / seg
            w = int(60 - 50 * fr) + 2
            out[i0:i1] = np.convolve(nz, np.ones(w) / w, "same")[i0:i1] * (1 + fr)
        env = np.sin(np.linspace(0, np.pi, L)) ** 1.5
        return out * env * v * 2.5
    def boom(v=0.9):
        L = int(0.9 * SR); x = np.arange(L) / SR
        f = 70 * np.exp(-x * 3) + 38
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 4.5)
        nz = rng.standard_normal(L) * np.exp(-x * 25) * 0.4
        return (s + nz) * v
    def thump(v=0.35):
        L = int(0.15 * SR); x = np.arange(L) / SR
        f = 160 * np.exp(-x * 20) + 60
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 30) * v
    def ding(f=1568, d=1.2, v=0.25):
        x = np.arange(int(d * SR)) / SR
        s = np.sin(2 * np.pi * f * x) + 0.45 * np.sin(2 * np.pi * f * 2.0 * x) * np.exp(-x * 6) + 0.2 * np.sin(2 * np.pi * f * 3.01 * x) * np.exp(-x * 9)
        return s * np.exp(-x * 4) * v
    def ooh(v=0.5):
        L = int(1.6 * SR); x = np.arange(L) / SR
        out = np.zeros(L, np.float32)
        r = np.random.default_rng(9)
        for _ in range(16):
            f0 = r.uniform(130, 300)
            contour = 1 + 0.18 * np.sin(np.clip(x / 1.4, 0, 1) * np.pi) - 0.08 * x
            vib = 1 + 0.01 * np.sin(2 * np.pi * r.uniform(4, 6) * x)
            f = f0 * contour * vib
            ph = 2 * np.pi * np.cumsum(f) / SR
            dl = int(r.uniform(0, 0.12) * SR)
            s = np.zeros(L, np.float32)
            for k in range(1, int(2500 / f0)):
                fk = k * f0
                amp = np.exp(-((fk - 330) / 140) ** 2) + 0.55 * np.exp(-((fk - 800) / 220) ** 2) + 0.03
                s += np.sin(k * ph) * amp
            s = np.roll(s, dl); s[:dl] = 0
            out += s
        env = np.clip(x / 0.25, 0, 1) * np.clip((1.6 - x) / 0.6, 0, 1)
        out = out * env
        return out / np.max(np.abs(out)) * v
    # hook
    add(0.0, whoosh(0.35, 0.3))
    for i, l in enumerate(LAND[:-1]): add(l - 0.01, thump(0.28 + 0.02 * i))
    add(LAND[-1] - 0.02, boom(0.85))
    add(1.35, pop(300, 900, 0.14, 0.45)); add(1.6, pop(700, 1500, 0.08, 0.3))
    add(1.95, ding(2093, 0.9, 0.12)); add(2.05, ding(2637, 0.9, 0.1)); add(2.15, ding(2093, 0.9, 0.08))
    add(2.2, pop(900, 1800, 0.06, 0.25))
    # transitions + facts
    for s in SWIPES: add(s - 0.25, whoosh(0.5, 0.33))
    for i, ft in enumerate(FACT_T):
        add(ft + 0.4, pop(250, 700, 0.16, 0.6)); add(ft + 0.41, thump(0.4))
        add(ft + 0.9, pop(600, 1400, 0.09, 0.3))
        add(ft + 1.6, ding(1760 if i < 4 else 2093, 1.1, 0.22))
        add(ft + 4.2, pop(800, 1700, 0.07, 0.3)); add(ft + 4.3, pop(900, 1900, 0.07, 0.25)); add(ft + 4.38, pop(700, 1500, 0.07, 0.25))
        if i == 4:
            add(ft + 0.5, ding(1046, 1.4, 0.18)); add(ft + 0.6, ding(1568, 1.4, 0.16))
            add(ft + 1.55, ooh(0.55))
    # outro
    add(28.12, boom(0.4))
    for k in range(14): add(28.15 + k * 0.035, pop(1200 + rng.uniform(-300, 600), 2200, 0.04, 0.18))
    for k, f in enumerate([1046, 1318, 1568, 2093]): add(28.4 + k * 0.11, ding(f, 1.3, 0.14))
    add(29.0, pop(500, 1200, 0.1, 0.3))
    return a

def mix(transpose, path):
    m = music(transpose)
    s = sfx()
    env = np.abs(s)
    k = int(0.08 * SR)
    env = np.convolve(env, np.ones(k) / k, "same")
    duck = 1 - 0.55 * np.clip(env * 6, 0, 1)
    t = np.arange(N) / SR
    fade = np.clip(t / 0.25, 0, 1) * np.clip((DUR - t) / 0.6, 0, 1)
    out = m * duck * fade * 0.9 + s
    out = np.tanh(out * 1.1)
    out = out / np.max(np.abs(out)) * 0.93
    pcm = (out * 32767).astype(np.int16)
    st = np.repeat(pcm[:, None], 2, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())

if __name__ == "__main__":
    mix(int(sys.argv[1]), sys.argv[2])
