#!/usr/bin/env python3
# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Apply Study AI Browser customizations to a Chromium checkout.

Usage:
  apply_patches.py --chromium /path/to/chromium/src [--check] [--dry-run] [--json]
                   [--only PATCH_ID ...] [--patches-dir DIR]

Patch modules are discovered in ``patches/patch_*.py`` (sorted by filename so
that the numeric prefix defines application order). Each module must expose
``PATCH: patch_edits.Patch``.

Behaviour contract:
  * Every context-bearing edit must match exactly once. A missing or ambiguous
    context is a hard error and makes the whole run exit non-zero.
  * Edits are idempotent: re-running on an already-patched tree reports each
    edit as "already-applied" or "skipped" instead of failing.
  * ``--check`` performs full validation (including CopyFile source existence
    and destination directory sanity) without writing anything. CI runs this
    against the pinned checkout before building.
  * Nothing is ever silently ignored: every edit produces a per-edit status.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from patch_edits import (  # noqa: E402
    CopyFile,
    CreateFile,
    InsertAfter,
    Patch,
    RegexReplace,
    Replace,
    project_root,
)

DEFAULT_PATCHES_DIR = Path(__file__).resolve().parent.parent / "patches"

STATUS_APPLIED = "applied"
STATUS_ALREADY_APPLIED = "already-applied"
STATUS_SKIPPED = "skipped"
STATUS_ERROR = "error"


