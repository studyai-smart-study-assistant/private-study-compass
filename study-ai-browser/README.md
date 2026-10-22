# Study AI Browser

A privacy-first Android browser built on **real Chromium source code** — not
an Android WebView wrapper. This repository contains the complete project:
Chromium pin, customization patches, build scripts, tests, docs, and GitHub
Actions CI/CD that produce the signed APK.

- **Pinned engine:** Chromium 156.0.8078.47 (`config/chromium_pin.json`)
- **App identity:** Study AI Browser, `com.studyai.browser`
- **What you get:** tabs, back/forward/reload, bookmarks, history, downloads,
  settings, incognito, clear-browsing-data, omnibox URL/search detection with
  a configurable external search provider (default fallback: DuckDuckGo —
  see docs/SEARCH_PROVIDERS.md)
- **Privacy-first, local-only profile data:** history, bookmarks, tabs,
  cookies and passwords stay in on-device app storage; Android cloud backup
  is disabled at the manifest level; the build ships with no Google API keys,
  no UMA/crash upload, and no analytics of any kind (docs/PRIVACY.md)
- **Modular AI readiness:** an inert `//study_ai/browser` bridge interface
  and registry are compiled in, reserved for Study AI's future AI API and
  MCP-powered browser agent. No fake agent, no embedded API secrets.
- **CI/CD:** hosted-runner verification on every change; the APK is built on
  a **GitHub-hosted larger runner** (no self-hosted hardware) and published
  directly as a GitHub Release asset — signed with credentials held only in
  GitHub Actions secrets, and only after build + signature verification pass.

## Repository map

```
study-ai-browser/
├── config/          Chromium pin, GN args (arm64/arm), app identity
├── patches/         Declarative patches + patch engine (build/apply_patches.py)
├── src-custom/      Java extension-point sources (//study_ai/browser)
├── build/           verify_environment.sh, fetch_chromium.sh,
│                    build_android.sh, sign_release.sh
├── tests/           Test suite (40 tests) + mock Chromium fixtures
├── branding/        App icon assets (launcher + adaptive)
└── docs/            BUILDING, PRIVACY, SEARCH_PROVIDERS, CI_CD, ARCHITECTURE
.github/workflows/   study-ai-browser-verify.yml, study-ai-browser-build-apk.yml
```

## Quick start

```bash
cd study-ai-browser
./tests/run_tests.sh                       # verify the project itself (no Chromium needed)

./build/verify_environment.sh              # check a build machine
./build/fetch_chromium.sh                  # depot_tools + pinned Chromium + patches (~300 GB, hours)
./build/build_android.sh "$(dirname "$PWD")/chromium-build" arm64
./build/sign_release.sh in.apk out.apk     # credentials via env vars only
```

**Prerequisites:** Linux x86-64, ~300 GB free disk, 64 GB RAM, 16+ cores,
JDK 17, git/python3/curl. Full details and troubleshooting: `docs/BUILDING.md`.
An APK is produced only by the build pipeline — nothing in this repository
claims to ship one without it.

## Documentation

| Document | Contents |
|---|---|
| docs/BUILDING.md | prerequisites, fetch/build/sign commands, GN args, update strategy, troubleshooting |
| docs/PRIVACY.md | local-only data guarantees, telemetry posture, documented network requests, audit checklist |
| docs/SEARCH_PROVIDERS.md | default and configurable providers; what the provider receives |
| docs/CI_CD.md | hosted verify workflow, GitHub-hosted larger-runner build, costs, release publishing, secrets, runbook |
| docs/ARCHITECTURE.md | patch system, feature map, AI/MCP extension points and phase-2 rules |

## Licensing

The browser engine is Chromium, Copyright The Chromium Authors, licensed
under the BSD 3-Clause license — see `LICENSE.md`. The pinned source tree
carries Chromium's `LICENSE` file and third-party notices; they are preserved
unmodified by the patch system (patches never touch license files), and
`THIRD_PARTY_NOTICES.md` documents the obligations that flow through to
distributed APKs. Study AI Browser's own additions (this repository's
original content) are distributed under Apache 2.0.

## Security updates

Chromium releases move fast; the update strategy in docs/BUILDING.md pins a
stable tag, and `fetch_chromium.sh` re-validates every patch context against
the new tree, reporting exactly what needs updating. Track the Chromium
stable channel and re-pin regularly so engine security fixes reach users.
