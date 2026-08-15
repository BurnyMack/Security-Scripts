<#

.SYNOPSIS
Script to display the Creation, Access and Write times of files in a given folder.

.DESCRIPTION
This script reports key details about files in a given folder. It identifies the filename, filesize (in bytes), creation/access/write times.
If no path is provided with the execution it looks at files in the current path.

.PARAMETER targetPath
Folder to scan for file timestamps. Defaults to the current directory.

.PARAMETER outputPath
Folder to write timestamps.csv into. If omitted, results are only displayed on screen, not saved.

.EXAMPLE
timestamps.ps1

.EXAMPLE
timestamps.ps1 -targetPath C:\Windows\temp -outputPath D:\incidentresponse\

.LINK
https://github.com/TazWake/

.NOTES
Under development

#>
param(
    [Parameter(Mandatory=$false)][string]$targetPath,
    [Parameter(Mandatory=$false)][string]$outputPath
    )
function outData {
    $output = "$outputPath\timestamps.csv"
    if ((Test-Path -Path $output) -eq $false) {
        try {
            New-Item $output -ItemType file -ErrorAction Stop | Out-Null
            'Name,Size(bytes),Creation Time (UTC),Last Access Time (UTC), Last Write Time (UTC)' | Out-File -FilePath $output -Append -Encoding ascii -Force -ErrorAction Stop
        } catch {
            Write-Error "Failed to create output file '$output': $_"
            throw
        }
    }
    return $output
}
function writeCSV ($scanpath, $outpath) {
    $files = Get-ChildItem $scanpath -Recurse -force
    foreach ($file in $files) {
        $box = Get-ItemProperty $file.FullName
        $data = $box.FullName + "," + $box.Length + "," + $box.CreationTimeUtc + "," + $box.LastAccessTimeUtc + "," + $box.LastWriteTimeUtc
        try {
            $data | Out-File -FilePath $outpath -Append -Encoding ascii -Force -ErrorAction Stop
        } catch {
            Write-Error "Failed to write timestamp record for '$($box.FullName)': $_"
        }
        }
}
$scanpath = "*"
if ($targetPath) {
    $scanpath = $targetPath
    }
Write-Host "Starting collection"
if ($outputPath) {
    $filepath = outData
    writeCSV $scanpath $filepath
}
Get-ItemProperty -Path $scanpath | Format-list -Property Name, Length, CreationTimeUtc, LastAccessTimeUtc, LastWriteTimeUtc
Write-Host "Collection completed"
