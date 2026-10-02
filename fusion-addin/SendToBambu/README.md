# Send to Bambu

Fusion add-in: one toolbar button exports every visible solid as a millimeter 3MF and opens it in Bambu Studio. You do not select bodies.

**Same add-in on Windows and Mac.** One zip, one folder, two operating systems.

## Install in Fusion (Windows and Mac)

1. Unzip this folder so you have a directory named `SendToBambu` that contains `SendToBambu.py`, `stb_export.py`, and `SendToBambu.manifest`. Replace the **entire** folder — not just one file.
2. In Fusion, open **Utilities → Add-Ins → Scripts and Add-Ins**.
3. Open the **Add-Ins** tab.
4. Click the green **+** next to My Add-Ins and choose the `SendToBambu` folder. If it is already listed, skip this.
5. If it is running, click **Stop**. Quit Fusion, open Fusion again, select **Send to Bambu**, check **Run on Startup**, then **Run**.

The **Send to Bambu** button appears in Design (and Surface / Mesh) on a **Bambu Print** panel. It is also listed under **Add-Ins**.

## Use

1. Open a design. Hide any body you do not want on the plate (browser light bulb off).
2. Click **Send to Bambu**. Every visible solid is sent — root bodies and visible assembly instances.
3. Bambu Studio opens with the parts. Slice and print from there.

## If Bambu Studio is not found

Use **Bambu Print Settings → Locate Bambu Studio…**

| | Typical path |
|---|---|
| Windows | `C:\Program Files\Bambu Studio\bambu-studio.exe` |
| Mac | `/Applications/BambuStudio.app` |

On Mac, pick the `.app` itself — Finder treats it as a folder. The add-in launches Studio with `open -a`, so a Studio window that is already open gets the file.

On Windows, auto-detect also checks Local AppData and the App Paths registry. Launch uses `cmd /c start` so Fusion is not left waiting on Studio.

## Notes

- Export asks Fusion to write **millimeters**. Older Fusion builds that cannot set units still get a ×10 convert from centimeters. Fusion’s 3D Print Utility is not used.
- Default format is **3MF** (`unit="millimeter"`), one named object per body. Switch to STL in settings if you prefer; multiple bodies are merged.
- Hidden bodies and surface bodies are skipped.
- Version 1.3.1: visible solids, no selection, true millimeter export.