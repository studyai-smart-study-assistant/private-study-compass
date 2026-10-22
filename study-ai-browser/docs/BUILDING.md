# Building Study AI Browser

Study AI Browser is built **from real Chromium source code**. There is no
WebView wrapper and no prebuilt binary in this repository — the repository
contains the project configuration, patches, scripts, tests, and CI that
produce the APK from a pinned Chromium checkout.

## Pinned version

**Chromium 156.0.8078.47** (`config/chromium_pin.json`). Every patch context
in `patches/` was authored against this exact tag; CI validates the contexts
against the real checkout (`apply_patches.py --check`) before every build.

## Machine requirements

| Requirement | Minimum | Notes |
|---|---|---|
| Disk | ~300 GB free | full checkout (~100 GB) + object files + build output |
| RAM | 64 GB | linking is the bottleneck; 32 GB works with slower lld settings but is painful |
| CPU | 16+ cores | a full first build takes several hours even on 32 cores |
| OS | Ubuntu 22.04/24.04 | Debian 12 also works |
| Network | unrestricted | fetch downloads ~50 GB of dependencies |

Run `build/verify_environment.sh` to check a machine.

## One-time setup

```bash
sudo apt-get update
sudo apt-get install -y git python3 curl openjdk-17-jdk lsb-release

git clone https://github.com/<you>/study-ai-browser.git   # or your fork
cd study-ai-browser

./build/verify_environment.sh
./build/fetch_chromium.sh        # depot_tools + 100+ GB checkout + patches + SDK/NDK
```

`fetch_chromium.sh` does, in order:

1. clones `depot_tools` into the build parent directory,
2. runs `fetch --nohooks chromium` (multi-hour, 100+ GB),
3. checks out the pinned tag,
4. runs `gclient sync -D` and `gclient runhooks` (downloads the Android
   SDK/NDK and Clang toolchain),
5. validates all patch contexts against the real tree (`apply_patches.py
   --check`) and then applies them.

By default the checkout lands in `../chromium-build/src` relative to this
project; override with `CHROMIUM_BUILD_DIR=/path`.

## Building

```bash
./build/build_android.sh "$(dirname "$PWD")/chromium-build" arm64
# or "arm" for 32-bit ARM
```

Output: `chromium-build/src/out/studyai-android-arm64/apks/StudyAIBrowser-arm64.apk`
plus a `.mapping` file for release builds (R8 obfuscation map).

## Signing

`build/sign_release.sh` signs with `apksigner` using credentials supplied via
environment variables (`STUDYAI_KEYSTORE_B64`, `STUDYAI_KEYSTORE_PASSWORD`,
`STUDYAI_KEY_ALIAS`, `STUDYAI_KEY_PASSWORD`). In CI these map to GitHub
Actions secrets — **signing material must never be committed**. Generate a
keystore once:

```bash
keytool -genkeypair -v -keystore studyai-release.jks \
  -alias studyai -keyalg RSA -keysize 4096 -validity 10000
base64 -w0 studyai-release.jks   # value for STUDYAI_KEYSTORE_B64
```

Store the base64 blob and passwords as repository secrets; see
`docs/CI_CD.md`. Keep an offline backup — a lost keystore cannot be recovered,
and Android will treat a re-signed app as a different application.

## GN arguments

`config/gn_args/android_arm64.gni` / `android_arm.gni` define the release
build: non-branded (`is_chrome_branded=false`), no Google API keys
(`use_official_google_api_keys=false`), app id `com.studyai.browser`, and
privacy hardening flags. Consequences of no API keys: UMA and crash-upload
are compiled out/disabled, and Google sign-in / Cast Google services degrade.
See `docs/PRIVACY.md`.

## Update strategy (new Chromium version)

1. Pick the target version (stable channel).
2. Update `config/chromium_pin.json`.
3. Run `./build/fetch_chromium.sh` — its built-in `--check` step reports
   exactly which patch contexts no longer match.
4. Update the affected `patches/patch_*.py` entries for the new file content,
   re-run `tests/run_tests.sh` (add/refresh mock fixtures), then build.
5. Test on a device: tabs, history, bookmarks, downloads, incognito, clear
   browsing data, search from the omnibox, and backup behaviour.

## Troubleshooting

* `apply_patches.py` reports "context not found" → the pinned Chromium changed
  the target file; update the patch (do not weaken the engine's uniqueness
  checks).
* OOM during linking → reduce parallelism (`autoninja -j N`), or add swap;
  do not drop below 32 GB.
* `gclient sync` SDK failures → delete the `src/third_party/android_sdk`
  directory and re-run `gclient runhooks`.
