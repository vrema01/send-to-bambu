"use client";

import { useEffect, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const windowsSteps = [
  {
    title: "Unzip the add-in",
    body: "Download SendToBambu.zip and unzip it. You should have a folder named SendToBambu that contains SendToBambu.py and SendToBambu.manifest. Use this same folder on a Mac if you have one.",
  },
  {
    title: "Add it in Fusion",
    body: "In Fusion: Utilities → Add-Ins → Scripts and Add-Ins. Open the Add-Ins tab, click the green plus next to My Add-Ins, and choose the SendToBambu folder.",
  },
  {
    title: "Stop, replace, then Run",
    body: "If Send to Bambu is already loaded, click Stop. Unzip this download over the same SendToBambu folder so SendToBambu.py and stb_export.py update together. Quit Fusion, open it, select the add-in, check Run on Startup, then Run.",
  },
  {
    title: "Bambu Studio path",
    body: "Auto-detect looks in Program Files, Local AppData, and the Windows App Paths registry. If yours lives elsewhere, click Locate Bambu Studio in Bambu Print Settings and pick bambu-studio.exe.",
  },
];

const macSteps = [
  {
    title: "Unzip the add-in",
    body: "Download SendToBambu.zip and unzip it. Keep the SendToBambu folder intact — Fusion needs SendToBambu.py sitting next to SendToBambu.manifest. The same zip is what you install on Windows.",
  },
  {
    title: "Add it in Fusion",
    body: "In Fusion: Utilities → Add-Ins → Scripts and Add-Ins. Open the Add-Ins tab, click the green plus next to My Add-Ins, and choose the SendToBambu folder.",
  },
  {
    title: "Stop, replace, then Run",
    body: "If Send to Bambu is already loaded, click Stop. Unzip this download over the same SendToBambu folder so SendToBambu.py and stb_export.py update together. Quit Fusion, open it, select the add-in, check Run on Startup, then Run.",
  },
  {
    title: "Bambu Studio path",
    body: "Auto-detect looks in /Applications and ~/Applications, then Spotlight. Launch uses macOS open -a so an already-running Studio gets the file. If needed, Locate Bambu Studio and pick BambuStudio.app (it behaves like a folder).",
  },
];

function StepList({ steps }: { steps: { title: string; body: string }[] }) {
  return (
    <ol className="grid gap-3">
      {steps.map((step, index) => (
        <li
          key={step.title}
          className="grid grid-cols-[auto_1fr] gap-4 rounded-lg border border-border bg-surface p-4"
        >
          <span className="flex size-8 items-center justify-center rounded-md bg-surface-2 font-mono text-sm text-sage">
            {index + 1}
          </span>
          <div className="min-w-0">
            <h3 className="text-sm font-medium text-fg">{step.title}</h3>
            <p className="mt-1 text-sm leading-relaxed text-muted">{step.body}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}

function detectOs(): "windows" | "mac" {
  if (typeof navigator === "undefined") return "windows";
  const platform = navigator.platform || "";
  const ua = navigator.userAgent || "";
  if (/Mac|iPhone|iPad/.test(platform) || /Mac OS X/.test(ua)) return "mac";
  return "windows";
}

export function InstallGuide() {
  const [os, setOs] = useState<"windows" | "mac">("windows");

  useEffect(() => {
    setOs(detectOs());
  }, []);

  return (
    <Tabs key={os} defaultValue={os} className="w-full">
      <TabsList className="w-full sm:w-auto">
        <TabsTrigger value="windows" className="flex-1 sm:flex-none">
          Windows
        </TabsTrigger>
        <TabsTrigger value="mac" className="flex-1 sm:flex-none">
          Mac
        </TabsTrigger>
      </TabsList>
      <TabsContent value="windows">
        <StepList steps={windowsSteps} />
      </TabsContent>
      <TabsContent value="mac">
        <StepList steps={macSteps} />
      </TabsContent>
    </Tabs>
  );
}
