import { createFileRoute } from "@tanstack/react-router";
import {
  BoxSelect,
  Download,
  Layers3,
  Printer,
  Settings2,
} from "lucide-react";
import { FusionToolbar } from "@/components/fusion-toolbar";
import { InstallGuide } from "@/components/install-guide";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/")({ component: Home });

const DOWNLOAD_HREF = "/downloads/SendToBambu.zip";

function DownloadButton({
  size = "lg",
  variant = "default",
}: {
  size?: "lg" | "default";
  variant?: "default" | "outline";
}) {
  return (
    <Button variant={variant} size={size} asChild>
      <a href={DOWNLOAD_HREF} download="SendToBambu.zip">
        <Download />
        Download add-in
      </a>
    </Button>
  );
}

function Home() {
  return (
    <div className="min-h-dvh bg-bg text-fg">
      <header className="sticky top-0 z-20 border-b border-border/80 bg-bg/90 backdrop-blur-sm">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4">
          <a href="#top" className="flex items-center gap-2 text-sm font-medium">
            <Printer className="size-4 text-sage" strokeWidth={1.75} />
            Send to Bambu
          </a>
          <DownloadButton size="default" />
        </div>
      </header>

      <main id="top">
        <section className="mx-auto grid max-w-5xl gap-10 px-4 py-12 sm:py-16 lg:grid-cols-[1.15fr_0.85fr] lg:items-center lg:py-20">
          <div>
            <p className="font-mono text-xs tracking-wide text-sage">
              Fusion add-in · Windows & Mac
            </p>
            <h1 className="mt-3 max-w-xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
              Send visible parts to Bambu Studio
            </h1>
            <p className="mt-4 max-w-lg text-base leading-relaxed text-muted">
              A button in Fusion that grabs every solid you can see, saves it
              in millimeters, and opens it in Bambu Studio. You do not select
              anything. Hide a body to leave it out.
            </p>
            <p className="mt-3 max-w-lg text-sm leading-relaxed text-sage">
              Already using an older copy? Stop it, replace the folder, quit
              Fusion, then Run again.
            </p>
            <div className="mt-7 flex flex-wrap items-center gap-3">
              <DownloadButton />
              <Button variant="outline" size="lg" asChild>
                <a href="#install">Install steps</a>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <a href="/instructions.html" download="SendToBambu-instructions.html">
                  Instructions page
                </a>
              </Button>
            </div>
          </div>
          <FusionToolbar />
        </section>

        <section className="border-y border-border bg-surface">
          <div className="mx-auto grid max-w-5xl gap-8 px-4 py-12 sm:grid-cols-3">
            {[
              {
                icon: BoxSelect,
                title: "Every visible solid",
                body: "No selection. It takes every visible solid in the design, including assembly instances. Hide a body in the browser to leave it off the plate.",
              },
              {
                icon: Layers3,
                title: "Separate objects, in mm",
                body: "Each visible solid opens as its own object in Bambu Studio, in millimeters. STL in settings is the one format that combines them.",
              },
              {
                icon: Printer,
                title: "Opens Bambu Studio",
                body: "Windows launches bambu-studio.exe. Mac uses open -a on BambuStudio.app so a Studio window that is already open gets the file.",
              },
            ].map((item) => (
              <div key={item.title} className="min-w-0">
                <item.icon className="size-5 text-sage" strokeWidth={1.75} />
                <h2 className="mt-3 text-base font-medium">{item.title}</h2>
                <p className="mt-2 text-sm leading-relaxed text-muted">
                  {item.body}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section id="install" className="mx-auto max-w-5xl px-4 py-14">
          <p className="font-mono text-xs tracking-wide text-sage">Install</p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight">
            Four steps. Same on Windows and Mac.
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted">
            Unzip the folder, tell Fusion where it is, and click Run. The
            only difference between computers is where Bambu Studio is
            installed, and the add-in looks for that itself.
          </p>
          <div className="mt-8">
            <InstallGuide />
          </div>
        </section>

        <section className="border-y border-border bg-surface">
          <div className="mx-auto grid max-w-5xl gap-10 px-4 py-14 lg:grid-cols-2">
            <div>
              <p className="font-mono text-xs tracking-wide text-sage">
                What it sends
              </p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight">
                All visible solids, nothing to pick
              </h2>
              <ul className="mt-5 grid gap-3 text-sm leading-relaxed text-muted">
                <li className="rounded-lg border border-border bg-bg px-4 py-3">
                  Every visible solid in the root component.
                </li>
                <li className="rounded-lg border border-border bg-bg px-4 py-3">
                  Visible bodies in assembly occurrences, in world position.
                </li>
                <li className="rounded-lg border border-border bg-bg px-4 py-3">
                  Hidden bodies (browser light bulb off) are skipped.
                </li>
                <li className="rounded-lg border border-border bg-bg px-4 py-3">
                  Several bodies — one 3MF with a named object per body.
                </li>
              </ul>
            </div>
            <div>
              <p className="font-mono text-xs tracking-wide text-sage">
                Settings
              </p>
              <h2 className="mt-2 flex items-center gap-2 text-2xl font-semibold tracking-tight">
                <Settings2 className="size-6 text-sage" strokeWidth={1.75} />
                Bambu Print Settings
              </h2>
              <p className="mt-3 text-sm leading-relaxed text-muted">
                Mesh quality, 3MF vs STL, whether to launch Studio, and an
                optional path if auto-detect misses your install.
              </p>
              <dl className="mt-5 grid gap-3 font-mono text-xs text-muted">
                <div className="rounded-lg border border-border bg-bg px-4 py-3">
                  <dt className="text-subtle">Windows</dt>
                  <dd className="mt-1 break-all text-fg">
                    {"C:\\Program Files\\Bambu Studio\\bambu-studio.exe"}
                  </dd>
                </div>
                <div className="rounded-lg border border-border bg-bg px-4 py-3">
                  <dt className="text-subtle">Mac</dt>
                  <dd className="mt-1 break-all text-fg">
                    /Applications/BambuStudio.app
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-5xl px-4 py-14">
          <h2 className="text-2xl font-semibold tracking-tight">
            If something misses
          </h2>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {[
              {
                q: "It says no body was found",
                a: "Turn the light bulb on for the bodies you want. Hidden bodies and surfaces are skipped. You do not need to click the bodies first.",
              },
              {
                q: "Bambu Studio did not open",
                a: "Install Bambu Studio, then click Bambu Print Settings → Locate Bambu Studio and pick the app.",
              },
              {
                q: "The part is the wrong size",
                a: "You still have an older copy. Stop the add-in, replace the whole SendToBambu folder, quit Fusion, then Run.",
              },
              {
                q: "I do not see the button",
                a: "Utilities → Add-Ins → Scripts and Add-Ins → Add-Ins tab → Send to Bambu → Run. Check Run on Startup so it comes back next time.",
              },
              {
                q: "An error mentions scale_binary_stl",
                a: "Fusion is still holding the old files. Stop the add-in, replace the whole folder, quit Fusion, then Run.",
              },
            ].map((item) => (
              <div
                key={item.q}
                className="rounded-lg border border-border bg-surface p-4"
              >
                <h3 className="text-sm font-medium">{item.q}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">
                  {item.a}
                </p>
              </div>
            ))}
          </div>
          <div className="mt-10 flex flex-wrap items-center gap-3">
            <DownloadButton />
            <Button variant="outline" asChild>
              <a href="/instructions.html" download="SendToBambu-instructions.html">
                Instructions page
              </a>
            </Button>
            <p className="text-sm text-muted">
              Zip includes the add-in and a short README.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
