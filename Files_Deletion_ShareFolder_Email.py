import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from Logger import Logger
from dotenv import load_dotenv
from Upload import upload_file_to_sharepoint
import json


# Load environment variables
load_dotenv()

# Initialize Logger
logger = Logger()

# Configurable Variables
shareDrive_Path = os.getenv("SHARE_DRIVE_PATH")

# Validate environment variables
if not shareDrive_Path:
    raise ValueError("SHARE_DRIVE_PATH environment variable is not set.")

# Step 1: Delete .xlsx and .csv files
deleted_files = []

if os.path.exists(shareDrive_Path):
    for file in os.listdir(shareDrive_Path):
        file_path = os.path.join(shareDrive_Path, file)
        if os.path.isfile(file_path) and file.endswith(('.xlsx', '.csv')):
            try:
                os.remove(file_path)
                deleted_files.append(file)
            except Exception as e:
                logger.log_to_database(
                    295, "Failed", "SM&B Files", "Failed",
                    f"Failed to delete {file_path}: {e}",
                    "Error", "SM&B Files deletion failed"
                )
                print(f"Failed to delete {file_path}: {e}")
    
    if deleted_files:
        logger.log_to_database(
            295, "Success", "SM&B Files", "Success",
            f"Deleted {len(deleted_files)} files successfully from Share Drive Path",
            "Success", "SM&B Files deleted"
        )
else:
    logger.log_to_database(
        295, "Warning", "SM&B Files", "Error",
        "Share Drive Path not found",
        "Error", "SM&B Files Path not found"
    )
    print("Share Drive Folder Path NOT Found!")


# Upload JSON file to SharePoint after deletion

base_dir = os.path.dirname(os.path.abspath(__file__))
# Use the template file as the source
template_file = os.path.join(base_dir, "email_details_template.json")
local_file = os.path.join(base_dir, "email_details.json")

# Read the template
with open(template_file, "r", encoding="utf-8") as f:
    email_details = json.load(f)

# Update the HTML_Body with the number of files deleted
num_deleted = len(deleted_files)
if "HTML_Body" in email_details:
    email_details["HTML_Body"] = email_details["HTML_Body"].replace("{num_deleted}", str(num_deleted))

# Save the updated email_details.json
with open(local_file, "w", encoding="utf-8") as f:
    json.dump(email_details, f, indent=4)


one_drive_url = os.getenv("ONE_DRIVE_URL")
one_drive_folder = os.getenv("ONE_DRIVE_FOLDER")

upload_success = upload_file_to_sharepoint(local_file, one_drive_url, one_drive_folder)

if upload_success:
    logger.log_to_database(
        295, "Success", "SM&B Upload Script", "Success",
        "email_details.json uploaded successfully to SharePoint.",
        "Success", "Upload completed"
    )
else:
    logger.log_to_database(
        295, "Failed", "SM&B Upload Script", "Failed",
        "Failed to upload email_details.json to SharePoint.",
        "Error", "Upload failed"
    )

