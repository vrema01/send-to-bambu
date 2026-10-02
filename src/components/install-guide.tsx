"use client";

import { useEffect, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const shared = [
  {
    title: "Download and unzip",
    body: "Download SendToBambu.zip and unzip it. You should get one folder named SendToBambu. Leave the files inside that folder. Do not rename it.",
  },
  {
    title: "Point Fusion at the folder",
    body: "In Fusion: Utilities → Add-Ins → Scripts and Add-Ins. Open the Add-Ins tab. Next to My Add-Ins, click the green +. Choose the SendToBambu folder.",
  },
  {
    title: "Turn it on",
    body: "Select Send to Bambu. Check Run on Startup, then click Run. The button shows up in Design, on a panel named Bambu Print.",
  },
];

const windowsSteps = [
  ...shared,
  {
    title: "Updating an older copy",
    body: "In Scripts and Add-Ins, select Send to Bambu and click Stop. Quit Fusion completely. Unzip the new download on top of the old SendToBambu folder and replace it. Open Fusion and click Run.",
  },
];

const macSteps = [
  ...shared,
  {
    title: "Updating an older copy",
    body: "In Scripts and Add-Ins, select Send to Bambu and click Stop. Quit Fusion (Fusion menu → Quit, not just close the window). Unzip the new download on top of the old SendToBambu folder and replace it. Open Fusion and click Run.",
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
