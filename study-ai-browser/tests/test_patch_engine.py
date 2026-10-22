# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the patch engine (build/apply_patches.py)."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "build"))

import apply_patches  # noqa: E402
from patch_edits import (  # noqa: E402
    CopyFile,
    CreateFile,
    InsertAfter,
    Patch,
    RegexReplace,
    Replace,
)

PATCH = Patch(id="t", description="test", edits=())
APPLIED = apply_patches.STATUS_ALREADY_APPLIED
ERROR = apply_patches.STATUS_ERROR


class PatchEngineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="studyai-engine-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.tree = self.tmp / "src"
        self.tree.mkdir()

    def statuses(self, patch, check_only=False):
        results, ok = apply_patches.run(self.tree, PROJECT_ROOT, [patch],
                                        check_only=check_only)
        return results, ok

    def write(self, rel, content):
        path = self.tree / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # --- Replace ---------------------------------------------------------
    def test_replace_applies_once(self):
        self.write("f.txt", "alpha beta\nbeta alpha\n")
        patch = Patch(id="r", description="", edits=(
            Replace(path="f.txt", old="alpha beta", new="gamma beta"),))
        results, ok = self.statuses(patch)
        self.assertTrue(ok)
        self.assertEqual(results[0]["status"], "applied")
        self.assertEqual((self.tree / "f.txt").read_text(), "gamma beta\nbeta alpha\n")

    def test_replace_missing_context_fails(self):
        self.write("f.txt", "nothing matches\n")
        patch = Patch(id="r", description="", edits=(
            Replace(path="f.txt", old="absent", new="x"),))
        results, ok = self.statuses(patch)
        self.assertFalse(ok)
        self.assertEqual(results[0]["status"], ERROR)

    def test_replace_ambiguous_context_fails(self):
        self.write("f.txt", "dup\ndup\n")
        patch = Patch(id="r", description="", edits=(
            Replace(path="f.txt", old="dup", new="x"),))
        results, ok = self.statuses(patch)
        self.assertFalse(ok)
        self.assertIn("2 times", results[0]["detail"])

    def test_replace_idempotent(self):
        self.write("f.txt", "gamma beta\n")
        patch = Patch(id="r", description="", edits=(
            Replace(path="f.txt", old="alpha beta", new="gamma beta"),))
        results, ok = self.statuses(patch)
        self.assertTrue(ok)
        self.assertEqual(results[0]["status"], APPLIED)

    def test_replace_missing_file_fails_even_in_check_mode(self):
        patch = Patch(id="r", description="", edits=(
            Replace(path="nope.txt", old="a", new="b"),))
        results, ok = self.statuses(patch, check_only=True)
        self.assertFalse(ok)
        self.assertEqual(results[0]["status"], ERROR)

    # --- RegexReplace ----------------------------------------------------
    def test_regex_replace_and_idempotency(self):
        self.write("f.txt", "<message name=\"IDS_X\">Chrome</message>\n")
        patch = Patch(id="rr", description="", edits=(
            RegexReplace(path="f.txt", pattern=r'(name="IDS_X">)\s*Chrome\s*(</message>)',
                         replacement=r"\1Replaced\2",
                         applied_pattern=r'(name="IDS_X">)\s*Replaced\s*(</message>)'),))
        results, ok = self.statuses(patch)
        self.assertTrue(ok)
        self.assertEqual(results[0]["status"], "applied")
        self.assertIn("Replaced", (self.tree / "f.txt").read_text())
        results, ok = self.statuses(patch)
        self.assertTrue(ok)
        self.assertEqual(results[0]["status"], APPLIED)

    def test_regex_replace_no_match_fails(self):
        self.write("f.txt", "zzz\n")
        patch = Patch(id="rr", description="", edits=(
            RegexReplace(path="f.txt", pattern="Chrome", replacement="X"),))
        results, ok = self.statuses(patch)
        self.assertFalse(ok)

    # --- InsertAfter -----------------------------------------------------
    def test_insert_after(self):
        self.write("f.txt", '  "a",\n  "b",\n')
        patch = Patch(id="ia", description="", edits=(
            InsertAfter(path="f.txt", anchor='  "a",\n', text='  "c",\n'),))
        results, ok = self.statuses(patch)
        self.assertTrue(ok)
        self.assertEqual((self.tree / "f.txt").read_text(), '  "a",\n  "c",\n  "b",\n')

    def test_insert_after_idempotent_and_ambiguous(self):
        self.write("f.txt", '  "a",\n  "c",\n  "a",\n')
        patch = Patch(id="ia", description="", edits=(
            InsertAfter(path="f.txt", anchor='  "a",\n', text='  "c",\n'),))
        results, ok = self.statuses(patch)
        self.assertTrue(ok)
        self.assertEqual(results[0]["status"], APPLIED)

        self.write("g.txt", '  "a",\n  "a",\n')
        patch = Patch(id="ia2", description="", edits=(
            InsertAfter(path="g.txt", anchor='  "a",\n', text='  "z",\n'),))
        results, ok = self.statuses(patch)
        self.assertFalse(ok)

    # --- CopyFile / CreateFile -------------------------------------------
    def test_copy_file_creates_parents_and_idempotent(self):
        src = PROJECT_ROOT / "tests" / "fixtures" / "chromium-mock" / "chrome" / "android" / "BUILD.gn"
        patch = Patch(id="cf", description="", edits=(
            CopyFile(src=str(src.relative_to(PROJECT_ROOT)), dest="some/new/dir/out.gn"),))
        results, ok = self.statuses(patch)
        self.assertTrue(ok)
        dest = self.tree / "some" / "new" / "dir" / "out.gn"
        self.assertTrue(dest.is_file())
        results, ok = self.statuses(patch)
        self.assertTrue(ok)
        self.assertEqual(results[0]["status"], APPLIED)

    def test_copy_file_missing_source_fails_in_check_mode(self):
        patch = Patch(id="cf", description="", edits=(
            CopyFile(src="tests/fixtures/does-not-exist.bin", dest="x/y.bin"),))
        results, ok = self.statuses(patch, check_only=True)
        self.assertFalse(ok)

    def test_create_file_idempotent(self):
        patch = Patch(id="c", description="", edits=(
            CreateFile(path="new/file.txt", content="hello\n"),))
        results, ok = self.statuses(patch)
        self.assertTrue(ok)
        results, ok = self.statuses(patch)
        self.assertTrue(ok)
        self.assertEqual(results[0]["status"], APPLIED)

    # --- run() contract ---------------------------------------------------
    def test_unknown_edit_type_is_error(self):
        class Bogus:
            pass
        results, ok = apply_patches.run(self.tree, PROJECT_ROOT, [
            Patch(id="b", description="", edits=(Bogus(),))])
        self.assertFalse(ok)
        self.assertEqual(results[0]["status"], ERROR)

    def test_load_patches_discovers_modules(self):
        patches = apply_patches.load_patches(PROJECT_ROOT / "patches")
        self.assertEqual(len(patches), 4)
        ids = [p.id for p in patches]
        self.assertEqual(ids, ["branding", "search-provider", "privacy", "extension-points"])


if __name__ == "__main__":
    unittest.main()
