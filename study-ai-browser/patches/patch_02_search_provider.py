# Copyright 2026 Study AI Browser contributors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Search provider patch: make DuckDuckGo the default fallback search engine.

Context verified against Chromium 156.0.8078.47
(components/search_engines/template_url_prepopulate_data.cc, function
GetPrepopulatedFallbackSearch): Chromium's fallback default engine is hard-coded
to Google. We switch that fallback to DuckDuckGo so fresh profiles do not send
queries to Google out of the box.

Scope note (documented in docs/SEARCH_PROVIDERS.md):
  * Regional default engines remain Chromium's; every user can change the
    engine in Settings > Search engine, which is the PRD's "configurable
    external search provider" requirement.
  * Whichever provider is active receives the user's search queries — that is
    the documented, unavoidable network request to the search provider.
"""

from patch_edits import Patch, Replace

PATCH = Patch(
    id="search-provider",
    description="Default fallback search engine: Google -> DuckDuckGo",
    edits=(
        Replace(
            path="components/search_engines/template_url_prepopulate_data.cc",
            old=(
                "  return FindPrepopulatedEngineInternal(prefs, regional_prepopulated_engines,\n"
                "                                        google.id,\n"
                "                                        /*use_first_as_fallback=*/true);"
            ),
            new=(
                "  return FindPrepopulatedEngineInternal(prefs, regional_prepopulated_engines,\n"
                "                                        duckduckgo.id,\n"
                "                                        /*use_first_as_fallback=*/true);"
            ),
            description="Fallback default search engine for fresh profiles",
        ),
    ),
)
