<#
.SYNOPSIS
A PowerShell script to assist incident responders in hunting down suspicious network connections

.DESCRIPTION
Using network IOCs, huntBotNets searches for connections to identified malicious IP addresses.
Output is stored into a text file.

.PARAMETER BotNetIP
The IP address to search current network connections for. Mandatory.

.PARAMETER OutPath
Directory to write conncheck.txt into. Defaults to the current directory.

.Example
botnetcheck.ps1 -BotNetIP 192.168.2.1

.Example
botnetcheck.ps1 -BotNetIP 192.168.2.1 -OutPath C:\DFIRLOGS\

.LINK
https://github.com/TazWake/
#>

param(
     [Parameter(Mandatory=$true)][string]$BotNetIP,
     [string]$OutPath = ".\"
     )

# Initial data for logging
$HostName = (Get-Item env:\Computername).Value
$DirPath = (Get-Item env:\userprofile).Value
$UserName = (Get-Item env:\USERNAME).Value
$Date = (Get-Date).ToString('dd.MM.yyyy')
$LogFile = Join-Path $OutPath "conncheck.txt"

# Notify User
Write-Host "[+] Beginning Data Collection on $HostName"

# Write log
Add-Content $LogFile "------------------------"
Add-Content $LogFile "- Checking for BotNets -"
Add-Content $LogFile "------------------------"
$b = "Hostname: " + $HostName
Add-Content $LogFile $b
$b = "Path: " + $DirPath
Add-Content $LogFile $b
$b = "User Name: " + $UserName
Add-Content $LogFile $b
$b = "Date: " + $Date
Add-Content $LogFile $b
Add-Content $LogFile "------------------------"


$cmd = netstat -nao | Select-String $BotNetIP

foreach ($element in $cmd)
{
    $data = $element -split ' ' | Where-Object {$_ -ne ''}
    $proc = Get-Process | Where-Object {$_.ID -eq $data[4]}
    $ConnCheck = @{
        'Local IP : Port#'=$data[1];
        'Remote IP : Port#'=$data[2];
        'Process ID'= $data[4];
        'Process Name'=$proc.Name
        'Process File Path'=$proc.path
        'Process Start Time'=$proc.starttime
        'Associated DLLs and Path'=$proc.Modules |Select-Object @{Name='Modules';Expression={$_.filename -join '; ' } } |Out-String
        }
    New-Object -TypeName psobject -Property $ConnCheck | Out-File -Append $LogFile -Encoding ascii
 }

 # Notify User
Write-Host "[+] Collection Complete - Results in $LogFile"
