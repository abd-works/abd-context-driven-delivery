# setup.ps1 — install the manifest-gate-notifier extension
#
# Detects whether Cursor or VS Code is installed and drops the extension into
# the correct extensions folder.  Run once after cloning, or whenever
# extension.js / package.json changes, then reload your editor window.
#
# Usage (from repo root or this folder):
#   .\utilities\manifest_hook\extension\setup.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ── Detect editor ────────────────────────────────────────────────────────────
# Cursor stores extensions in ~/.cursor/extensions/
# VS Code stores extensions in ~/.vscode/extensions/
# We check both install locations; Cursor wins if both exist.

$cursorExtDir = "$env:USERPROFILE\.cursor\extensions"
$vscodeExtDir = "$env:USERPROFILE\.vscode\extensions"

if (Test-Path $cursorExtDir) {
    $extDir = $cursorExtDir
    $editor = "Cursor"
} elseif (Test-Path $vscodeExtDir) {
    $extDir = $vscodeExtDir
    $editor = "VS Code"
} else {
    Write-Error "Neither ~/.cursor/extensions nor ~/.vscode/extensions found. Is Cursor or VS Code installed?"
    exit 1
}

Write-Host "Detected editor: $editor  ($extDir)"

# ── Install ───────────────────────────────────────────────────────────────────
# We copy the unpacked folder directly rather than using the CLI
# --install-extension command, which can hang waiting for a running editor
# instance to respond.  The editor loads unpacked extension folders from its
# extensions directory on startup / window reload, so this works reliably.

$dest = Join-Path $extDir "abd.manifest-gate-notifier-1.0.0"
if (Test-Path $dest) {
    Remove-Item $dest -Recurse -Force
}
New-Item -ItemType Directory -Path $dest | Out-Null
Copy-Item (Join-Path $scriptDir "package.json") $dest
Copy-Item (Join-Path $scriptDir "extension.js")  $dest

Write-Host "Installed to: $dest"
Write-Host ""
Write-Host "Reload your editor (Ctrl+Shift+P -> Reload Window) to activate."
