# Test data

`generate.py` builds a photo library with known contents, so your detector can be scored against
ground truth instead of against your own eyes.

```bash
pip install Pillow
python3 generate.py                 # ~300 files, ~34 MB, about 6 seconds
python3 generate.py --scale 10      # ~3000 files, for performance work
python3 generate.py --out /tmp/lib  # somewhere else
```

Output lands in `out/`, which is gitignored. It is deterministic: same seed, same bytes.

## What it contains

At `--scale 1`:

| Kind | Count | Where |
|---|---|---|
| Original photos | 120 | `out/Camera/` |
| Exact duplicates | 40 | `out/Camera/` |
| Near-duplicates | 60 | `out/Camera/` |
| Blurry photos | 40 | `out/Camera/` |
| Screenshots | 40 | `out/Screenshots/` |
| **Total** | **300** | ~34 MB |

* An **exact duplicate** is the same file saved under a different name.
* A **near-duplicate** is the same photo, resized by a few percent, brightened or darkened slightly,
  and re-encoded at a lower JPEG quality. This is what a real "similar photos" feature has to catch.
* A **blurry** photo is its own shot, not a duplicate of anything. It belongs to its own group.
* Each file carries a plausible modification time spread across 2024 and 2025.

An original plus its duplicates form one **group**. About 66 groups have more than one member. Keeping
one file per group frees roughly **10.6 MB of the 34 MB**.

## Ground truth

`out/manifest.json` lists every file with its `kind` and its `group`, plus a summary. Use it to
measure yourself — question 2 of `docs/MY_SOLUTION.md` asks for those numbers.

```json
{
  "file": "Camera/IMG_00187.jpg",
  "kind": "near_duplicate",
  "group": 43,
  "bytes": 61204,
  "taken_at": "2024-08-02T14:31:00"
}
```

Two files are duplicates of each other when they share a `group`, the `group` is not `-1`, and
neither is `blurry`. Screenshots all carry `group: -1`; they are not duplicates of each other.

## Getting it onto a device

```bash
./push-to-device.sh android      # adb push + media scan
./push-to-device.sh ios          # xcrun simctl addmedia, booted simulator
```

For a physical iPhone, AirDrop the `out/` folder to it — the simulator route does not apply.

## Honest limitations

These are generated images, not photographs. They have the properties that matter here — duplicate
groups, a sharp/blurry split, screenshot layouts — but they are flat abstract shapes. If your
approach depends on photographic content, say so in `MY_SOLUTION.md` and test it on your own library
as well.
