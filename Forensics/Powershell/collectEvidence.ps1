<#
.SYNOPSIS
Captures essential triage data from a device and stores the resulting files on a removable disk.

.DESCRIPTION
Runs Magnet RAM Capture to image memory, then runs a KAPE !SANS_Triage collection, storing both
under .\Evidence\<computername>\ along with an activity log and MD5 hashes of the captured files.
Takes no parameters - all paths are derived from the current directory and $env:COMPUTERNAME.

.EXAMPLE
.\collectEvidence.ps1

.NOTES
Requirements:
    1. A USB or other storage location large enough to store output.
        NOTE: Bear in mind, memory capture can result in a file approximately 5-10% larger than the system memory. The triage VHDX can be approximately 0.5gb in size.
    2. This script on the root of the USB.
    3. A correctly licenced copy of KAPE with appropriate targets/modules on in a folder called Kape at the root of the USB.
    4. A copy of Magnet Ram Capture (MRC.exe) on root of the USB.

Execution:
    1. Run powershell with Administrator privileges.
    2. Navigate to the USB.
    3. .\collectEvidence.ps1
#>

Write-Host -ForegroundColor Blue "++++++++++++++++++++++++++"
Write-Host -ForegroundColor DarkCyan "+ Triage Data Collection +"
Write-Host -ForegroundColor DarkCyan "+   Starting Collection  +"
Write-Host -ForegroundColor DarkCyan "+       @tazwake         +"
Write-Host -ForegroundColor Blue "++++++++++++++++++++++++++"
# Set up evidence and logging
$EvidenceDir = ".\Evidence\$env:COMPUTERNAME"
$LogFile = "$EvidenceDir\log.txt"
New-Item -ItemType Directory -Path $EvidenceDir -Force | Out-Null
Write-Host -ForegroundColor Gray 'Artifact collection initiated at' $(Get-Date)
Set-Content -Path $LogFile -Value "Evidence collection started: $((Get-Date).ToString())"
Add-Content -Path $LogFile -Value "Initial folder created."

Add-Content -Path $LogFile -Value "Memory capture initiated: $((Get-Date).ToString())"
try {
    .\MRC.exe /accepteula /go /silent
    Start-Sleep -Seconds 3
    Write-Host -ForegroundColor Yellow "[ ] Launching Magnet RAM Capture to collect a memory image."
    Write-Host -ForegroundColor Yellow "[!] This may take a long time. "
    Wait-Process -Name "MRC"
    Write-Host -ForegroundColor DarkYellow "[X] Capture complete, logging OS build data. Renaming evidence."
    [System.Environment]::OSVersion.Version > "$EvidenceDir\OS_build_version.txt"
    Get-ChildItem -Filter 'MagnetRAMCapture*' -Recurse | Rename-Item -NewName {$_.name -replace 'MagnetRAMCapture', $env:COMPUTERNAME }
    Move-Item -Path .\*.txt -Destination $EvidenceDir -ErrorAction Stop
    Move-Item -Path .\*.raw -Destination $EvidenceDir -ErrorAction Stop
    # MD5 here is for evidence-integrity verification, not cryptographic security - matches chain-of-custody convention.
    Get-FileHash -Algorithm MD5 "$EvidenceDir\*.raw" | Out-File "$EvidenceDir\MemoryCapture_MD5Hashes.txt"
    Write-Host -ForegroundColor Yellow "[ ] Memory capture completed."
    Add-Content -Path $LogFile -Value "Memory capture completed: $((Get-Date).ToString())"
} catch {
    Write-Error "Memory capture step failed: $_"
    Add-Content -Path $LogFile -Value "Memory capture FAILED: $_"
}

Start-Sleep -Seconds 1
Add-Content -Path $LogFile -Value "KAPE triage date collection initiated: $((Get-Date).ToString())"
Write-Host -ForegroundColor Green "[ ] Collecting OS Artifacts."
try {
    .\Kape\kape.exe --tsource C: --tdest $EvidenceDir --target !SANS_Triage --vhdx $env:COMPUTERNAME --zv false
    Set-Content -Path "$EvidenceDir\Finished.txt" -Value "Evidence collection complete: $((Get-Date).ToString())" -ErrorAction Stop
    # MD5 here is for evidence-integrity verification, not cryptographic security - matches chain-of-custody convention.
    Get-FileHash -Algorithm MD5 "$EvidenceDir\*.vhdx" | Out-File "$EvidenceDir\KapeOutput_MD5Hashes.txt"
    Add-Content -Path $LogFile -Value "Collection completed: $((Get-Date).ToString())"
    Write-Host -ForegroundColor Green "[ ] Collection completed"
} catch {
    Write-Error "KAPE triage step failed: $_"
    Add-Content -Path $LogFile -Value "KAPE triage FAILED: $_"
}
