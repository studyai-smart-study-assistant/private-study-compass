<!-- LOVABLE:BEGIN -->
# study-ai-browser/ — Android (Chromium) project

This directory is a **standalone Android/Chromium deliverable** (see
README.md). It is not part of the TanStack Start web app and must never be
imported by or integrated with `src/`, `vite.config.ts`, or the web build.

Rules for changes in this directory:
- Engine comes from the pinned Chromium checkout (`config/chromium_pin.json`);
  never vendor Chromium source files into this repository.
- Customizations are made only through `patches/patch_*.py` + the patch
  engine; never hand-edit "expected" Chromium content elsewhere.
- Every patch context must be verified against the pinned tag
  (`build/apply_patches.py --check` in CI); keep `tests/fixtures/chromium-mock/`
  in sync with real file fragments.
- No secrets, API keys, or telemetry endpoints anywhere in this directory.
- Run `./tests/run_tests.sh` after any change here.
<!-- LOVABLE:END -->
