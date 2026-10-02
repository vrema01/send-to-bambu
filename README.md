# Send to Bambu

A Fusion 360 button that sends every visible solid to Bambu Studio, already in millimeters. You do not select bodies. Hide a body to leave it out.

**Share this page:** the steps below are the whole install.

Download: [SendToBambu.zip](https://github.com/vrema01/send-to-bambu/releases/latest/download/SendToBambu.zip)

A longer page with the same steps is in [docs/index.html](docs/index.html).

## Install it once

1. Unzip `SendToBambu.zip`. You should get one folder named `SendToBambu`. Do not rename it.
2. In Fusion: **Utilities → Add-Ins → Scripts and Add-Ins**.
3. Open the **Add-Ins** tab. Next to **My Add-Ins**, click the green **+** and choose that folder.
4. Select **Send to Bambu**, check **Run on Startup**, then click **Run**.

The button is in Design, on the **Bambu Print** panel.

## Send a part

1. Hide any body you do not want (light bulb off). You do not select anything.
2. Click **Send to Bambu**.
3. Each visible solid opens as its own object in Bambu Studio. Slice and print there.

Leave the format on 3MF. STL combines every body into one mesh.

## Updating an older copy

1. Scripts and Add-Ins → Send to Bambu → **Stop**.
2. Quit Fusion completely.
3. Replace the old `SendToBambu` folder with the new unzip.
4. Open Fusion and click **Run**.

## If Bambu Studio does not open

**Bambu Print Settings → Locate Bambu Studio**

- Windows: `C:\Program Files\Bambu Studio\bambu-studio.exe`
- Mac: `/Applications/BambuStudio.app` (pick the app itself)

## If something looks wrong

- **Wrong size.** Stop the add-in, replace the whole folder, quit Fusion, then Run.
- **No body found.** Turn the light bulb on. Surfaces are skipped.
- **No button.** Scripts and Add-Ins → Send to Bambu → Run.
- **Error says `scale_binary_stl`.** Same as wrong size: replace the whole folder and quit Fusion before you Run.

The Fusion add-in source is in `fusion-addin/SendToBambu`. This repository also contains the small install website.
