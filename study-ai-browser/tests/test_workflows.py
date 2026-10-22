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
    @staticmethod
    def _triggers(doc):
        # YAML 1.1 parses an unquoted `on:` key as boolean True; accept both.
        return doc.get("on", doc.get(True))

    def test_verify_workflow_parses(self):
        doc = yaml.safe_load(VERIFY.read_text())
        self.assertTrue(self._triggers(doc))
        self.assertIn("jobs", doc)

    def test_build_workflow_parses(self):
        doc = yaml.safe_load(BUILD.read_text())
        triggers = self._triggers(doc) or {}
        self.assertIn("workflow_dispatch", triggers)
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

    def test_targets_github_hosted_larger_runner(self):
        # The workflow must select the runner via the dispatch input and must
        # not reference any self-hosted runner label anywhere.
        self.assertIn("runs-on: ${{ inputs.runner_label }}", self.text)
        self.assertIn("larger runner", self.text)
        self.assertNotIn("self-hosted", self.text)

    def test_signing_uses_only_github_secrets(self):
        for secret in ("secrets.STUDYAI_KEYSTORE_B64", "secrets.STUDYAI_KEYSTORE_PASSWORD",
                       "secrets.STUDYAI_KEY_ALIAS", "secrets.STUDYAI_KEY_PASSWORD"):
            self.assertIn(secret, self.text)
        # No literal credential material may appear in the workflow.
        self.assertNotRegex(self.text, r"keystore-.*==")

    def test_no_actions_artifact_uploads(self):
        # Artifact storage is not used: quota-safe by design.
        self.assertNotIn("upload-artifact", self.text)

    def test_publishes_release_assets_with_scoped_github_token(self):
        self.assertIn("gh release create", self.text)
        self.assertIn("GH_TOKEN: ${{ github.token }}", self.text)
        self.assertIn("contents: write", self.text)

    def test_release_only_after_build_sign_and_verify(self):
        # The publish step must come after build/sign/verify and must not be
        # forced to run when the job fails.
        sign_pos = self.text.index("Sign release APK")
        verify_pos = self.text.index("Verify APK signature")
        publish_pos = self.text.index("Publish APK as a GitHub Release asset")
        self.assertLess(verify_pos, publish_pos)
        self.assertLess(sign_pos, publish_pos)
        publish_block = self.text[publish_pos:publish_pos + 400]
        self.assertNotIn("if: always()", publish_block)
        self.assertNotIn("continue-on-error", publish_block)

    def test_both_architectures_selectable(self):
        self.assertIn("arm64", self.text)
        self.assertIn("arm", self.text)


if __name__ == "__main__":
    unittest.main()
