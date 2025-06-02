import os
import shutil
import zipfile

# Configuration
output_folder = "SpineViewer-anosu"
zip_filename = "SpineViewer.zip"
zip_path = os.path.join(output_folder, zip_filename)
files_to_keep = [zip_filename, "LICENSE.txt"]  # Files to skip during cleaning

def clean_folder_keep_files(folder_path, keep_files):
    """Clean folder contents except for the specified files"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return
    
    for filename in os.listdir(folder_path):
        if filename in keep_files:
            continue  # Skip files we want to keep
        
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"[!] Failed to delete {file_path}: {e}")

# Skip download – assume zip file already exists
if not os.path.exists(zip_path):
    print(f"[!] ZIP file not found at {zip_path}. Cannot proceed.")
    exit(1)
else:
    print(f"[✓] ZIP file found at {zip_path}. Cleaning folder before extraction...")

# Clean the folder (keep only the zip file and LICENSE.txt)
clean_folder_keep_files(output_folder, files_to_keep)
print("[✓] Folder cleaned (kept .zip file and LICENSE.txt)")

# Extract the zip
print("[*] Extracting contents...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(output_folder)
print(f"[+] Extracted to {output_folder}")

# Final cleanup - delete the zip
try:
    os.remove(zip_path)
    print("[✓] Cleaned up .zip file. Done!")
except Exception as e:
    print(f"[!] Failed to delete zip file: {e}")