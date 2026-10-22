# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Branding patch: Study AI Browser name and launcher icons.

Contexts verified against Chromium 156.0.8078.47:
  * chrome/android/java/AndroidManifest.xml — application_label block
    (line: android:label="{% block application_label %}@string/app_name{% endblock %}")
  * chrome/android/java/res/drawable-*/ic_launcher.png referenced by the
    manifest as android:icon="@drawable/ic_launcher"
  * chrome/android/java/strings/android_chrome_strings.grd IDS_APP_NAME
    message is validated in CI by `apply_patches.py --check` against the
    pinned checkout; the regex covers attribute-order variations.
"""

from patch_edits import CopyFile, Patch, RegexReplace, Replace

APP_NAME = "Study AI Browser"

LAUNCHER_ICON_COPIES = tuple(
    CopyFile(
        src=f"branding/icons/launcher-{dpi}.png",
        dest=f"chrome/android/java/res/drawable-{dpi}/ic_launcher.png",
        description=f"Launcher icon for {dpi}",
    )
    for dpi in ("mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi")
)

PATCH = Patch(
    id="branding",
    description=f"Brand the browser as '{APP_NAME}' and install launcher icons",
    edits=(
        Replace(
            path="chrome/android/java/AndroidManifest.xml",
            old='android:label="{% block application_label %}@string/app_name{% endblock %}"',
            new=f'android:label="{{% block application_label %}}{APP_NAME}{{% endblock %}}"',
            description="Set the application label shown by Android",
        ),
        RegexReplace(
            path="chrome/android/java/strings/android_chrome_strings.grd",
            pattern=r'(<message\s+name="IDS_APP_NAME"[^>]*>)\s*Chrome\s*(</message>)',
            replacement=r"\g<1>" + APP_NAME + r"\g<2>",
            applied_pattern=(
                r'(<message\s+name="IDS_APP_NAME"[^>]*>)\s*'
                + APP_NAME
                + r"\s*(</message>)"
            ),
            description="Non-translatable in-app application name string",
        ),
    )
    + LAUNCHER_ICON_COPIES,
)
