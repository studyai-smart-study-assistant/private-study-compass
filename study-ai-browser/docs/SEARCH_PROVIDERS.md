# Search providers

Study AI Browser does **not** include a search engine or crawler of its own.
The omnibox detects URLs and sends search queries to an external search
provider, exactly like every mainstream browser.

## Default

Fresh profiles fall back to **DuckDuckGo** (`patches/patch_02_search_provider.py`
changes Chromium's hard-coded fallback from Google to DuckDuckGo in
`components/search_engines/template_url_prepopulate_data.cc`).

## Configurable by the user

Settings → Search engine exposes Chromium's full engine list; the user can
select any prepopulated provider or add a custom one (name, URL pattern with
`%s`). The address bar continues to detect URLs vs. queries regardless of
provider.

## What the selected provider receives

Every omnibox search sends the **search query text** to the active provider.
This is inherent to searching with an external provider and is documented in
docs/PRIVACY.md. Providers may additionally receive IP address and their own
cookies per their policies; browser history and page contents are *not* sent
to providers.

## Adding or changing the default (developers)

1. Edit `patches/patch_02_search_provider.py` (engine references come from
   `third_party/search_engines_data/resources/definitions/prepopulated_engines.h`
   in the checkout).
2. Run `apply_patches.py --check` against a fresh pinned checkout — the
   engine fails loudly if upstream renamed things.
3. Update this file and `docs/PRIVACY.md` (the "receives search queries" row).
