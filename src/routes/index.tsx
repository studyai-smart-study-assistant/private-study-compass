import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Study AI Browser — Android Project Source" },
      {
        name: "description",
        content:
          "Complete source repository for Study AI Browser: a Chromium-based Android browser with local-first privacy, build scripts, tests, and CI/CD workflows.",
      },
      { property: "og:title", content: "Study AI Browser — Android Project Source" },
      {
        property: "og:description",
        content:
          "Complete source repository for Study AI Browser: a Chromium-based Android browser with local-first privacy, build scripts, tests, and CI/CD workflows.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <div
      className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center"
      style={{ backgroundColor: "#fcfbf8" }}
    >
      <img
        src="/favicon.png"
        alt="Study AI Browser logo"
        width={96}
        height={96}
        loading="lazy"
      />
      <h1 className="text-2xl font-semibold text-neutral-900">Study AI Browser</h1>
      <p className="max-w-md text-sm text-neutral-600">
        This Lovable project hosts the Android browser project source in the{" "}
        <code>study-ai-browser/</code> directory — a Chromium-based browser with
        local-first privacy, build scripts, tests, and CI/CD workflows. See{" "}
        <code>study-ai-browser/README.md</code>.
      </p>
    </div>
  );
}