def load_patches(patches_dir: Path) -> list[Patch]:
    """Import every patch module and collect its PATCH definition."""
    if not patches_dir.is_dir():
        raise FileNotFoundError(f"patches directory not found: {patches_dir}")
    modules = sorted(patches_dir.glob("patch_*.py"))
    if not modules:
        raise RuntimeError(f"no patch modules found in {patches_dir}")
    patches: list[Patch] = []
    for module_path in modules:
        name = f"studyai_patch_{module_path.stem}"
        spec = importlib.util.spec_from_file_location(name, module_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        patch = getattr(module, "PATCH", None)
        if not isinstance(patch, Patch):
            raise RuntimeError(f"{module_path} does not define a Patch named PATCH")
        patches.append(patch)
    return patches


def _read(tree: Path, rel: str) -> str:
    path = tree / rel
    if not path.is_file():
        raise FileNotFoundError(f"expected file missing in checkout: {rel}")
    return path.read_text(encoding="utf-8")


def _write(tree: Path, rel: str, content: str) -> None:
    path = tree / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _check_edit_writable(edit, tree: Path, repo: Path, errors: list[str]) -> None:
    """Static validation that does not need file content matching."""
    if isinstance(edit, CopyFile):
        src = repo / edit.src
        if not src.is_file():
            errors.append(f"CopyFile source missing: {edit.src}")
    if isinstance(edit, (Replace, RegexReplace, InsertAfter)):
        if not (tree / edit.path).is_file():
            errors.append(f"target file missing in checkout: {edit.path}")


def _apply_edit(edit, tree: Path, repo: Path) -> tuple[str, str | None]:
    """Apply one edit. Returns (status, error_detail)."""
    if isinstance(edit, Replace):
        text = _read(tree, edit.path)
        if edit.old not in text:
            if edit.new in text:
                return STATUS_ALREADY_APPLIED, None
            return STATUS_ERROR, f"context not found in {edit.path}"
        if text.count(edit.old) != 1:
            return STATUS_ERROR, (
                f"context occurs {text.count(edit.old)} times in {edit.path}, expected 1"
            )
        _write(tree, edit.path, text.replace(edit.old, edit.new, 1))
        return STATUS_APPLIED, None

    if isinstance(edit, RegexReplace):
        text = _read(tree, edit.path)
        pattern = re.compile(edit.pattern, re.DOTALL)
        matches = pattern.findall(text)
        if len(matches) < edit.expected_matches:
            if edit.applied_pattern and re.search(edit.applied_pattern, text, re.DOTALL):
                return STATUS_ALREADY_APPLIED, None
            return STATUS_ERROR, (
                f"regex matched {len(matches)} times in {edit.path}, "
                f"expected >= {edit.expected_matches}"
            )
        new_text, count = pattern.subn(edit.replacement, text, count=edit.expected_matches)
        _write(tree, edit.path, new_text)
        return STATUS_APPLIED, None

    if isinstance(edit, InsertAfter):
        text = _read(tree, edit.path)
        if edit.text.strip() and edit.text.strip() in text:
            return STATUS_ALREADY_APPLIED, None
        if text.count(edit.anchor) != 1:
            return STATUS_ERROR, (
                f"anchor occurs {text.count(edit.anchor)} times in {edit.path}, expected 1"
            )
        idx = text.index(edit.anchor) + len(edit.anchor)
        _write(tree, edit.path, text[:idx] + edit.text + text[idx:])
        return STATUS_APPLIED, None

    if isinstance(edit, CopyFile):
        src = repo / edit.src
        dest = tree / edit.dest
        if dest.is_file() and dest.read_bytes() == src.read_bytes():
            return STATUS_ALREADY_APPLIED, None
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(src.read_bytes())
        return STATUS_APPLIED, None

    if isinstance(edit, CreateFile):
        dest = tree / edit.path
        if dest.is_file() and dest.read_text(encoding="utf-8") == edit.content:
            return STATUS_ALREADY_APPLIED, None
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(edit.content, encoding="utf-8")
        return STATUS_APPLIED, None

    return STATUS_ERROR, f"unknown edit type: {type(edit).__name__}"


def run(
    tree: Path,
    repo: Path,
    patches: list[Patch],
    check_only: bool = False,
    dry_run: bool = False,
    only_ids: set[str] | None = None,
) -> tuple[list[dict], bool]:
    """Apply (or validate) patches. Returns (results, ok)."""
    results: list[dict] = []
    ok = True

    for patch in patches:
        if only_ids and patch.id not in only_ids:
            continue
        errors: list[str] = []
        for edit in patch.edits:
            _check_edit_writable(edit, tree, repo, errors)
        if errors:
            for err in errors:
                results.append(
                    {"patch": patch.id, "edit": type(edit).__name__, "status": STATUS_ERROR,
                     "detail": err}
                )
            ok = False
            continue

        for edit in patch.edits:
            if check_only:
                # Full context validation without writing.
                status, detail = STATUS_APPLIED, None
                try:
                    if isinstance(edit, Replace):
                        text = _read(tree, edit.path)
                        count = text.count(edit.old)
                        if count != 1 and not (count == 0 and edit.new in text):
                            status, detail = STATUS_ERROR, (
                                f"context occurs {count} times, expected 1"
                            )
                    elif isinstance(edit, RegexReplace):
                        text = _read(tree, edit.path)
                        matches = re.findall(edit.pattern, text, re.DOTALL)
                        if len(matches) < edit.expected_matches and not (
                            edit.applied_pattern and re.search(edit.applied_pattern, text, re.DOTALL)
                        ):
                            status, detail = STATUS_ERROR, (
                                f"regex matched {len(matches)} times, expected >= {edit.expected_matches}"
                            )
                    elif isinstance(edit, InsertAfter):
                        text = _read(tree, edit.path)
                        if text.count(edit.anchor) != 1 and edit.text.strip() not in text:
                            status, detail = STATUS_ERROR, (
                                f"anchor occurs {text.count(edit.anchor)} times, expected 1"
                            )
                except FileNotFoundError as exc:
                    status, detail = STATUS_ERROR, str(exc)
                if detail:
                    ok = False
                results.append(
                    {"patch": patch.id, "edit": type(edit).__name__, "status": status,
                     "detail": detail}
                )
                continue

            if dry_run:
                results.append(
                    {"patch": patch.id, "edit": type(edit).__name__, "status": STATUS_SKIPPED,
                     "detail": "dry-run"}
                )
                continue

            try:
                status, detail = _apply_edit(edit, tree, repo)
            except FileNotFoundError as exc:
                status, detail = STATUS_ERROR, str(exc)
            if status == STATUS_ERROR:
                ok = False
            results.append(
                {"patch": patch.id, "edit": type(edit).__name__, "status": status,
                 "detail": detail}
            )
    return results, ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chromium", type=Path, help="Path to the Chromium src/ checkout")
    parser.add_argument("--patches-dir", type=Path, default=DEFAULT_PATCHES_DIR)
    parser.add_argument("--check", action="store_true",
                        help="Validate all contexts without writing anything")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be done without writing anything")
    parser.add_argument("--only", nargs="*", default=None, help="Apply only these patch ids")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    if not args.chromium:
        parser.error("--chromium is required")

    tree = args.chromium.resolve()
    if not tree.is_dir():
        parser.error(f"Chromium checkout not found: {tree}")

    patches = load_patches(args.patches_dir.resolve())
    results, ok = run(tree, project_root(), patches,
                      check_only=args.check, dry_run=args.dry_run,
                      only_ids=set(args.only) if args.only else None)

    errors = [r for r in results if r["status"] == STATUS_ERROR]
    if args.json:
        print(json.dumps({"ok": ok, "results": results}, indent=2))
    else:
        for r in results:
            line = f"[{r['status']}] {r['patch']} :: {r['edit']}"
            if r.get("detail"):
                line += f" — {r['detail']}"
            print(line)
        print(f"\n{len(results)} edits, {len(errors)} errors")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
