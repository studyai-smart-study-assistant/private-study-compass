# CI/CD

Two workflows live at the repository root (path-filtered to `study-ai-browser/`):

## 1. `study-ai-browser-verify.yml` — hosted runner (free)

Runs on every push/PR touching the project:

* full test suite (`tests/run_tests.sh`): patch-engine unit tests, all patches
  applied to the mock Chromium tree, config/consistency validation,
  workflow validation;
* `bash -n` syntax check of all build scripts;
* confirmation that the pinned Chromium tag exists upstream;
* repository-wide scan for private-key material.

## 2. `study-ai-browser-build-apk.yml` — self-hosted runner (produces the APK)

A real Chromium build **cannot** run on standard hosted runners (100+ GB
checkout, 64+ GB RAM, multi-hour builds). This workflow targets a self-hosted
Linux runner labelled `[self-hosted, linux, chromium]` and is triggered
manually (`workflow_dispatch`).

### Provisioning a runner (one-time)

1. Create a Linux machine meeting `docs/BUILDING.md` requirements
   (e.g. 32 cores, 64 GB RAM, 300 GB SSD).
2. Install the GitHub Actions runner per GitHub's docs and register it to
   this repository with the labels `self-hosted`, `linux`, `chromium`.
3. As the runner user: `sudo apt-get install -y git python3 curl
   openjdk-17-jdk lsb-release`.
4. Run `study-ai-browser/build/verify_environment.sh` to confirm readiness.
5. Recommended: pre-warm the source once (`./build/fetch_chromium.sh`) so the
   first CI build only compiles — subsequent runs reuse the checkout and are
   incremental.

### Secrets (Repository → Settings → Secrets and variables → Actions)

| Secret | Contents |
|---|---|
| `STUDYAI_KEYSTORE_B64` | release keystore, base64-encoded |
| `STUDYAI_KEYSTORE_PASSWORD` | keystore password |
| `STUDYAI_KEY_ALIAS` | signing key alias |
| `STUDYAI_KEY_PASSWORD` | key password (optional; defaults to keystore password) |

Credentials exist **only** as Actions secrets — never in the repo (the verify
workflow scans for violations). Without secrets the workflow still uploads a
clearly-named **unsigned** APK for testing.

### Artifacts

Each run uploads `StudyAIBrowser-<arch>-apk` (signed or unsigned APK) and, if
produced, the R8 `mapping` file. Verify a signed APK on-device before release:

```bash
apksigner verify --print-certs StudyAIBrowser-arm64.apk
```

### Runbook: cutting a release

1. Confirm the verify workflow is green.
2. Run the build workflow for `arm64` (and `arm` if needed).
3. Download the artifacts, verify signatures, install on a test device.
4. Exercise: omnibox URL/search detection, tabs, back/forward/reload,
   bookmarks, history, downloads, settings, incognito, clear browsing data.
5. Tag the repository; attach the APKs to the GitHub release.
