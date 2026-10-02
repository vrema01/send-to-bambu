import { Printer, Settings } from "lucide-react";

export function FusionToolbar() {
  return (
    <div className="overflow-hidden rounded-xl border border-border bg-surface shadow-soft">
      <div className="flex items-center gap-2 border-b border-border bg-surface-2 px-3 py-2">
        <span className="size-2.5 rounded-full bg-border" />
        <span className="size-2.5 rounded-full bg-border" />
        <span className="size-2.5 rounded-full bg-border" />
        <p className="ml-2 truncate font-mono text-xs text-muted">
          Design · Bracket_v3
        </p>
      </div>
      <div className="flex gap-1 overflow-x-auto px-2 py-2">
        {["SOLID", "SURFACE", "MESH", "SHEET METAL"].map((tab) => (
          <span
            key={tab}
            className="shrink-0 rounded-md px-2.5 py-1.5 text-xs font-medium tracking-wide text-muted"
          >
            {tab}
          </span>
        ))}
        <span className="shrink-0 rounded-md bg-surface-2 px-2.5 py-1.5 text-xs font-medium tracking-wide text-fg">
          MAKE
        </span>
      </div>
      <div className="flex items-stretch gap-2 border-t border-border px-3 py-3">
        <div className="flex min-w-16 flex-1 flex-col items-center justify-center gap-1 rounded-md px-2 py-2 text-muted">
          <span className="text-xs tracking-wide">3D Print</span>
        </div>
        <div className="flex min-w-28 flex-1 flex-col items-center justify-center gap-1 rounded-md bg-sage px-3 py-2 text-sage-fg">
          <Printer className="size-4" strokeWidth={1.75} />
          <span className="text-center text-xs font-medium tracking-wide">
            Send to Bambu
          </span>
        </div>
        <div className="flex min-w-16 flex-1 flex-col items-center justify-center gap-1 rounded-md px-2 py-2 text-muted">
          <Settings className="size-4" strokeWidth={1.75} />
          <span className="text-xs tracking-wide">Settings</span>
        </div>
      </div>
    </div>
  );
}
