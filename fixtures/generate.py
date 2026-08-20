#!/usr/bin/env python3
"""Generate a deterministic photo library for the PhotoCleaner test.

The output contains a known number of exact duplicates, near-duplicates, blurry
photos and screenshots, so a detector can be scored against ground truth.

    python3 generate.py                 # ~300 files
    python3 generate.py --scale 10      # ~3000 files, for performance work
    python3 generate.py --out /tmp/lib  # somewhere else

Requires Pillow:  pip install Pillow
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    raise SystemExit("Pillow is missing.  pip install Pillow")

# Per 1x scale. --scale multiplies each of these.
N_ORIGINALS = 120
N_EXACT_DUPES = 40
N_NEAR_DUPES = 60
N_BLURRY = 40
N_SCREENSHOTS = 40

PORTRAIT = (1080, 1440)
LANDSCAPE = (1440, 1080)
SCREEN = (1170, 2532)

EPOCH = datetime(2024, 1, 1, 9, 0, 0)


def _palette(rng: random.Random) -> list[tuple[int, int, int]]:
    """A handful of related colours, so two originals never look alike."""
    base = rng.randint(0, 359)
    out = []
    for offset in (0, 35, 190, 215, 90):
        hue = (base + offset) % 360
        sat = rng.uniform(0.35, 0.95)
        val = rng.uniform(0.45, 1.0)
        i = int(hue / 60) % 6
        f = hue / 60 - int(hue / 60)
        p, q, t = val * (1 - sat), val * (1 - sat * f), val * (1 - sat * (1 - f))
        r, g, b = [
            (val, t, p), (q, val, p), (p, val, t),
            (p, q, val), (t, p, val), (val, p, q),
        ][i]
        out.append((int(r * 255), int(g * 255), int(b * 255)))
    return out


def make_original(rng: random.Random, size: tuple[int, int]) -> Image.Image:
    """A synthetic photo. Distinct enough that two of them never hash alike.

    The low-frequency colour field is what a perceptual hash keys on, so it is
    built from a unique random grid rather than from a shared gradient. Two
    originals therefore land far apart in hash space, which is the whole point
    of the fixture.
    """
    w, h = size
    colours = _palette(rng)

    # Unique low-frequency field: a small random grid, smoothly upscaled.
    gw, gh = 5, 7
    grid = Image.new("RGB", (gw, gh))
    grid.putdata([
        tuple(max(0, min(255, c + rng.randint(-55, 55))) for c in rng.choice(colours))
        for _ in range(gw * gh)
    ])
    img = grid.resize((w, h), Image.BICUBIC)
    draw = ImageDraw.Draw(img, "RGBA")

    # Foreground shapes, each with a hard outline. The outlines are the
    # high-frequency detail a sharpness metric measures, so a blurred copy of
    # this image scores clearly lower than the original.
    for _ in range(rng.randint(6, 13)):
        colour = rng.choice(colours) + (rng.randint(120, 245),)
        edge = tuple(255 - c for c in colour[:3]) + (255,)
        x0, y0 = rng.randint(0, w), rng.randint(0, h)
        r = rng.randint(int(min(w, h) * 0.08), int(min(w, h) * 0.40))
        lw = rng.randint(4, 9)
        shape = rng.choice(("ellipse", "rect", "triangle"))
        if shape == "ellipse":
            box = (x0 - r, y0 - r, x0 + r, y0 + r)
            draw.ellipse(box, fill=colour, outline=edge, width=lw)
        elif shape == "rect":
            box = (x0 - r, y0 - r // 2, x0 + r, y0 + r // 2)
            draw.rectangle(box, fill=colour, outline=edge, width=lw)
        else:
            pts = [(x0, y0 - r), (x0 - r, y0 + r), (x0 + r, y0 + r)]
            draw.polygon(pts, fill=colour, outline=edge, width=lw)

    # Fine speckle, so sharpness survives a downscale to thumbnail size.
    for _ in range(rng.randint(280, 520)):
        x0, y0 = rng.randint(0, w), rng.randint(0, h)
        d = rng.randint(3, 7)
        tone = 245 if rng.random() < 0.5 else 12
        draw.ellipse((x0, y0, x0 + d, y0 + d), fill=(tone, tone, tone, 230))

    return img.filter(ImageFilter.GaussianBlur(radius=0.3))


def _font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 9.2
        return ImageFont.load_default()


def make_screenshot(rng: random.Random, idx: int) -> Image.Image:
    """A phone screenshot: status bar, title, list rows, tab bar."""
    w, h = SCREEN
    dark = rng.random() < 0.4
    bg = (18, 18, 20) if dark else (248, 248, 250)
    fg = (238, 238, 240) if dark else (28, 28, 30)
    card = (34, 34, 38) if dark else (255, 255, 255)
    accent = rng.choice([(52, 199, 89), (0, 122, 255), (255, 149, 0), (255, 59, 48)])

    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)

    draw.text((60, 48), f"{rng.randint(7, 23):02d}:{rng.randint(0, 59):02d}",
              fill=fg, font=_font(38))
    draw.rounded_rectangle((w - 150, 46, w - 70, 82), radius=10, outline=fg, width=3)
    draw.rectangle((w - 146, 50, w - 146 + rng.randint(10, 72), 78), fill=accent)

    draw.text((60, 150), rng.choice(
        ["Messages", "Settings", "Photos", "Inbox", "Orders", "Notifications"]),
        fill=fg, font=_font(64))

    y = 260
    while y < h - 260:
        row_h = rng.randint(130, 190)
        draw.rounded_rectangle((48, y, w - 48, y + row_h), radius=24, fill=card)
        draw.ellipse((80, y + 28, 80 + row_h - 56, y + row_h - 28), fill=accent)
        line_w = rng.randint(300, w - 400)
        draw.rounded_rectangle((row_h + 60, y + 40, row_h + 60 + line_w, y + 62),
                               radius=11, fill=fg)
        draw.rounded_rectangle((row_h + 60, y + 84, row_h + 60 + line_w * 2 // 3, y + 102),
                               radius=9, fill=(120, 120, 128))
        y += row_h + 20

    draw.rectangle((0, h - 180, w, h), fill=card)
    for i in range(4):
        cx = w // 8 + i * w // 4
        colour = accent if i == idx % 4 else (120, 120, 128)
        draw.rounded_rectangle((cx - 30, h - 130, cx + 30, h - 70), radius=14, fill=colour)

    return img


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(Path(__file__).parent / "out"))
    ap.add_argument("--scale", type=int, default=1, help="multiply every count")
    ap.add_argument("--seed", type=int, default=20260820)
    args = ap.parse_args()

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    (out / "Camera").mkdir(parents=True)
    (out / "Screenshots").mkdir(parents=True)

    rng = random.Random(args.seed)
    s = max(1, args.scale)
    n_orig, n_exact = N_ORIGINALS * s, N_EXACT_DUPES * s
    n_near, n_blur, n_shot = N_NEAR_DUPES * s, N_BLURRY * s, N_SCREENSHOTS * s

    manifest: list[dict] = []
    counter = 0
    taken_at = EPOCH

    def write(img: Image.Image, kind: str, group: int, folder: str, ext: str) -> None:
        nonlocal counter, taken_at
        counter += 1
        taken_at += timedelta(minutes=rng.randint(7, 900))
        if ext == "png":
            name = "Screenshot_%s.png" % taken_at.strftime("%Y-%m-%d_%H-%M-%S")
            path = out / folder / name
            img.save(path, "PNG", optimize=True)
        else:
            name = "IMG_%05d.jpg" % counter
            path = out / folder / name
            img.save(path, "JPEG", quality=88, subsampling=1)
        ts = taken_at.timestamp()
        os.utime(path, (ts, ts))
        manifest.append({
            "file": f"{folder}/{name}",
            "kind": kind,
            "group": group,
            "bytes": path.stat().st_size,
            "taken_at": taken_at.isoformat(),
        })

    print(f"generating into {out} ...")

    originals: list[tuple[int, Image.Image]] = []
    for i in range(n_orig):
        size = PORTRAIT if rng.random() < 0.72 else LANDSCAPE
        img = make_original(rng, size)
        originals.append((i, img))
        write(img, "original", i, "Camera", "jpg")

    # Exact duplicates: same pixels, same encoder settings, different filename.
    for _ in range(n_exact):
        group, img = rng.choice(originals)
        write(img.copy(), "exact_duplicate", group, "Camera", "jpg")

    # Near-duplicates: re-encoded, nudged in size and brightness. Same photo.
    for _ in range(n_near):
        group, img = rng.choice(originals)
        w, h = img.size
        scale = rng.uniform(0.94, 0.99)
        near = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        # One factor for the whole image. Rolling it inside the lambda would
        # randomise the tone curve per level and stop this being a duplicate.
        gain = rng.uniform(0.95, 1.05)
        near = near.point(lambda v, g=gain: max(0, min(255, int(v * g))))
        counter += 1
        taken_at += timedelta(seconds=rng.randint(2, 40))
        name = "IMG_%05d.jpg" % counter
        path = out / "Camera" / name
        near.save(path, "JPEG", quality=rng.choice([58, 65, 72]), subsampling=2)
        ts = taken_at.timestamp()
        os.utime(path, (ts, ts))
        manifest.append({"file": f"Camera/{name}", "kind": "near_duplicate",
                         "group": group, "bytes": path.stat().st_size,
                         "taken_at": taken_at.isoformat()})

    # Blurry: a distinct shot that happens to be out of focus. Its own group.
    for i in range(n_blur):
        size = PORTRAIT if rng.random() < 0.8 else LANDSCAPE
        img = make_original(rng, size)
        img = img.filter(ImageFilter.GaussianBlur(radius=rng.uniform(9.0, 18.0)))
        write(img, "blurry", n_orig + i, "Camera", "jpg")

    for i in range(n_shot):
        write(make_screenshot(rng, i), "screenshot", -1, "Screenshots", "png")

    total_bytes = sum(m["bytes"] for m in manifest)
    summary = {
        "seed": args.seed,
        "scale": s,
        "files": len(manifest),
        "total_bytes": total_bytes,
        "counts": {
            "original": n_orig,
            "exact_duplicate": n_exact,
            "near_duplicate": n_near,
            "blurry": n_blur,
            "screenshot": n_shot,
        },
        # An original plus its exact and near duplicates form one group.
        # A group of size 1 is not a duplicate group.
        "duplicate_groups": len({
            m["group"] for m in manifest
            if m["kind"] in ("exact_duplicate", "near_duplicate")
        }),
        "reclaimable_bytes": sum(
            m["bytes"] for m in manifest
            if m["kind"] in ("exact_duplicate", "near_duplicate")
        ),
    }
    (out / "manifest.json").write_text(
        json.dumps({"summary": summary, "files": manifest}, indent=2))

    print(json.dumps(summary, indent=2))
    print(f"\n{len(manifest)} files, {total_bytes / 1e6:.1f} MB -> {out}")
    print("ground truth: manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
