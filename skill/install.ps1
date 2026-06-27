# Install divergent-agents skills for Claude Code on Windows.
#
#   powershell -ExecutionPolicy Bypass -File skill\install.ps1            # user-wide
#   powershell -ExecutionPolicy Bypass -File skill\install.ps1 -Project  # this project only
#
param([switch]$Project)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$dest = if ($Project) { Join-Path (Get-Location) ".claude\skills" } else { Join-Path $env:USERPROFILE ".claude\skills" }
New-Item -ItemType Directory -Force -Path $dest | Out-Null
foreach ($s in "divergence", "robust-solve") {
    $target = Join-Path $dest $s
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Copy-Item -Recurse -Force (Join-Path $here $s) $target
    Write-Host "  installed  $s  ->  $target"
}
Write-Host ""
Write-Host "Done. Restart Claude Code, then type  /diverge  or  /robust-solve"
