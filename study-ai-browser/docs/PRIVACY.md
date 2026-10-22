# Privacy architecture

## Principle

Study AI Browser is local-first: **all browser profile data stays on the
device**. Browsing history, bookmarks, tabs, cookies, site data, passwords,
and downloads live in the app's private storage and are never uploaded to any
Study AI backend, cloud service, analytics pipeline, or sync target. There is
no Study AI cloud sync in v1 — no Supabase, no Edge Functions, no analytics.

## What the build enforces

| Control | Mechanism |
|---|---|
| No Google API keys | `use_official_google_api_keys=false` (config/gn_args) — keyed services are compiled out; nothing can silently ship keys |
| UMA metrics / crash upload | disabled by default in non-branded builds (`is_chrome_branded=false`); no keys → no upload endpoints |
| Field-trial/variation config | `disable_fieldtrial_testing_config=true` |
| Android cloud backup | patches/patch_03_privacy.py forces `android:allowBackup="false"` in the manifest — profile data can never leave via the backup transport |
| Third-party telemetry | the browser is Chromium + the patches in this repo; no additional analytics or SDK is added |
| Search provider | default fallback is DuckDuckGo (patch_02); user-configurable in Settings → Search engine |

## Network requests that remain (unavoidable, documented)

| Request | To | When | Can it be avoided? |
|---|---|---|---|
| Page loads | the websites you visit | whenever you browse | no — this is what a browser does |
| Search queries | the selected search provider (default DuckDuckGo) | omnibox search | only by not searching |
| HTTPS upgrades/CRLs/OCSP | sites / certificate authorities | certificate checks | partially, browser-managed |
| Safe Browsing checks | Google | only if the user enables Safe Browsing in settings | yes — leave off for maximum privacy; site-local phishing protection still applies |
| Component/network updates (e.g. root store) | Google | component updater | OS root store is used when available; disabling would degrade TLS security |
| HTTPS/DNS (as configured) | DNS resolvers | name resolution | user can choose private DoH providers in settings |

Nothing above sends browsing history, visited URLs, tab data, cookies, or page
contents to Study AI infrastructure. Website and search-provider recipients
are inherent to browsing and are controlled by what the user chooses to visit
and which provider they select.

## Data storage locations (all on-device, app-private)

* History, bookmarks, passwords, cookies: Chromium profile storage in the
  app's private data directory (`/data/data/com.studyai.browser/`).
* Downloads: standard `Downloads` via system picker; nothing is uploaded.
* Clear browsing data: Chromium's built-in settings (history, cookies, cache,
  site data, passwords) — same behaviour as stock Chromium.

## Audit checklist for future changes

Before merging any new feature (especially anything touching the reserved
`//study_ai/browser` bridge), verify:

1. no new network host is contacted without documentation in this file;
2. no profile data crosses a process boundary to anything non-device-local;
3. Android backup rules still exclude the app's data (manifest check in CI);
4. no API keys or tokens are embedded in the APK (CI leak scan);
5. `apply_patches.py --check` still passes against the pinned Chromium.

## Known limitations

* Chromium is large; a security review of the whole engine is out of scope.
  The update strategy (docs/BUILDING.md) tracks Chromium stable releases so
  engine security fixes land promptly.
* Safe Browsing, when enabled by the user, sends site URLs to Google —
  documented here rather than silently altered.
* Component updates keep the root store current; blocking them would weaken
  TLS validation and is not done.
