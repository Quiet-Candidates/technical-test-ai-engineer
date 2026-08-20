#!/usr/bin/env bash
# Push the generated library onto a device or a simulator.
#
#   ./push-to-device.sh android
#   ./push-to-device.sh ios
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${OUT:-$HERE/out}"
TARGET="${1:-}"

if [[ ! -d "$OUT" ]]; then
  echo "No $OUT — run: python3 $HERE/generate.py" >&2
  exit 1
fi

count() { find "$1" -type f \( -name '*.jpg' -o -name '*.png' \) | wc -l | tr -d ' '; }

case "$TARGET" in
  android)
    command -v adb >/dev/null || { echo "adb not found — install platform-tools" >&2; exit 1; }
    adb get-state >/dev/null 2>&1 || { echo "No device. Check: adb devices" >&2; exit 1; }

    echo "pushing $(count "$OUT") files ..."
    adb push "$OUT/Camera/."      /sdcard/DCIM/Camera/       >/dev/null
    adb push "$OUT/Screenshots/." /sdcard/Pictures/Screenshots/ >/dev/null

    # Without this the files exist but MediaStore has never heard of them.
    adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE \
      -d file:///sdcard/DCIM >/dev/null 2>&1 || true
    adb shell "content call --uri content://media/external --method scan_volume" >/dev/null 2>&1 || true
    echo "done. If the gallery looks empty, reboot the device — MediaStore can lag."
    ;;

  ios)
    command -v xcrun >/dev/null || { echo "xcrun not found — install Xcode" >&2; exit 1; }
    xcrun simctl list devices booted | grep -q Booted \
      || { echo "No booted simulator. Start one from Xcode, or: xcrun simctl boot <udid>" >&2; exit 1; }

    echo "adding $(count "$OUT") files to the booted simulator ..."
    # addmedia takes a bounded argument list, so feed it in chunks.
    find "$OUT" -type f \( -name '*.jpg' -o -name '*.png' \) -print0 \
      | xargs -0 -n 40 xcrun simctl addmedia booted
    echo "done. Open Photos on the simulator."
    echo "For a physical iPhone, AirDrop $OUT instead."
    ;;

  *)
    echo "usage: $0 {android|ios}" >&2
    exit 1
    ;;
esac
