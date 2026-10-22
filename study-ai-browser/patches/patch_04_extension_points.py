# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Extension-point patch: add the //study_ai/browser Java bridge to chrome_java.

Context verified against Chromium 156.0.8078.47 (chrome/android/BUILD.gn,
android_library("chrome_java") deps list): the two-line anchor below sits
inside the chrome_java deps. The bridge target is added there so future Study
AI capabilities (AI API, MCP browser agent) can hook in without touching
Chromium internals again.

The bridge itself is pure plumbing: an interface + registry with NO network
code and NO embedded API secrets, per the PRD. Real AI capabilities arrive in
a later phase and must obtain credentials server-side at runtime, never from
the app package.
"""

from patch_edits import CopyFile, InsertAfter, Patch

CHROME_JAVA_DEPS_ANCHOR = (
    '      "//chrome/browser/accessibility/hierarchysnapshotter/android:java",\n'
    '      "//chrome/browser/android/browserservices/intents:java",\n'
)

PATCH = Patch(
    id="extension-points",
    description="Add //study_ai/browser bridge sources to chrome_java",
    edits=(
        CopyFile(
            src="src-custom/study_ai/browser/BUILD.gn",
            dest="study_ai/browser/BUILD.gn",
            description="Build target for the Study AI bridge",
        ),
        CopyFile(
            src="src-custom/study_ai/browser/java/org/studyai/browser/StudyAiAgentBridge.java",
            dest="study_ai/browser/java/org/studyai/browser/StudyAiAgentBridge.java",
            description="Bridge interface (extension point, no fake agent)",
        ),
        CopyFile(
            src="src-custom/study_ai/browser/java/org/studyai/browser/StudyAiBridgeRegistry.java",
            dest="study_ai/browser/java/org/studyai/browser/StudyAiBridgeRegistry.java",
            description="Thread-safe bridge registry/dispatcher",
        ),
        InsertAfter(
            path="chrome/android/BUILD.gn",
            anchor=CHROME_JAVA_DEPS_ANCHOR,
            text='      "//study_ai/browser:java",\n',
            description="Add bridge target to chrome_java dependencies",
        ),
    ),
)
