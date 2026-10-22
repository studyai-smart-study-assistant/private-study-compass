# CI/CD

Two workflows live at the repository root (path-filtered to `study-ai-browser/`).
**Both run entirely on GitHub-hosted runners — no self-hosted hardware is
required or used.**

## 1. `study-ai-browser-verify.yml` — hosted runner (free)

Runs on every push/PR touching the project, on the standard hosted runner
(`ubuntu-24.04`):

* full test suite (`tests/run_tests.sh`): patch-engine unit tests, all patches
  applied to the mock Chromium tree, config/consistency validation,
  workflow validation;
* `bash -n` syntax check of all build scripts;
* confirmation that the pinned Chromium tag exists upstream;
* repository-wide scan for private-key material.

## 2. `study-ai-browser-build-apk.yml` — GitHub-hosted larger runner (produces the APK)

### Why a standard hosted runner cannot do it

A genuine Chromium build is far beyond the standard `ubuntu-latest` runner,
and no amount of workflow tuning fixes a resource ceiling:

| Resource | Standard hosted runner | Chromium needs |
|---|---|---|
| Disk | **14 GB** SSD | ~100 GB source checkout, ~300 GB total for checkout + output |
| RAM | 16 GB | 64 GB minimum (linking is the bottleneck) |
| CPU | 4 vCPU | 16+ cores for a multi-hour build |
| Job time cap | 6 h | first build takes several hours on many cores |

The checkout cannot even be fetched onto a 14 GB disk, so a genuine
Chromium-based APK is **impossible** on standard hosted runners. This project
does not fake it — see "Limitations" below.

### The solution: GitHub-hosted *larger* runners

GitHub offers managed larger runners that are still fully hosted by GitHub
(no machine to provision, patch, or rent from a third party) with
pay-per-minute billing:

| Size | RAM | SSD | Rate (Linux) | ≈ per hour |
|---|---|---|---|---|
| 16-core | 64 GB | 600 GB | $0.042/min | $2.52 |
| 32-core (recommended) | 128 GB | 1200 GB | $0.082/min | $4.92 |
| 64-core | 256 GB | 2040 GB | $0.162/min | $9.72 |

Ballpark cost per full build on the recommended 32-core runner: the fetch
(~1–2 h) plus compile/link (~4–7 h) is roughly a **6–9 h job → $30–45 per
run**. The 16-core runner is cheaper per run but sits exactly at the 64 GB
RAM minimum and can push past the default 6 h job cap. The 64-core runner
finishes fastest and often costs about the same overall.

Rates and specifications are published by GitHub ("Actions runner pricing"
and "Larger runners reference" in the GitHub Docs); check them before
budgeting. Larger runners are billed per minute regardless of repository
visibility — they are not covered by the free standard-runner allowance.

### One-time setup (a few clicks, no hardware)

1. Repository **Settings → Actions → Runners → New runner → New GitHub-hosted
   larger runner**.
2. Pick the Ubuntu image and a size (32-core recommended). Note the
   machine-size label GitHub assigns (e.g. `32-core`) — that is the value
   passed to the workflow's `runner_label` input.
3. In the runner's settings, raise **maximum run time** from the default
   6 hours to at least 12 hours (first builds can exceed 6 h).
4. Billing: larger-runner usage is pay-per-minute and requires Actions
   spending to be enabled for the repository owner's account.
5. Add the four signing secrets (below) — or skip; the workflow then
   publishes a clearly-marked *unsigned* pre-release.

### Workflow inputs (Actions tab → "study-ai-browser build apk" → Run workflow)

| Input | Meaning |
|---|---|
| `arch` | `arm64` (recommended) or `arm` |
| `runner_label` | machine-size label of your larger runner, e.g. `32-core` |
| `make_release` | publish the APK as a GitHub Release asset after a verified build |
| `release_tag` | optional tag; auto-generated (`studyai-v<chromium>-run<n>`) when empty |

The job runs `verify_environment.sh` → `fetch_chromium.sh` (which validates
every patch context against the pinned tree) → `install-build-deps.sh` →
`build_android.sh` → `sign_release.sh` → `apksigner verify` → release
publishing, in that order.

### Release publishing (no Actions artifacts)

This workflow **does not use Actions artifact uploads at all** — APKs and
mapping files are published directly as **GitHub Release assets**:

* The release step is the last step of the job; if the fetch, build, sign, or
  verification step fails, the job stops first and **no release is created**.
* Publishing uses the workflow's ephemeral `GITHUB_TOKEN`; the elevated
  `contents: write` permission is scoped to that single job only. Enable
  "Read and write permissions" for the token under Settings → Actions →
  General → Workflow permissions if your repository/org restricts the
  default.
* The APK is attached with `gh release create`/`gh release upload --clobber`;
  the R8 `mapping` file is attached alongside when produced.
* Without signing secrets the job still succeeds, but the APK is attached to
  a **pre-release** and labelled UNSIGNED — a failed or unverifiable
  signature is never published as a normal release build.
* Each architecture dispatches its own run; both attach to their own release
  (or to the same tag via `--clobber` if you pass an explicit `release_tag`).

### Secrets (Repository → Settings → Secrets and variables → Actions)

| Secret | Contents |
|---|---|
| `STUDYAI_KEYSTORE_B64` | release keystore, base64-encoded |
| `STUDYAI_KEYSTORE_PASSWORD` | keystore password |
| `STUDYAI_KEY_ALIAS` | signing key alias |
| `STUDYAI_KEY_PASSWORD` | key password (optional; defaults to keystore password) |

Credentials exist **only** as Actions secrets — never in the repo (the verify
workflow scans for violations).

### Runbook: cutting a release

1. Confirm the verify workflow is green.
2. Dispatch the build workflow: `arm64`, your runner label, `make_release: true`.
3. When the job is green, download the APK from the Releases page (Assets).
4. Verify the signature before distributing:
   `apksigner verify --print-certs StudyAIBrowser-arm64.apk`.
5. Install on a test device and exercise: omnibox URL/search detection, tabs,
   back/forward/reload, bookmarks, history, downloads, settings, incognito,
   clear browsing data.
6. Tag the repository; the release is already attached to its build tag.

### Limitations (documented, not hidden)

* **Cold builds.** Larger runners are ephemeral: the 100+ GB checkout is
  re-fetched on every run. GitHub's Actions cache caps at 10 GB per
  repository, far below the checkout, so only depot_tools could be cached —
  not worth the complexity. Expect a similar duration and cost per run.
* **Standard hosted runners cannot build Chromium** (14 GB disk vs ~100 GB
  checkout). There is no free hosted path; the larger runner is the only
  GitHub-hosted way, and it bills per minute.
* **Job cap.** Keep the larger runner's "maximum run time" at ≥ 12 h; the
  workflow's own `timeout-minutes` is 720.
* **No APK exists in this repository.** The APK is produced only by a green
  run of the build workflow; nothing here claims otherwise.
