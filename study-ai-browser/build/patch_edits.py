# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Edit primitives for Study AI Browser Chromium customization patches.

Every patch module under patches/ imports its edit types from this module and
exposes a single module-level ``PATCH`` (a :class:`Patch`). The engine
(``apply_patches.py``) applies the edits to a Chromium checkout and fails
loudly when an expected context is missing -- a patch that no longer matches
the pinned Chromium tree is treated as a build-blocking error, never a silent
no-op. Run with ``--check`` in CI to validate all contexts against a real
checkout before any build.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Patch:
    """A named set of edits applied to a Chromium checkout."""

    id: str
    description: str
    edits: tuple


@dataclass(frozen=True)
class Replace:
    """Replace an exact substring that must occur exactly once.

    Idempotent: if ``new`` is already present and ``old`` is gone, the edit is
    reported as already applied instead of an error.
    """

    path: str
    old: str
    new: str
    description: str = ""


@dataclass(frozen=True)
class RegexReplace:
    """Replace text matching a regex; ``expected_matches`` must be matched.

    Idempotency: when the pattern no longer matches but ``applied_pattern``
    does, the edit is reported as already applied.
    """

    path: str
    pattern: str
    replacement: str
    expected_matches: int = 1
    applied_pattern: str = ""
    description: str = ""


@dataclass(frozen=True)
class InsertAfter:
    """Insert ``text`` after the (unique) ``anchor`` substring.

    Idempotent: skipped when ``text`` is already present in the file.
    """

    path: str
    anchor: str
    text: str
    description: str = ""


@dataclass(frozen=True)
class CopyFile:
    """Copy a file from this repository into the Chromium tree.

    ``src`` is relative to the study-ai-browser project root; ``dest`` is
    relative to the Chromium src/ root. Missing destination directories are
    created. Idempotent: skipped when the destination already has identical
    bytes.
    """

    src: str
    dest: str
    description: str = ""


@dataclass(frozen=True)
class CreateFile:
    """Create a new file in the Chromium tree.

    ``path`` is relative to the Chromium src/ root. Idempotent: skipped when
    the file already exists with identical content.
    """

    path: str
    content: str
    description: str = ""


def project_root() -> Path:
    """Absolute path of the study-ai-browser project root (this repo)."""
    return Path(__file__).resolve().parent.parent
