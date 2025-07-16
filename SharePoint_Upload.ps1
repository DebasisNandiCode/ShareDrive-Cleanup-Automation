param (
    [Parameter(Mandatory = $true)]
    [string]$Location,
    [Parameter(Mandatory = $true)]
    [string]$OneDriveURL,
    [Parameter(Mandatory = $true)]
    [string]$OneFolderOneDrive
)

Add-Type -Path "D:\XXXX\XXXX\ISAPI\Microsoft.SharePoint.Client.dll"
Add-Type -Path "D:\XXXX\XXXX\ISAPI\Microsoft.SharePoint.Client.Runtime.dll"

if ($OneDriveURL[-1] -eq "/") 
{
    $OneDriveURL = $OneDriveURL.Substring(0, $OneDriveURL.Length - 1)
}
# Get the current date in UTC
$currentDateUtc = [DateTime]::UtcNow
# Get the Eastern Standard Time timezone
$estTimeZone = [System.TimeZoneInfo]::FindSystemTimeZoneById("Eastern Standard Time")
# Convert the current UTC date to EST
$currentDateEst = [System.TimeZoneInfo]::ConvertTimeFromUtc($currentDateUtc, $estTimeZone)
$currentDateEst = $currentDateEst.AddDays(-1)

# Function to recursively upload a folder and its contents
Function Upload-FolderContents($File, $TargetFolderF) {
    # $Files = Get-ChildItem $LocalFolder -File
    # ForEach ($File in $Files) {
    $FileStream = [System.IO.File]::OpenRead($File)
    $FileCreationInfo = New-Object Microsoft.SharePoint.Client.FileCreationInformation
    $FileCreationInfo.Overwrite = $true
    $FileCreationInfo.ContentStream = $FileStream
    $fileName = Split-Path -Path $File -Leaf
    $FileCreationInfo.URL = $fileName

    #-----------------------------
    $Upload = $TargetFolderF.Files.Add($FileCreationInfo)
    $Ctx.Load($Upload)
    $Ctx.ExecuteQuery()
    $FileStream.Close() # Close the file stream after upload
    Write-Host "SharePoint file uploaded successfully: " , $FileCreationInfo.URL
    #-----------------------------
    
}

# Specify the User account for an Office 365 global admin in your organization
$AdminAccount = "automation.team@xxxxxxxx.com"
$AdminPass = "Password@#1234"

$DocumentLibrary = "Documents"

$TargetFolderName = $OneFolderOneDrive

# Connect and Load OneDrive Library and Root Folder
$SecurePass = ConvertTo-SecureString $AdminPass -AsPlainText -Force
$Ctx = New-Object Microsoft.SharePoint.Client.ClientContext($OneDriveURL)
$Credentials = New-Object Microsoft.SharePoint.Client.SharePointOnlineCredentials($AdminAccount, $SecurePass)
$Ctx.Credentials = $Credentials

$TargetFolderTodayN
Try {
    $List = $Ctx.Web.Lists.GetByTitle($DocumentLibrary)
    $Ctx.Load($List)
    $Ctx.Load($List.RootFolder)
    $Ctx.ExecuteQuery()

    # Setting Target Folder
    $TargetFolder = $null
    if ($TargetFolderName) {
        # Write-Host $List.RootFolder.ServerRelativeUrl
        $TargetFolderRelativeUrl = $List.RootFolder.ServerRelativeUrl  + $TargetFolderName
        Write-Host '$TargetFolderRelativeUrl' , $TargetFolderRelativeUrl
        # if // is there then make it singel /
        $TargetFolderRelativeUrl = $TargetFolderRelativeUrl.Replace("//", "/")
          $TargetFolder = $Ctx.Web.GetFolderByServerRelativeUrl($TargetFolderRelativeUrl)
        $TargetFolder.Context.ExecuteQuery()
        # Write-Host '$TargetFolder.Name'
        # Write-Host $TargetFolder.Name
        $Ctx.Load($TargetFolder)
        $Ctx.ExecuteQuery()
        
        $TargetFolderTodayN = $Ctx.Web.GetFolderByServerRelativeUrl($TargetFolderRelativeUrl)
        # Write-Host $TargetFolderTodayN
        # Write-Host  $TargetFolderRelativeUrlTodayFolder
        $Ctx.Load($TargetFolderTodayN)
        $Ctx.ExecuteQuery()

        if (!$TargetFolderTodayN.Exists) {
            Throw "$TargetFolderName - the target folder does not exist in the OneDrive root folder."
        }
    }
    else {
        $TargetFolder = $List.RootFolder.ToString()
    }


    $value = $Location
    Write-Host $value

    Upload-FolderContents $value $TargetFolderTodayN

}
catch {
    Write-Host $_.Exception.Message -ForegroundColor "Red"
}

