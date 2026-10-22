// Mock fragment of components/search_engines/template_url_prepopulate_data.cc
// (Chromium 156.0.8078.47) used by the patch tests.

std::unique_ptr<TemplateURLData> GetPrepopulatedFallbackSearch(
    PrefService& prefs,
    const std::vector<raw_ptr<const PrepopulatedEngine>>&
        regional_prepopulated_engines) {
  return FindPrepopulatedEngineInternal(prefs, regional_prepopulated_engines,
                                        google.id,
                                        /*use_first_as_fallback=*/true);
}
