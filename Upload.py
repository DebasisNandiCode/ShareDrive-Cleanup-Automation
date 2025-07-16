import subprocess
import os

def upload_file_to_sharepoint(local_file, one_drive_url, one_drive_folder):
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ps_file = os.path.join(base_dir, "SharePoint_Upload.ps1")

    if not os.path.exists(local_file):
        print(f"Error: File not found: {local_file}")
        return False

    command = [
        "powershell",
        "-ExecutionPolicy", "ByPass",
        "-File", ps_file,
        "-Location", local_file,
        "-OneDriveURL", one_drive_url,
        "-OneFolderOneDrive", one_drive_folder
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        print("Upload successful.")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Upload failed: {e.stderr}")
        return False
