import os
import shutil
import zipfile

# Configuration
output_folder = "SpineViewer-anosu"
zip_filename = "SpineViewer.zip"
zip_path = os.path.join(output_folder, zip_filename)

def clean_folder_keep_zip(folder_path, zip_to_keep):
    """Clean folder contents except for the specified zip file"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return
    
    for filename in os.listdir(folder_path):
        if filename == zip_to_keep:
            continue  # Skip the zip file we want to keep
        
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

# Clean the folder (keep only the zip file)
clean_folder_keep_zip(output_folder, zip_filename)
print("[✓] Folder cleaned (only .zip file remains)")

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