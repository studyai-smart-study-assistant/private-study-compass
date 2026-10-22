# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Apply every project patch to the mock Chromium tree and assert outcomes.

The mock tree mirrors the exact fragments of Chromium 156.0.8078.47 that the
patches match against (contexts were captured from the pinned tag). CI
additionally runs `apply_patches.py --check` against a real checkout before
building.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "build"))

import apply_patches  # noqa: E402

FIXTURES = PROJECT_ROOT / "tests" / "fixtures" / "chromium-mock"
APP_NAME = "Study AI Browser"


def apply_all(tree: Path):
    patches = apply_patches.load_patches(PROJECT_ROOT / "patches")
    results, ok = apply_patches.run(tree, PROJECT_ROOT, patches)
    return results, ok


class PatchesOnFixturesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="studyai-fixtures-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.tree = self.tmp / "src"
        shutil.copytree(FIXTURES, self.tree)

    def read(self, rel):
        return (self.tree / rel).read_text(encoding="utf-8")

    def test_all_patches_apply_cleanly(self):
        results, ok = apply_all(self.tree)
        self.assertTrue(ok, msg=str(results))
        self.assertTrue(all(r["status"] == "applied" for r in results))

    def test_second_run_is_idempotent(self):
        apply_all(self.tree)
        results, ok = apply_all(self.tree)
        self.assertTrue(ok, msg=str(results))
        self.assertFalse(any(r["status"] == "error" for r in results))

    def test_branding_label_and_app_name(self):
        apply_all(self.tree)
        manifest = self.read("chrome/android/java/AndroidManifest.xml")
        self.assertIn(
            f'android:label="{{% block application_label %}}{APP_NAME}{{% endblock %}}"',
            manifest)
        grd = self.read("chrome/android/java/strings/android_chrome_strings.grd")
        self.assertRegex(grd, r'name="IDS_APP_NAME"[^>]*>\s*' + APP_NAME)
        self.assertNotRegex(grd, r'name="IDS_APP_NAME"[^>]*>\s*Chrome')

    def test_branding_icons_installed(self):
        apply_all(self.tree)
        for dpi in ("mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"):
            dest = self.tree / f"chrome/android/java/res/drawable-{dpi}/ic_launcher.png"
            self.assertTrue(dest.is_file(), msg=f"missing launcher icon for {dpi}")
            src = PROJECT_ROOT / f"branding/icons/launcher-{dpi}.png"
            self.assertEqual(dest.read_bytes(), src.read_bytes())

    def test_search_provider_fallback_is_duckduckgo(self):
        apply_all(self.tree)
        cc = self.read("components/search_engines/template_url_prepopulate_data.cc")
        self.assertIn("duckduckgo.id", cc)
        self.assertNotIn("google.id,", cc)

    def test_backup_disabled_even_with_backup_key(self):
        apply_all(self.tree)
        manifest = self.read("chrome/android/java/AndroidManifest.xml")
        self.assertNotIn('android:allowBackup="true"', manifest)
        self.assertEqual(manifest.count('android:allowBackup="false"'), 2)

    def test_extension_point_wired_into_chrome_java(self):
        apply_all(self.tree)
        build_gn = self.read("chrome/android/BUILD.gn")
        self.assertIn('"//study_ai/browser:java",', build_gn)
        bridge = self.tree / "study_ai/browser/java/org/studyai/browser/StudyAiAgentBridge.java"
        registry = self.tree / "study_ai/browser/java/org/studyai/browser/StudyAiBridgeRegistry.java"
        gn = self.tree / "study_ai/browser/BUILD.gn"
        self.assertTrue(bridge.is_file())
        self.assertTrue(registry.is_file())
        self.assertTrue(gn.is_file())
        # Bridge sources must not embed secrets or network code.
        for path in (bridge, registry):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("http", text.lower().replace("http", "http"), msg=path.name)
            for forbidden in ("ApiKey", "api_key", "Bearer", "password", "secret"):
                self.assertNotIn(forbidden, text, msg=path.name)


if __name__ == "__main__":
    unittest.main()
