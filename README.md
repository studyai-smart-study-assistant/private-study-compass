# Private Study Compass

Project: Study AI Browser — PRD + TRD

Build a complete Android browser named Study AI Browser, based on the real Chromium Android source code. This must be a genuine Chromium-based browser, not an Android WebView wrapper, a mock UI, or a simplified browser.

Product Requirements (PRD)

Create a usable Android browser with:

- Study AI Browser branding, app icon, and a clean, mobile-friendly interface.
- An address/search bar that detects URLs and search queries, using a configurable external search provider.
- Tabs, back/forward, reload, bookmarks, browsing history, downloads, and browser settings.
- Private/incognito browsing and an option to clear browsing data.
- A modular architecture that can support Study AI's future AI API and MCP-powered browser agent. Do not implement a fake agent or embed API secrets in the app.

Technical Requirements (TRD)

1. First inspect the current repository and build environment. Identify the appropriate Chromium Android source revision, dependencies, build requirements, licensing obligations, and feasibility. Then proceed incrementally: first establish a genuine Chromium Android build, then customize the app and add features. Do not stop after producing a plan.

2. Use Chromium's actual browser engine and navigation infrastructure. Do not silently substitute WebView or claim the project is complete without a verifiable build.

3. Privacy-first architecture: Keep browsing history, bookmarks, tabs, cookies, and other browser profile data in the app's local private storage by default. Never upload browsing history, visited URLs, tab data, cookies, or page contents to Supabase, Edge Functions, Lovable cloud, analytics, or any Study AI backend. No cloud sync or history upload by default. Audit Android backup behaviour and optional Chromium telemetry/reporting. Preserve essential security updates and document unavoidable network requests, including those made to websites and the selected search provider.

4. Configure search providers without building a search engine or crawler of our own. Clearly document that the selected provider receives search queries.

5. GitHub CI/CD: Create production-minded GitHub Actions workflows, build scripts, and documentation. Run applicable checks and build the Android APK; upload verifiable APK artifacts. Store release-signing credentials only in GitHub Actions secrets, never in source code. If a standard hosted runner cannot handle Chromium's source build, provide a workflow and clear setup instructions for a suitably provisioned self-hosted Linux runner instead of pretending the build succeeded.

6. Preserve Chromium copyright notices and all required third-party license notices. Document the Chromium version, build prerequisites, local privacy guarantees and limitations, build commands, release-signing setup, and update strategy in "README.md".

Acceptance Criteria

Deliver the actual project code, Android configuration, build scripts, tests where applicable, and CI/CD workflows. Work in small, verifiable milestones and report which steps genuinely build and pass. Do not fabricate build results, leave essential features as placeholders, or claim an APK exists unless it has actually been generated.

Keep the initial scope focused on a functional Chromium browser and local-first privacy. Design the architecture so Study AI's AI API and MCP browser-agent capabilities can be added in a later phase.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/6fa730a7-925d-4cc7-ab61-2791496d884c).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
