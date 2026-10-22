# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Privacy patch: keep browser profile data out of Android backups.

Context verified against Chromium 156.0.8078.47
(chrome/android/java/AndroidManifest.xml): when the `backup_key` build variable
is defined the manifest sets android:allowBackup="true" with a backup agent.
We force allowBackup="false" in that branch as well, so profile data (history,
bookmarks, tabs, cookies, passwords) can never leave the device through the
Android backup transport — see docs/PRIVACY.md.

Telemetry/reporting is handled at build level, not by a patch: Study AI Browser
builds non-branded (is_chrome_branded=false), which keeps UMA metrics and crash
report upload disabled by default. GN args additionally disable the field-trial
testing config. See config/gn_args/*.gni and docs/PRIVACY.md.
"""

from patch_edits import Patch, Replace

PATCH = Patch(
    id="privacy",
    description="Disable Android cloud backup of browser profile data",
    edits=(
        Replace(
            path="chrome/android/java/AndroidManifest.xml",
            old=(
                "        {% if backup_key is defined %}\n"
                '        android:allowBackup="true"\n'
            ),
            new=(
                "        {% if backup_key is defined %}\n"
                '        android:allowBackup="false"\n'
            ),
            description=(
                "Force allowBackup=false even when a backup_key is present so "
                "no browser profile data is included in Android backups"
            ),
        ),
    ),
)
