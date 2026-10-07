# Send to Bambu

Sends selected bodies to Bambu Studio as STL.

Version 1.1 closes open sections before export. Open surface bodies are copied into a temporary component, stitched (0.5 mm gap tolerance), and exported only if they become a solid. Your original design is not changed.

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

The manifest starts the add-in when Fusion opens. The button shows under Utilities, named Send to Bambu. If it is not listed, press Shift+S, open the Add-Ins tab, and confirm SendToBambu is under My Add-Ins.

Button shows under Utilities, named Send to Bambu.

## Use

1. Select one or more bodies.
2. Click Send to Bambu.
3. Bambu Studio opens with the STL files.

Close Bambu Studio first if it is already open. It often ignores a file sent while it is running.

## Paths

Windows: `C:\Program Files\Bambu Studio\bambu-studio.exe`

Mac: `/Applications/BambuStudio.app`

If Studio is installed somewhere else, edit `BAMBU_WIN` or `BAMBU_MAC` at the top of `SendToBambu.py`.
