import os
import sys
import json
import csv
import subprocess
import shutil
import tempfile
import UnityPy
import re
import urllib.request
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QScrollArea, QHBoxLayout, QLabel, QLineEdit,
    QFileDialog, QMessageBox, QProgressDialog
)
from PyQt6.QtGui import QIcon, QColor, QPalette
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer

def download_file(url, destination):
    try:
        urllib.request.urlretrieve(url, destination)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

class AssetExtractor(QThread):
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(str, str, str)

    def __init__(self, bundle_path, spine_assets_dir):
        super().__init__()
        self.bundle_path = bundle_path
        self.spine_assets_dir = spine_assets_dir
        self.cancelled = False

    def run(self):
        try:
            bundle_name = os.path.splitext(os.path.basename(self.bundle_path))[0]
            output_dir = os.path.join(self.spine_assets_dir, bundle_name)

            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            os.makedirs(output_dir, exist_ok=True)

            self.progress_signal.emit(10, "Loading bundle...")
            env = UnityPy.load(self.bundle_path)
            self.progress_signal.emit(20, "Scanning assets...")

            spine_assets = {'skel': None, 'atlas': None, 'textures': []}
            objects = list(env.objects)
            for i, obj in enumerate(objects):
                if self.cancelled:
                    break
                progress = 20 + int((i / len(objects)) * 70)
                self.progress_signal.emit(progress, f"Processing {obj.type.name}...")

                try:
                    data = obj.read()

                    if obj.type.name == "Texture2D":
                        texture_name = f"{data.m_Name}.png"
                        texture_path = os.path.join(output_dir, texture_name)
                        data.image.save(texture_path)
                        spine_assets['textures'].append(texture_path)

                    elif obj.type.name == "TextAsset":
                        asset_name = data.m_Name
                        asset_path = os.path.join(output_dir, asset_name)

                        if asset_name.endswith('.skel') or '.skel.' in asset_name:
                            spine_assets['skel'] = asset_path
                        elif asset_name.endswith('.atlas') or '.atlas.' in asset_name:
                            spine_assets['atlas'] = asset_path

                        with open(asset_path, "wb") as f:
                            f.write(data.m_Script.encode("utf-8", "surrogateescape"))

                except Exception as e:
                    print(f"Error processing asset: {e}")

            if self.cancelled:
                shutil.rmtree(output_dir)
                self.finished_signal.emit(None, None, "Extraction cancelled")
            else:
                self.progress_signal.emit(95, "Finalizing...")
                if spine_assets['skel']:
                    self.finished_signal.emit(
                        output_dir,
                        spine_assets['skel'],
                        "Extraction complete"
                    )
                else:
                    self.finished_signal.emit(
                        output_dir,
                        None,
                        "No Spine skeleton file found"
                    )
                self.progress_signal.emit(100, "Done")

        except Exception as e:
            self.finished_signal.emit(None, None, f"Extraction failed: {str(e)}")

    def cancel(self):
        self.cancelled = True

class SpineViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_file = "spine_viewer_settings.json"
        self.setWindowTitle("NIKKE Spine Viewer")
        self.setGeometry(100, 100, 800, 600)
        self.viewer_processes = []

        # Check for CSV updates before loading
        self.check_csv_updates()
        self.character_map = self.load_character_map()
        self.settings = self.load_settings()

        # Apply Windows 11 dark theme
        self.set_windows11_dark_theme()

        main_layout = QVBoxLayout()

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Mods Folder:"))

        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Path to your mods folder")
        if self.settings.get("mods_folder"):
            self.folder_edit.setText(self.settings["mods_folder"])
        folder_layout.addWidget(self.folder_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_mods_folder)
        folder_layout.addWidget(browse_btn)

        refresh_btn = QPushButton("Refresh Mods List")
        refresh_btn.clicked.connect(self.load_mods)
        folder_layout.addWidget(refresh_btn)

        main_layout.addLayout(folder_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)

        self.current_extraction = None
        self.progress_dialog = None

        self.verify_mods_folder()
        self.folder_edit.textChanged.connect(self.folder_path_changed)

    def check_csv_updates(self):
        """Check for updates to Codes_and_Names.csv from GitHub"""
        github_url = "https://raw.githubusercontent.com/kxdekxde/nikke-spine-viewer/main/Codes_and_Names.csv"
        local_path = "Codes_and_Names.csv"
        
        try:
            # Download the file to a temporary location
            temp_path = os.path.join(tempfile.gettempdir(), "temp_Codes_and_Names.csv")
            if download_file(github_url, temp_path):
                # Compare with local file if it exists
                if os.path.exists(local_path):
                    with open(local_path, 'r', encoding='utf-8') as local_file:
                        local_content = local_file.read()
                    with open(temp_path, 'r', encoding='utf-8') as temp_file:
                        remote_content = temp_file.read()
                    
                    if local_content != remote_content:
                        # Files are different, replace local with remote
                        shutil.copy(temp_path, local_path)
                        print("Updated Codes_and_Names.csv from GitHub")
                else:
                    # Local file doesn't exist, create it
                    shutil.copy(temp_path, local_path)
                    print("Downloaded Codes_and_Names.csv from GitHub")
                
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except Exception as e:
            print(f"Error checking for CSV updates: {e}")

    def set_windows11_dark_theme(self):
        """Apply Windows 11 style dark theme to the application"""
        app = QApplication.instance()
        
        # Enable dark title bar on Windows
        if sys.platform == "win32":
            try:
                from ctypes import windll, byref, sizeof, c_int
                hwnd = int(self.winId())
                for attribute in [19, 20]:  # Try both dark mode attributes
                    try:
                        value = c_int(1)
                        windll.dwmapi.DwmSetWindowAttribute(
                            hwnd,
                            attribute,
                            byref(value),
                            sizeof(value)
                        )
                    except Exception as e:
                        print(f"Dark title bar not supported (attribute {attribute}): {e}")
            except Exception as e:
                print(f"Dark title bar initialization failed: {e}")

        # Create dark palette with correct parameter order
        palette = QPalette()
        # Regular colors
        palette.setColor(QPalette.ColorRole.Window, QColor(32, 32, 32))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(120, 120, 120))

        # Disabled colors - correct parameter order
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))

        app.setPalette(palette)

        # Set style sheet for additional styling with blue scrollbar
        self.setStyleSheet("""
            QWidget {
                background-color: #202020;
                color: #f0f0f0;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 9pt;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
            QScrollArea {
                border: none;
            }
            QLineEdit {
                background-color: #252525;
                color: #f0f0f0;
                padding: 5px;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                selection-background-color: #3a6ea5;
                selection-color: #ffffff;
            }
            QLineEdit:disabled {
                background-color: #1a1a1a;
                color: #7f7f7f;
            }
            QProgressDialog {
                background-color: #202020;
                color: #f0f0f0;
            }
            QProgressBar {
                background-color: #252525;
                color: #f0f0f0;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3a6ea5;
                border-radius: 3px;
            }
            QLabel {
                color: #f0f0f0;
            }
            QMessageBox {
                background-color: #202020;
            }
            QMessageBox QLabel {
                color: #f0f0f0;
            }
            QScrollBar:vertical {
                border: none;
                background: #252525;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #1a4b8c;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical {
                border: none;
                background: none;
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                background: #252525;
                height: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background: #1a4b8c;
                min-width: 20px;
                border-radius: 5px;
            }
        """)

    def load_character_map(self):
        character_map = {}
        try:
            with open("Codes_and_Names.csv", newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    character_map[row['ID']] = row['CHARACTER']
        except Exception as e:
            print(f"Error loading character map: {e}")
        return character_map

    def extract_id_from_filename(self, filename):
        for key in self.character_map.keys():
            if key in filename:
                return key
        return None

    def format_display_name(self, name):
        return name.replace('_', ' ')

    def get_spine_assets_dir(self):
        spine_dir = os.path.join(tempfile.gettempdir(), "SpineAssets")
        os.makedirs(spine_dir, exist_ok=True)
        return spine_dir

    def browse_mods_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Mods Folder", os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.folder_edit.setText(folder)
            self.settings["mods_folder"] = folder
            self.save_settings()
            self.load_mods()

    def folder_path_changed(self, text):
        self.settings["mods_folder"] = text
        self.save_settings()
        self.load_mods()

    def load_settings(self):
        default_settings = {
            "mods_folder": ""
        }
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return default_settings

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def verify_mods_folder(self):
        if not self.settings.get("mods_folder") or not os.path.exists(self.settings["mods_folder"]):
            QMessageBox.information(
                self, "Select Mods Folder",
                "Please enter or browse to your mods folder path",
                QMessageBox.StandardButton.Ok
            )
        else:
            self.load_mods()

    def load_mods(self):
        mods_folder = self.settings.get("mods_folder", "")
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if mods_folder and os.path.exists(mods_folder):
            for item in sorted(os.listdir(mods_folder)):
                item_path = os.path.join(mods_folder, item)
                if os.path.isdir(item_path) or item.startswith('.') or item.endswith('.json'):
                    continue
                self.add_mod_item(item, item_path)

    def add_mod_item(self, original_name, file_path):
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)
        item_layout.setSpacing(10)

        preview_btn = QPushButton("Preview")
        preview_btn.setFixedWidth(100)
        preview_btn.clicked.connect(lambda _, p=file_path: self.preview_file(p))
        item_layout.addWidget(preview_btn)

        self.name_edit = QLineEdit(self.format_display_name(original_name))
        self.name_edit.setStyleSheet("color: #f0f0f0;")
        self.name_edit.setMinimumWidth(300)
        self.name_edit.setProperty("original_path", file_path)
        item_layout.addWidget(self.name_edit)

        character_id = self.extract_id_from_filename(original_name)
        character_name = self.character_map.get(character_id, "Unknown")
        character_label = QLabel(character_name)
        character_label.setStyleSheet("color: #a6a6a6;")
        character_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        character_label.setMinimumWidth(150)
        item_layout.addWidget(character_label)

        rename_btn = QPushButton("Rename")
        rename_btn.setFixedWidth(100)
        rename_btn.clicked.connect(self.rename_file)
        item_layout.addWidget(rename_btn)

        self.scroll_layout.addWidget(item_widget)

    def rename_file(self):
        btn = self.sender()
        if not btn:
            return
            
        item_widget = btn.parentWidget()
        if not item_widget:
            return
            
        name_edit = None
        original_path = None
        for child in item_widget.children():
            if isinstance(child, QLineEdit):
                name_edit = child
                original_path = child.property("original_path")
                break
                
        if not name_edit or not original_path:
            return
            
        new_name = name_edit.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Error", "Name cannot be empty", QMessageBox.StandardButton.Ok)
            return
            
        new_filename = new_name.replace(' ', '_')
        dir_path = os.path.dirname(original_path)
        old_filename = os.path.basename(original_path)
        extension = os.path.splitext(old_filename)[1]
        new_path = os.path.join(dir_path, new_filename + extension)
        
        try:
            os.rename(original_path, new_path)
            name_edit.setProperty("original_path", new_path)
            
            character_id = self.extract_id_from_filename(new_filename)
            character_name = self.character_map.get(character_id, "Unknown")
            
            for child in item_widget.children():
                if isinstance(child, QLabel) and child.text() not in ["Preview", "Rename"]:
                    child.setText(character_name)
                    break
                    
            QMessageBox.information(self, "Success", "File renamed successfully", QMessageBox.StandardButton.Ok)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rename file: {str(e)}", QMessageBox.StandardButton.Ok)

    def preview_file(self, file_path):
        if file_path.endswith('.skel') or file_path.endswith('.json'):
            self.preview_animation(file_path)
        else:
            self.extract_and_preview(file_path)

    def extract_and_preview(self, bundle_path):
        spine_assets_dir = self.get_spine_assets_dir()
        self.progress_dialog = QProgressDialog(
            f"Loading assets from {os.path.basename(bundle_path)}...",
            "Cancel", 0, 100, self)
        self.progress_dialog.setWindowTitle("Loading Assets")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.canceled.connect(self.cancel_extraction)

        self.current_extraction = AssetExtractor(bundle_path, spine_assets_dir)
        self.current_extraction.progress_signal.connect(self.update_progress)
        self.current_extraction.finished_signal.connect(self.extraction_complete)
        self.current_extraction.start()

        self.progress_dialog.show()

    def update_progress(self, value, message):
        if self.progress_dialog:
            self.progress_dialog.setValue(value)
            self.progress_dialog.setLabelText(message)

    def cancel_extraction(self):
        if self.current_extraction and self.current_extraction.isRunning():
            self.current_extraction.cancel()
        if self.progress_dialog:
            self.progress_dialog.close()
        self.progress_dialog = None

    def extraction_complete(self, output_dir, skel_path, message):
        if self.progress_dialog:
            self.progress_dialog.close()
        if skel_path:
            self.preview_animation(skel_path)
        else:
            if output_dir:
                QMessageBox.warning(
                    self, "Extraction Complete",
                    f"{message}\n\nExtracted assets to:\n{output_dir}",
                    QMessageBox.StandardButton.Ok
                )
            else:
                QMessageBox.critical(
                    self, "Extraction Failed",
                    message,
                    QMessageBox.StandardButton.Ok
                )

    def preview_animation(self, animation_path):
        # Get the path to the Spine Viewer executable
        viewer_path = os.path.join(os.path.dirname(__file__), "SpineViewer-anosu", "SpineViewer.exe")
        
        if not os.path.exists(viewer_path):
            QMessageBox.critical(
                self, "Error",
                f"Spine Viewer not found at path: {viewer_path}",
                QMessageBox.StandardButton.Ok
            )
            return

        try:
            # Run the Spine Viewer with the animation file
            subprocess.Popen(
                [viewer_path, animation_path],
                shell=True
            )
            
            QTimer.singleShot(500, self.bring_to_front)
            
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to launch Spine Viewer:\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )

    def bring_to_front(self):
        self.raise_()
        self.activateWindow()
        self.showNormal()

    def closeEvent(self, event):
        shutil.rmtree(self.get_spine_assets_dir(), ignore_errors=True)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    if os.path.exists("icon.png"):
        app.setWindowIcon(QIcon("icon.png"))
    
    viewer = SpineViewer()
    viewer.show()
    sys.exit(app.exec())