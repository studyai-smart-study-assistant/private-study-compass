#!/usr/bin/env bash
# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Signs a Study AI Browser APK with the release keystore supplied through
# environment variables (GitHub Actions secrets — NEVER stored in the repo):
#
#   STUDYAI_KEYSTORE_B64        base64-encoded .jks/.keystore file
#   STUDYAI_KEYSTORE_PASSWORD   keystore password
#   STUDYAI_KEY_ALIAS           key alias
#   STUDYAI_KEY_PASSWORD        key password (defaults to keystore password)
#
# Usage: ./sign_release.sh IN.apk OUT-signed.apk
# Without credentials, prints a warning and exits 0 so CI can still publish an
# unsigned artifact for testing (clearly labelled unsigned).

set -euo pipefail

IN="${1:?usage: sign_release.sh IN.apk OUT-signed.apk}"
OUT="${2:?usage: sign_release.sh IN.apk OUT-signed.apk}"

if [[ -z "${STUDYAI_KEYSTORE_B64:-}" ]]; then
  echo "WARNING: STUDYAI_KEYSTORE_B64 not set — copying UNSIGNED apk: $OUT" >&2
  cp "$IN" "$OUT"
  exit 0
fi

: "${STUDYAI_KEYSTORE_PASSWORD:?STUDYAI_KEYSTORE_PASSWORD is required with a keystore}"
: "${STUDYAI_KEY_ALIAS:?STUDYAI_KEY_ALIAS is required with a keystore}"
KEY_PASSWORD="${STUDYAI_KEY_PASSWORD:-$STUDYAI_KEYSTORE_PASSWORD}"

KS=$(mktemp /tmp/studyai-keystore-XXXXXX.jks)
trap 'rm -f "$KS"' EXIT
base64 --decode > "$KS" <<< "$STUDYAI_KEYSTORE_B64"

# Android SDK build-tools apksigner; provided by gclient runhooks inside the
# Chromium checkout. Prefer ANDROID_BUILD_TOOLS_DIR when set.
APKSIGNER="apksigner"
if [[ -n "${ANDROID_BUILD_TOOLS_DIR:-}" && -x "$ANDROID_BUILD_TOOLS_DIR/apksigner" ]]; then
  APKSIGNER="$ANDROID_BUILD_TOOLS_DIR/apksigner"
fi

"$APKSIGNER" sign \
  --ks "$KS" \
  --ks-key-alias "$STUDYAI_KEY_ALIAS" \
  --ks-pass "pass:$STUDYAI_KEYSTORE_PASSWORD" \
  --key-pass "pass:$KEY_PASSWORD" \
  --out "$OUT" "$IN"

"$APKSIGNER" verify --print-certs "$OUT"
echo "Signed APK written: $OUT"
