# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Validate the GitHub Actions workflows.

If PyYAML is available the files are parsed as YAML; otherwise structural
checks run on the raw text. PyYAML is not a project dependency — CI installs
it in the verify workflow, and parsing is a best-effort extra here.
"""

import re
import unittest
from pathlib import Path

try:
    import yaml  # type: ignore
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

ROOT = Path(__file__).resolve().parent.parent.parent  # repository root
VERIFY = ROOT / ".github/workflows/study-ai-browser-verify.yml"
BUILD = ROOT / ".github/workflows/study-ai-browser-build-apk.yml"


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class YamlParsingTest(unittest.TestCase):
    def test_verify_workflow_parses(self):
        doc = yaml.safe_load(VERIFY.read_text())
        self.assertIn("on", doc or {})
        self.assertIn("jobs", doc)

    def test_build_workflow_parses(self):
        doc = yaml.safe_load(BUILD.read_text())
        self.assertIn("jobs", doc)
        self.assertIn("build", doc["jobs"])


class VerifyWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.text = VERIFY.read_text()

    def test_runs_on_hosted_runner(self):
        self.assertIn("ubuntu-24.04", self.text)

    def test_only_triggers_on_browser_project_changes(self):
        self.assertIn("study-ai-browser/**", self.text)

    def test_runs_tests_and_leak_scan(self):
        self.assertIn("run_tests.sh", self.text)
        self.assertIn("PRIVATE KEY", self.text)


class BuildWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.text = BUILD.read_text()

    def test_targets_self_hosted_runner_with_chromium_label(self):
        self.assertIn("self-hosted", self.text)
        self.assertIn("chromium", self.text)

    def test_signing_uses_only_github_secrets(self):
        for secret in ("secrets.STUDYAI_KEYSTORE_B64", "secrets.STUDYAI_KEYSTORE_PASSWORD",
                       "secrets.STUDYAI_KEY_ALIAS", "secrets.STUDYAI_KEY_PASSWORD"):
            self.assertIn(secret, self.text)
        # No literal credential material may appear in the workflow.
        self.assertNotRegex(self.text, r"keystore-.*==")

    def test_uploads_apk_artifact(self):
        self.assertIn("upload-artifact", self.text)
        self.assertIn("StudyAIBrowser-", self.text)

    def test_both_architectures_built(self):
        self.assertIn("arm64", self.text)
        self.assertIn("arm", self.text)


if __name__ == "__main__":
    unittest.main()
