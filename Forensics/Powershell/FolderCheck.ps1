<#
.SYNOPSIS
Reports the Name, Creation, and Last Modified timestamps for every subfolder of a given folder.

.DESCRIPTION
Searches a given folder and returns the Name, Modification timestamp and Creation timestamp
($SI) for any subfolders, writing the results to a CSV file.

.PARAMETER DirectoryPath
The folder to scan for subfolders.

.PARAMETER OutputPath
Path/filename of the CSV to create.

.EXAMPLE
.\FolderCheck.ps1 -DirectoryPath C:\Users -OutputPath C:\DFIRLOGS\folders.csv
#>

param(
    [Parameter(Mandatory=$true)][string]$DirectoryPath,
    [Parameter(Mandatory=$true)][string]$OutputPath
    )

$subfolders = Get-ChildItem -Path $DirectoryPath -Directory

$folderInfo = @()

foreach ($subfolder in $subfolders) {
    $folderName = $subfolder.Name
    $lastModifiedDate = $subfolder.LastWriteTime
    $creationDate = $subfolder.CreationTime
    $folderObject = New-Object PSObject -Property @{
        FolderName = $folderName
        LastModifiedDate = $lastModifiedDate
        CreationDate = $creationDate
    }
    $folderInfo += $folderObject
}

$folderInfo | Export-Csv -Path $OutputPath -NoTypeInformation
