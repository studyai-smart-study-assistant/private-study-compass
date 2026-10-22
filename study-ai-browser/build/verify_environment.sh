#!/usr/bin/env bash
# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Verifies that a machine can fetch and build Chromium for Study AI Browser.
# Run on the CI build runner (GitHub-hosted larger runner) and on any new
# developer machine.
# Usage: ./verify_environment.sh [--min-ram-gb 64] [--min-disk-gb 300]

set -euo pipefail

MIN_RAM_GB=64
MIN_DISK_GB=300

while [[ $# -gt 0 ]]; do
  case "$1" in
    --min-ram-gb) MIN_RAM_GB="$2"; shift 2 ;;
    --min-disk-gb) MIN_DISK_GB="$2"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0

check() { # name, description, command...
  local name="$1" desc="$2"; shift 2
  if "$@" >/dev/null 2>&1; then
    echo "OK      ${name}: ${desc}"
  else
    echo "MISSING ${name}: ${desc}"
    failures=$((failures + 1))
  fi
}

echo "Study AI Browser build environment check"
echo "Project dir: ${PROJECT_DIR}"
echo

# Disk space where the checkout will live (cwd by default, or CHROMIUM_DIR).
checkout_parent="${CHROMIUM_DIR:-$(pwd)}"
avail_gb=$(df -BG "${checkout_parent}" | awk 'NR==2 {gsub("G","",$4); print $4}')
if (( avail_gb >= MIN_DISK_GB )); then
  echo "OK      disk: ${avail_gb} GB available at ${checkout_parent} (need ${MIN_DISK_GB})"
else
  echo "MISSING disk: only ${avail_gb} GB available at ${checkout_parent} (need ${MIN_DISK_GB})"
  failures=$((failures + 1))
fi

ram_gb=$(free -g | awk 'NR==2 {print $2}')
if (( ram_gb >= MIN_RAM_GB )); then
  echo "OK      ram: ${ram_gb} GB (need ${MIN_RAM_GB}; linking Chromium needs lots of RAM)"
else
  echo "MISSING ram: ${ram_gb} GB (need ${MIN_RAM_GB})"
  failures=$((failures + 1))
fi

cpus=$(nproc)
if (( cpus >= 16 )); then
  echo "OK      cpus: ${cpus}"
else
  echo "MISSING cpus: ${cpus} (16+ recommended for reasonable build times)"
  failures=$((failures + 1))
fi

check git     "git 2.34+"               bash -c 'git --version | grep -q "git version 2\."'
check python3 "Python 3.8+"             bash -c 'python3 --version | grep -q "Python 3\.1[0-9]\|Python 3\.8\|Python 3\.9"'
check curl    "curl (depot_tools downloads)" curl --version
check java    "JDK 17 (Android build)"  bash -c 'java -version 2>&1 | grep -q "version \"17\."'

# Android SDK/NDK are provisioned by gclient runhooks into the checkout, but
# the OS needs their prerequisites:
for pkg_header in \
  "libnss3 (Linux build deps):ldconfig -p | grep -q libnss3.so" \
  "libgbm (Linux build deps):ldconfig -p | grep -q libgbm.so"; do
  name="${pkg_header%%:*}"; cmd="${pkg_header#*:}"
  check "$name" "shared library present" bash -c "$cmd"
done

echo
cat <<'EOF'
Recommended OS packages (Ubuntu 22.04/24.04) — Chromium's install-build-deps
script installs all of them automatically after depot_tools fetch:
  sudo apt-get install -y git python3 curl openjdk-17-jdk lsb-release
  # then, inside the Chromium checkout: ./build/install-build-deps.sh
EOF

if (( failures > 0 )); then
  echo "FAILED: ${failures} check(s) missing."
  exit 1
fi
echo "All environment checks passed."
