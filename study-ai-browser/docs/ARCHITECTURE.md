# Architecture

```
                        GitHub repository (this code)
┌──────────────────────────────────────────────────────────────────┐
│ config/     Chromium pin (156.0.8078.47), GN args, app identity  │
│ patches/    Declarative patches applied to the Chromium tree     │
│             (patch engine: build/apply_patches.py)               │
│ src-custom/ Java sources copied in as //study_ai/browser         │
│ build/      fetch / build / sign / verify scripts                │
│ tests/      Patch-engine + patch + config + workflow tests       │
│ branding/   App name, launcher icons, adaptive icon assets       │
│ docs/       Building, privacy, search, CI, this file             │
└──────────────────────────────────────────────────────────────────┘
                                   │  fetch_chromium.sh
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│ Chromium checkout (src/) + applied patches                       │
│   chrome_public_apk  →  StudyAIBrowser-<arch>.apk                │
└──────────────────────────────────────────────────────────────────┘
```

## Why patches instead of a fork dump

The project pins Chromium and carries a small, reviewed set of customizations
applied by `build/apply_patches.py`. This is the pattern used by established
Chromium-based browsers: the engine comes from upstream unmodified, our
changes are explicit, versioned, testable in isolation (`tests/run_tests.sh`
runs them against mock fragments of the pinned sources), and CI verifies each
context against the real tree before building. A patch that no longer matches
fails the build loudly instead of silently degrading.

## What the patches do today

| Patch | Purpose |
|---|---|
| `patch_01_branding` | app name ("Study AI Browser") in manifest + strings, launcher icons in all density buckets |
| `patch_02_search_provider` | default fallback search engine → DuckDuckGo (user-configurable in settings) |
| `patch_03_privacy` | force `android:allowBackup="false"` so profile data never leaves via Android backup |
| `patch_04_extension_points` | adds `//study_ai/browser` (bridge interface + registry) and wires it into `chrome_java` |

Package identity comes from GN args (`chrome_public_manifest_package =
com.studyai.browser`), not a patch — one file to change, validated by tests.

## Features shipped by stock Chromium (no patching needed)

Tabs, back/forward/reload, bookmarks, browsing history, downloads, settings,
incognito, clear-browsing-data, omnibox URL/query detection — the
`chrome_public_apk` target provides all of them; the PRD's browser behaviour
is inherited from the real engine.

## Reserved extension points (Phase 2: AI API + MCP browser agent)

`//study_ai/browser` ships two classes, deliberately inert:

* `StudyAiAgentBridge` — command interface (`id()`, `onCommand(command, payloadJson)`).
* `StudyAiBridgeRegistry` — thread-safe registration and dispatch; **empty by
  default**, so v1 behaviour is exactly stock Chromium.

Phase-2 rules (enforced by review checklist in docs/PRIVACY.md):

1. A bridge implementation registers itself at startup; core browser code
   depends only on the interface.
2. No API secrets in the app package. Credentials arrive at runtime from the
   user or a backend the user explicitly connects; the AI backend itself is a
   later-phase component and this repo ships none of it.
3. No fake agent: until a real implementation ships, no bridge is registered
   and nothing pretends to be one.
4. All profile data stays on-device; a bridge that needs page content obtains
   it from the local session and must not exfiltrate it (privacy doc gate).

## Build flow and CI

* `build/fetch_chromium.sh` — depot_tools, pinned checkout, hooks,
  patch validation + application.
* `build/build_android.sh` — `gn gen` with `config/gn_args/*.gni`,
  `autoninja chrome_public_apk`, artifact copying.
* `build/sign_release.sh` — `apksigner` with env-provided credentials only.
* Hosted CI verifies everything verifiable without the source checkout;
  a GitHub-hosted larger runner builds the APKs and publishes them as
  Release assets (docs/CI_CD.md).
