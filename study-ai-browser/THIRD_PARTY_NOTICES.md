# Third-party notices

Distributed APKs are built from the pinned Chromium source tree
(`config/chromium_pin.json`). Chromium bundles a very large number of
third-party components, each with its own license; those notices reach users
through the licenses page built into the browser (Chromium's `about_credits`
resource, generated from the checkout at build time and visible in Settings →
Licenses). The build system and this repository must not alter, omit, or
reorder those generated notices.

## How notices are preserved

1. The patch engine (`build/apply_patches.py`) only modifies the files listed
   in `patches/patch_*.py` — no patch may touch any `LICENSE*` file,
   `third_party/` notices, or the credits generation logic. New patches are
   reviewed against this rule (checklist in docs/PRIVACY.md).
2. The checkout is fetched from the official Chromium repository at a pinned
   tag, so all upstream copyright headers and third-party license files are
   present verbatim.
3. The launcher icon assets in `branding/icons/` are original Study AI
   Browser artwork (Apache 2.0, see LICENSE.md) — they replace icon files
   only, never license or notice resources.

## Components added by Study AI Browser

| Component | License | Origin |
|---|---|---|
| Chromium source tree (engine and bundled third-party components) | BSD 3-Clause + per-component licenses (see built-in licenses page) | https://chromium.googlesource.com/chromium/src |
| depot_tools (build tooling only, not distributed in the APK) | BSD-style | https://chromium.googlesource.com/chromium/tools/depot_tools |
| Study AI Browser branding assets and Java bridge sources | Apache 2.0 | this repository |

## Distribution obligations checklist (per release)

- [ ] APK contains the Chromium licenses page and it opens from Settings.
- [ ] No patch or build step removed or rewrote license/notice files.
- [ ] `LICENSE.md` ships with the source distribution of this repository.
