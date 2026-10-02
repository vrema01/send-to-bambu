# Send to Bambu

A Fusion button that sends every solid you can see to Bambu Studio. The file is in millimeters. You do not select bodies. Hide a body (light bulb off) to leave it out.

Works on Windows and Mac from the same folder.

## Install it once

1. Unzip so you have a folder named `SendToBambu`. Do not rename it, and do not pull the files out.
2. In Fusion: **Utilities → Add-Ins → Scripts and Add-Ins**.
3. Open the **Add-Ins** tab. Next to **My Add-Ins**, click the green **+** and choose the `SendToBambu` folder.
4. Select **Send to Bambu**, check **Run on Startup**, then click **Run**.

The button is in the Design workspace, on a panel named **Bambu Print**.

## Send a part

1. Open the design. Hide anything you do not want printed.
2. Click **Send to Bambu**.
3. Bambu Studio opens. Slice and print there.

## You already installed an older copy

1. In Scripts and Add-Ins, select **Send to Bambu** and click **Stop**.
2. Quit Fusion completely. Closing the design is not enough.
3. Unzip the new download on top of the old `SendToBambu` folder and replace it.
4. Open Fusion and click **Run**.

## If Bambu Studio does not open

Click **Bambu Print Settings → Locate Bambu Studio** and pick:

| | Pick this |
|---|---|
| Windows | `C:\Program Files\Bambu Studio\bambu-studio.exe` |
| Mac | `/Applications/BambuStudio.app` |

On a Mac, choose the `.app` itself even if Finder treats it like a folder.

## If something looks wrong

- **Wrong size in Bambu.** You still have an older copy. Stop, replace the whole folder, quit Fusion, then Run.
- **No body found.** Turn the light bulb on. Hidden bodies and surfaces are skipped.
- **Button missing.** Scripts and Add-Ins → Send to Bambu → Run.
- **Error mentions `scale_binary_stl`.** Fusion is still holding the old files. Stop, replace the whole folder, quit Fusion, then Run.
