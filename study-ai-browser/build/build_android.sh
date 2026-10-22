#!/usr/bin/env bash
# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Builds the Study AI Browser Android APK from a patched Chromium checkout
# (see fetch_chromium.sh). Usage:
#
#   ./build_android.sh [TARGET_DIR] [arm64|arm]
#
# Outputs:
#   TARGET_DIR/out/studyai-android-<arch>*/apks/StudyAIBrowser-<arch>.apk
#   TARGET_DIR/out/studyai-android-<arch>*/apks/...apk.mapping (for releases)

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_PARENT="$(dirname "$PROJECT_DIR")/chromium-build"
TARGET_DIR="${1:-${CHROMIUM_BUILD_DIR:-$DEFAULT_PARENT}}"
ARCH="${2:-arm64}"

case "$ARCH" in
  arm64) GN_ARGS_FILE="android_arm64.gni"; CPU="arm64" ;;
  arm)   GN_ARGS_FILE="android_arm.gni";   CPU="arm" ;;
  *) echo "arch must be arm64 or arm" >&2; exit 2 ;;
esac

CHROMIUM_SRC="$TARGET_DIR/src"
OUT_DIR="out/studyai-android-$ARCH"

if [[ ! -d "$CHROMIUM_SRC" ]]; then
  echo "Chromium checkout not found at $CHROMIUM_SRC — run fetch_chromium.sh first." >&2
  exit 1
fi

cd "$CHROMIUM_SRC"
export PATH="$TARGET_DIR/depot_tools:$PATH"
export DEPOT_TOOLS_UPDATE=0
export AUTONINJA_GOMA=0

echo "==> Ensuring Study AI Browser patches are applied (idempotent)"
python3 "$PROJECT_DIR/build/apply_patches.py" --chromium "$PWD"

GN_ARGS="$(tr -d '\n' < "$PROJECT_DIR/config/gn_args/$GN_ARGS_FILE" | sed 's/#.*//g; s/  */ /g')"
echo "==> Generating build dir $OUT_DIR with args: $GN_ARGS"
gn gen "$OUT_DIR" --args="$GN_ARGS"

echo "==> Building chrome_public_apk for $CPU (this takes hours on first run)"
autoninja -C "$OUT_DIR" chrome_public_apk

APK_DIR="$OUT_DIR/apks"
if compgen -G "$APK_DIR/chrome-public*.apk" > /dev/null; then
  APK=$(ls "$APK_DIR"/chrome-public*.apk | head -n 1)
elif compgen -G "$APK_DIR/*.apk" > /dev/null; then
  APK=$(ls "$APK_DIR"/*.apk | head -n 1)
else
  echo "No APK produced — build failed." >&2
  exit 1
fi
cp "$APK" "$APK_DIR/StudyAIBrowser-$ARCH.apk"
if [[ -f "${APK%.apk}.apk.mapping" ]]; then
  cp "${APK%.apk}.apk.mapping" "$APK_DIR/StudyAIBrowser-$ARCH.apk.mapping"
fi

echo "==> Build OK: $CHROMIUM_SRC/$APK_DIR/StudyAIBrowser-$ARCH.apk"
