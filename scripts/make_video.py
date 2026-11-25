#!/usr/bin/env python3
"""Render one Did You Know video from a JSON spec.

Usage:  python3 scripts/make_video.py spec.json

Spec for a single-fact video (13 s):
  {"style": "single", "category": "human_body", "out": "videos/human-body-xyz.mp4",
   "emoji": "🦴", "headline": "Babies have about *300 bones*",
   "detail": "Many fuse together as they grow. Adults have just 206."}

Spec for a 5-fact "Mind Blown" video (31 s):
  {"style": "five", "category": "space", "out": "videos/space-5-facts-2.mp4",
   "facts": [["☀️", "Headline with *keyword*", "One-line explanation.", "😲⏱️👀", "o"], ... 5 items]}
  Put the most surprising fact last. Mouth = o | jaw | grin.
  Reactions = exactly 3 emoji. Use "PLANET" as emoji to draw a planet.

category: animals | space | history | human_body | food
Headlines: <= 8 words, mark the keyword with *asterisks*. Explanation: <= 2 short lines.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))

SINGLE_STYLE = {
    "animals": ("ANIMALS", (255, 63, 191)),
    "space": ("SPACE", (64, 200, 255)),
    "history": ("HISTORY", (255, 140, 40)),
    "human_body": ("HUMAN BODY", (80, 230, 140)),
    "food": ("FOOD", (180, 110, 255)),
}
TRANSPOSE = {"animals": 0, "space": 2, "history": -3, "human_body": 5, "food": -1}


def run(cmd):
    subprocess.run(cmd, check=True)


def make_single(spec, out):
    import single
    name, color = SINGLE_STYLE[spec["category"]]
    fact = dict(slug=spec["category"], category=name, color=color, emoji=spec["emoji"],
                headline=spec["headline"], detail=spec["detail"])
    tmp = tempfile.mkdtemp()
    v, a = os.path.join(tmp, "v.mp4"), os.path.join(tmp, "a.wav")
    single.build(fact, v)
    hf = single.F("LuckiestGuy-Regular.ttf", 76)
    nh = len(single.layout_rich(fact["headline"], hf, 850, 86)[0])
    single.sfx(fact, a, nh, 0)
    run(["ffmpeg", "-v", "error", "-y", "-i", v, "-i", a, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out])


def make_five(spec, out):
    import render2, audio2
    from content import CATS
    cat = dict(next(c for c in CATS if c["slug"] == spec["category"]))
    assert len(spec["facts"]) == 5, "need exactly 5 facts"
    cat["facts"] = [tuple(f) for f in spec["facts"]]
    tmp = tempfile.mkdtemp()
    v, a, mux = os.path.join(tmp, "v.mp4"), os.path.join(tmp, "a.wav"), os.path.join(tmp, "m.mp4")
    render2.build(cat, v)
    audio2.mix(TRANSPOSE[spec["category"]], a)
    run(["ffmpeg", "-v", "error", "-y", "-i", v, "-i", a, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
         "-crf", "24", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", mux])
    os.replace(mux, out)


def preview(out, style):
    """Save a contact sheet of frames next to the video, to check the layout."""
    stem = out[:-4]
    times = ["1.8", "3.5", "6", "10", "12"] if style == "single" else ["2.5", "6.2", "21.8", "26.5", "29.8"]
    from PIL import Image
    ims = []
    for t in times:
        p = f"{stem}_t{t}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", out, "-frames:v", "1", p], check=True)
        ims.append(Image.open(p));
    sheet = Image.new("RGB", (1100 * len(ims), 1920), "white")
    for i, im in enumerate(ims): sheet.paste(im, (i * 1100, 0))
    sheet.resize((sheet.width // 3, sheet.height // 3)).save(stem + "_preview.jpg", quality=85)
    for t in times: os.remove(f"{stem}_t{t}.jpg")
    return stem + "_preview.jpg"


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    out = spec["out"]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    (make_single if spec["style"] == "single" else make_five)(spec, out)
    pv = preview(out, spec["style"])
    print(json.dumps({"video": out, "bytes": os.path.getsize(out), "preview": pv}))
