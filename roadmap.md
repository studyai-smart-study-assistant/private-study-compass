# Study AI Browser — Roadmap

Chromium-based Android browser (pin: Chromium 156.0.8078.47, arm64+arm).
Code lives in `study-ai-browser/`; CI workflows at repo root are path-filtered.

## Tasks
- [x] Feasibility check: sandbox cannot build Chromium (32GB scratch, 32GB RAM, 10-min cmd cap); build happens in CI on self-hosted runner
- [x] Branding assets (app icon, launcher set, adaptive icons) in `study-ai-browser/branding/`
- [x] Core docs: README.md, BUILDING.md, PRIVACY.md, SEARCH_PROVIDERS.md, CI_CD.md, ARCHITECTURE.md
- [x] Build scripts: verify_environment / fetch_chromium / build_android / sign_release + patch engine (`build/apply_patches.py`)
- [x] Patch set: branding (verified manifest label + icons), search provider fallback (verified), backup disable (verified), AI extension points (verified BUILD.gn anchor)
- [x] Config: GN args templates, Chromium pin, app config, signing script (env secrets only)
- [x] Custom Java extension-point sources (`src-custom/` → `//study_ai/browser`)
- [x] Tests: patch engine unit tests, patches-on-mock-tree tests, config/workflow validators (40 tests, all passing)
- [x] GitHub Actions: verify.yml (hosted) + build-apk.yml (self-hosted, signs via secrets)
- [x] License docs: LICENSE.md (BSD-3 + Apache 2.0), THIRD_PARTY_NOTICES.md
- [x] Run all runnable tests locally; verified patch anchors against real Chromium 156 sources (manifest, BUILD.gn, template_url_prepopulate_data.cc)
- [ ] APK generation — BLOCKED: requires the self-hosted build runner (docs/CI_CD.md); user provisions hardware
- [ ] First real CI build + on-device smoke test — BLOCKED: same runner
