# Study AI Browser — Roadmap

Chromium-based Android browser (pin: Chromium 156.0.8078.47, arm64+arm).
Code lives in `study-ai-browser/`; CI workflows at repo root are path-filtered.

## Tasks
- [x] Feasibility check: sandbox cannot build Chromium (32GB scratch, 32GB RAM, 10-min cmd cap); build happens in CI on self-hosted runner
- [ ] Branding assets (app icon, adaptive foreground) in `study-ai-browser/branding/`
- [ ] Core docs: README.md, BUILDING.md, PRIVACY.md, SEARCH_PROVIDERS.md, CI_CD.md, ARCHITECTURE.md
- [ ] Build scripts: fetch/build/sign/verify + patch engine (`build/apply_patches.py`)
- [ ] Patch set: branding, search provider default, privacy/telemetry kill switches, backup rules, AI extension points
- [ ] Config: GN args templates, Chromium pin, search provider config, signing template (no secrets)
- [ ] Custom Java extension-point sources (`src-custom/`)
- [ ] Tests: patch engine tests (runnable here), config/GN-args validators, script checks
- [ ] GitHub Actions: `verify.yml` (hosted runner) + `build-apk.yml` (self-hosted, signs via secrets)
- [ ] License docs: Chromium notices preservation + third-party notices
- [ ] Run all runnable tests locally; report what was verified vs. what needs the build machine
