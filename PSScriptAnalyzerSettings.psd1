# PSScriptAnalyzer configuration for Forensics/Powershell.
#
# Runs the default rule set except for two rules that flag deliberate,
# documented choices in these interactive IR/forensics scripts:
#
#   PSAvoidUsingWriteHost
#       These scripts use Write-Host (with -ForegroundColor) on purpose to give
#       the analyst colored, immediate console status during live response. That
#       is the correct use of Write-Host for an interactive tool; their actual
#       data/evidence is written to files and logs, not the pipeline.
#
#   PSAvoidUsingBrokenHashAlgorithms
#       collectEvidence.ps1 computes MD5 over captured images for chain-of-
#       custody verification (a forensics convention), not for cryptographic
#       security. A SHA-256 manifest is written alongside it.
@{
    ExcludeRules = @(
        'PSAvoidUsingWriteHost',
        'PSAvoidUsingBrokenHashAlgorithms'
    )
}
