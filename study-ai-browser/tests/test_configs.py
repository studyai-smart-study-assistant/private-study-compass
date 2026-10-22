# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Validate project configuration files and cross-file consistency."""

import json
import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load(rel):
    return json.loads((PROJECT_ROOT / rel).read_text(encoding="utf-8"))


class PinConfigTest(unittest.TestCase):
    def setUp(self):
        self.pin = load("config/chromium_pin.json")

    def test_version_is_a_valid_chromium_tag(self):
        version = self.pin["chromium_version"]
        self.assertRegex(version, r"^\d+\.\d+\.\d+\.\d+$")

    def test_targets_build_the_public_apk(self):
        self.assertEqual(
            set(self.pin["targets"].values()), {"chrome_public_apk"})

    def test_source_is_real_chromium(self):
        self.assertEqual(
            self.pin["chromium_source_url"],
            "https://chromium.googlesource.com/chromium/src.git")


class GnArgsTest(unittest.TestCase):
    def parse(self, rel):
        args = {}
        for line in (PROJECT_ROOT / rel).read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            m = re.match(r"(\w+)\s*=\s*(.+)$", line)
            if m:
                args[m.group(1)] = m.group(2).strip().strip('"')
        return args

    def test_required_privacy_flags(self):
        for rel in ("config/gn_args/android_arm64.gni", "config/gn_args/android_arm.gni"):
            args = self.parse(rel)
            self.assertEqual(args["target_os"], "android")
            self.assertEqual(args["is_debug"], "false")
            self.assertEqual(args["is_chrome_branded"], "false",
                             msg=f"{rel}: branding off keeps telemetry off by default")
            self.assertEqual(args["use_official_google_api_keys"], "false",
                             msg=f"{rel}: no Google API keys embedded")
            self.assertEqual(args["disable_fieldtrial_testing_config"], "true")

    def test_package_matches_app_config(self):
        app_id = load("config/app_config.json")["application_id"]
        for rel in ("config/gn_args/android_arm64.gni", "config/gn_args/android_arm.gni"):
            self.assertEqual(self.parse(rel)["chrome_public_manifest_package"], app_id)

    def test_arm_files_differ_only_in_target_cpu(self):
        a = self.parse("config/gn_args/android_arm64.gni")
        b = self.parse("config/gn_args/android_arm.gni")
        self.assertEqual(a["target_cpu"], "arm64")
        self.assertEqual(b["target_cpu"], "arm")
        a.pop("target_cpu"), b.pop("target_cpu")
        self.assertEqual(a, b)


class BrandingConsistencyTest(unittest.TestCase):
    def test_patch_name_matches_app_config(self):
        app_name = load("config/app_config.json")["app_name"]
        patch = (PROJECT_ROOT / "patches/patch_01_branding.py").read_text()
        self.assertIn(f'APP_NAME = "{app_name}"', patch)

    def test_launcher_icons_exist_for_all_buckets(self):
        for dpi in ("mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"):
            path = PROJECT_ROOT / f"branding/icons/launcher-{dpi}.png"
            self.assertTrue(path.is_file(), msg=f"missing {dpi}")
            data = path.read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG"), msg=f"{path} not a PNG")


class NoSecretsTest(unittest.TestCase):
    def test_no_private_keys_anywhere_in_project(self):
        pattern = re.compile(
            r"BEGIN (RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY", re.MULTILINE)
        for path in PROJECT_ROOT.rglob("*"):
            if path.is_file() and path.suffix != ".png":
                try:
                    text = path.read_text(encoding="utf-8")
                except (UnicodeDecodeError, PermissionError):
                    continue
                self.assertIsNone(pattern.search(text), msg=f"key material in {path}")

    def test_scripts_only_reference_secret_env_vars(self):
        sign = (PROJECT_ROOT / "build/sign_release.sh").read_text()
        for var in ("STUDYAI_KEYSTORE_B64", "STUDYAI_KEYSTORE_PASSWORD",
                    "STUDYAI_KEY_ALIAS", "STUDYAI_KEY_PASSWORD"):
            self.assertIn(var, sign)


if __name__ == "__main__":
    unittest.main()
