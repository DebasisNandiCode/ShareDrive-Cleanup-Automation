# ShareDrive-Cleanup-Automation

This project automates the deletion of .xlsx and .csv files from a shared drive folder, logs the activity, updates an email template with the deletion count, uploads the email details to SharePoint, and triggers an email notification via Power Automate.

## Features

- Deletes .xlsx and .csv files from a specified shared drive folder
- Maintains detailed logs in a database
- Updates an email template with the count of deleted files
- Uploads the email details to SharePoint
- Integrates with Power Automate for email notifications

## Prerequisites

- Python 3.7+
- PowerShell 5.1+
- Access to the shared drive folder
- SharePoint access with appropriate permissions
- SQL Server database for logging
- Power Automate flow configured to trigger on SharePoint file upload

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ShareDrive-Cleanup-Automation.git
   cd ShareDrive-Cleanup-Automation 

2. Create a .env file in the root directory:
  SHARE_DRIVE_PATH=\\10.xxx.xxx.254\Enterprise\reporting\reports
  ONE_DRIVE_URL=https://yourcompany.sharepoint.com/sites/your-site
  ONE_DRIVE_FOLDER=/YourTargetFolder
  CentDB_HOST=your-db-server
  CentDB_DATABASE=your-db-name
  CentDB_USER=your-db-user
  CentDB_PASSWORD=your-db-password

## Configuration
  1. SharePoint Configuration:
      Update the SharePoint DLL paths in SharePoint_Upload.ps1
      Set the correct admin credentials in the same file
  2. Email Template:
      Modify email_details_template.json to customize the email content
      Update recipient emails in the template
  3. Power Automate:
      Set up a flow that triggers when email_details.json is uploaded to SharePoint
      Configure the flow to send an email using the JSON content


Thank you.

Developed by Debasis Nandi
