#!/usr/bin/env bash
# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Runs the Study AI Browser test suite (stdlib unittest; no dependencies).
# Usage: ./tests/run_tests.sh

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "==> Running Study AI Browser tests"
python3 -m unittest discover -s tests -p "test_*.py" -v 2>&1 | tail -n 25

# Fail when the pipe swallowed a non-zero status from unittest.
status="${PIPESTATUS[0]:-0}"
exit "$status"
