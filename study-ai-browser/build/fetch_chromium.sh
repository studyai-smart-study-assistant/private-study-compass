#!/usr/bin/env bash
# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Fetches the pinned Chromium source, applies the Study AI Browser patches,
# and syncs dependencies. Run once per machine (or when the pin changes).
#
# Usage:
#   ./fetch_chromium.sh [TARGET_DIR]        # default: ../../chromium relative to project
#   ./verify_environment.sh first — a full checkout needs ~300 GB and several hours.
#
# Environment:
#   CHROMIUM_VERSION   override the pinned version (also updates nothing on disk;
#                      the pin stays config/chromium_pin.json)

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_PARENT="$(dirname "$PROJECT_DIR")/chromium-build"
TARGET_DIR="${1:-${CHROMIUM_BUILD_DIR:-$DEFAULT_PARENT}}"
CHROMIUM_VERSION="${CHROMIUM_VERSION:-$(python3 - "$PROJECT_DIR/config/chromium_pin.json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1]))["chromium_version"])
PY
)}"

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

if [[ ! -d depot_tools ]]; then
  echo "==> Cloning depot_tools"
  git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
fi
export PATH="$PWD/depot_tools:$PATH"
# depot_tools must not self-update on CI runners.
export DEPOT_TOOLS_UPDATE=0

if [[ ! -d src ]]; then
  echo "==> Fetching Chromium (this is a 100+ GB, multi-hour step)"
  fetch --nohooks chromium
fi

cd src
echo "==> Checking out pinned version ${CHROMIUM_VERSION}"
git fetch origin "refs/tags/${CHROMIUM_VERSION}" --depth=1
git checkout --detach "FETCH_HEAD"

echo "==> gclient sync (downloads Android SDK/NDK via hooks)"
gclient sync -D --with_branch_heads

echo "==> Running hooks (SDK/NDK download, clang toolchain)"
gclient runhooks

echo "==> Verifying Study AI Browser patch contexts against ${CHROMIUM_VERSION}"
python3 "$PROJECT_DIR/build/apply_patches.py" --chromium "$PWD" --check

echo "==> Applying Study AI Browser patches"
python3 "$PROJECT_DIR/build/apply_patches.py" --chromium "$PWD"

echo "==> Done. Build with: $PROJECT_DIR/build/build_android.sh"
