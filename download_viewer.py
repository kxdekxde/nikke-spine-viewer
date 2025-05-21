import os
import requests
import zipfile
from tqdm import tqdm

# Configuration
direct_url = "https://download1527.mediafire.com/i4ma8jwtjydg0pyXvGY76z5CNyKiq-J4TOqFJXln8XDHKzFh8YDcF0axLwl_TN8jt2oA_5_ly4P9UjQJp5-v2WWMth5_q1ByVW9qyinQ5SOGP94jlfiDYybEEFPL7Ui21TLtgzHVI_0QMLxmcbwEh60FOV0BzWSQfvDLQdgGAWIq/r9v1f68wz5zltuy/SpineViewer.zip"
output_folder = "SpineViewer-anosu"
zip_filename = "SpineViewer.zip"
zip_path = os.path.join(output_folder, zip_filename)

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Skip download if the zip already exists
if not os.path.exists(zip_path):
    print(f"[*] Downloading Viewer...")
    response = requests.get(direct_url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    block_size = 8192

    with open(zip_path, 'wb') as f, tqdm(
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
        desc=zip_filename,
        initial=0
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=block_size):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))
    print(f"[+] Downloaded to {zip_path}")
else:
    print(f"[✓] ZIP file already exists at {zip_path}. Skipping download...")

# Extract the zip
print("[*] Extracting contents...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(output_folder)
print(f"[+] Extracted to {output_folder}")

# Delete the zip
os.remove(zip_path)
print("[✓] Cleaned up .zip file. Done!")
