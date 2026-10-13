# Send to Bambu

Sends every visible body to Bambu Studio as a closed STL. Hidden bodies are skipped. There is no selection and no message box.

Version 1.2 closes open sections before export. The body is copied into a temporary component. Your original design is not changed. Nearby open edges are stitched (0.5 mm, then 1 mm, 2 mm, and 4 mm). Each hole that is still open is patched and stitched back on. The STL is written only when the result is a watertight solid.

## Install

Fusion requires the folder, the Python file, and the manifest to share one name. This add-in uses `SendToBambu` for all three: the folder `SendToBambu`, `SendToBambu.py`, and `SendToBambu.manifest`.

Copy this whole folder into Fusion's AddIns folder.

Windows:

`%AppData%\Autodesk\Autodesk Fusion 360\API\AddIns\SendToBambu`

If that folder is not on the machine, use:

`%AppData%\Autodesk\Autodesk Fusion\API\AddIns\SendToBambu`

Mac:

`~/Library/Application Support/Autodesk/Autodesk Fusion/API/AddIns/SendToBambu`

Older Mac installs:

`~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/SendToBambu`

The manifest starts the add-in when Fusion opens. On the Solid tab, Bambu is the last icon. Click the green icon once. If it is not listed, press Shift+S, open the Add-Ins tab, select SendToBambu, and click Run.

## Use

1. Leave the light on for every body that should print. Hide the rest.
2. Click the green Bambu icon.
3. Bambu Studio comes forward with those bodies. There is no selection step and no status box.

Close Bambu Studio first if it is already open. It often ignores a file sent while it is running.

## Paths

Windows: `C:\Program Files\Bambu Studio\bambu-studio.exe`

Mac: `/Applications/BambuStudio.app`

If Studio is installed somewhere else, edit `BAMBU_WIN` or `BAMBU_MAC` at the top of `SendToBambu.py`.

## Source

The master copy is https://github.com/vrema01/send-to-bambu on the `main` branch.
