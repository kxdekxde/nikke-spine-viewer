# NIKKE Spine Viewer
A simple tool that uses a modified version of [anosu's Spine Viewer](https://github.com/anosu/Spine-Viewer) to view [NIKKE](https://nikke-en.com/) Spine animations or any other compatible game that uses Spine.


## Portable Version:
If you don't want to install the stuff below to use the scripts you can download this portable version ready for usage.


<p align="center">
  👉<a href="https://www.mediafire.com/file/dkj0lvvnu3rn771/NIKKESpineViewer.7z/file"><strong>DOWNLOAD HERE</strong></a>👈
</p>



## Requirements to use the scripts:

  - Download and install [.NET SDK 8](https://dotnet.microsoft.com/en-us/download/dotnet/thank-you/sdk-8.0.404-windows-x64-installer).
  - Download and install [Python](https://www.python.org/downloads/), along with all of the addons included (pip, etc) and enable 'PATH' as well.
  - Download and install [Microsoft C++ Build Tools](https://aka.ms/vs/17/release/vs_BuildTools.exe), and after that install the necessary libraries following [this video](https://files.catbox.moe/vqsuix.mp4).
  - Open CMD and type:
    ```
    pip install UnityPy PyQt6 requests
    ```
    Hit Enter to install.
  
  



## Usage:

1. Double-click on _NIKKESpineViewer.pyw_ and the script will start to download the required files.
2. After to finish the downloads the script will ask the user for the path to NMM "mods" folder, click OK on the message box.
3. You will see this GUI:


<img src="https://files.catbox.moe/i42ie6.png" width="700"/>


4. Click on `Browse...` and navigate to your NMM mods folder and select it.
5. The viewer will show the list with your mods, from here you can preview them or rename them.


<img src="https://files.catbox.moe/cg4fpd.png" width="700"/>


6. This is optional, double-click on _CREATE_SHORTCUT.bat_ if you want to create a shortcut for the viewer on your Desktop.

### Buttons:

`Preview`: Open the corresponding skeleton viewer version to see the Spine animation.

`Refresh Mods List`: If you renamed, moved or deleted the mods then use this button to refresh the mods list to show the changes.

`Rename`: Renames your mods directly from the GUI. It's not necessary to use `_` in this case.

## How to build:
```
pyinstaller --onefile --windowed --icon="icon.ico" ^
--add-data "icon.png;." ^
--add-data "spine_viewer_settings.json;." ^
--add-data "Codes_and_Names.csv;." ^
--add-data "%USERPROFILE%\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\UnityPy\\resources;UnityPy/resources" ^
--additional-hooks-dir=. ^
NIKKESpineViewer.pyw
```



