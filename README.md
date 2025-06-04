# NIKKE Spine Viewer
A simple tool that uses a modified version of [anosu's Spine Viewer](https://github.com/anosu/Spine-Viewer) to view [NIKKE](https://nikke-en.com/) Spine animations or any other compatible game that uses Spine.


### The script to download the viewer uses [NicKoehler's mediafire bulk downloader](https://github.com/NicKoehler/mediafire_bulk_downloader).

## Portable Version (old GUI):
If you don't want to install the stuff below to use the scripts you can download this portable version ready for usage.


<p align="center">
  👉<a href="https://www.mediafire.com/file/dkj0lvvnu3rn771/NIKKESpineViewer.7z/file"><strong>DOWNLOAD HERE</strong></a>👈
</p>

## Executable Usage:

1. Double-click on _NIKKESpineViewer.exe_.
2. The viewer will ask the user for the path to NMM "mods" folder, click OK on the message box.
3. You will see this GUI:


<img src="https://files.catbox.moe/i42ie6.png" width="700"/>


4. Click on `Browse...` and navigate to your NMM mods folder and select it.
5. The viewer will show the list with your mods, from here you can preview them or rename them.


<img src="https://files.catbox.moe/cg4fpd.png" width="700"/>


### Buttons:

`Preview`: Open the corresponding skeleton viewer version to see the Spine animation.

`Refresh Mods List`: If you renamed, moved or deleted the mods then use this button to refresh the mods list to show the changes.

`Rename`: Renames your mods directly from the GUI. It's not necessary to use `_` in this case.

# Update 2.0 Version:

Better style on the GUI, this version works as script instead. The list of characters is updated automatically now; and I added a search bar to filter your mods list by author, character, standing, aim, cover, etc.

<img src="https://files.catbox.moe/fatv79.png" width="700"/>


## Requirements to use the scripts:

  - Double-click on _install_requirements.bat_ to install the required dependencies and Python 3.13.
  - Download and install [Microsoft C++ Build Tools](https://aka.ms/vs/17/release/vs_BuildTools.exe), and after that install the necessary libraries following [this video](https://files.catbox.moe/vqsuix.mp4).
  
  NOTE: The requirements listed in "requirements.txt" are only for my GUI script, you will need to install the ones necessary for anosu's Spine Viewer separately (Electron, Node.js, etc).

## Usage:

1. Double-click on _NIKKESpineViewer.bat_.
2. The viewer will ask the user for the path to NMM "mods" folder, click OK on the message box.
3. Click on `Browse...` and navigate to your NMM mods folder and select it.
4. The viewer will show the list with your mods, from there you can preview them or rename them.
5. You can create a shortcut to the viewer on your Desktop with _CREATE_SHORTCUT.bat_.
