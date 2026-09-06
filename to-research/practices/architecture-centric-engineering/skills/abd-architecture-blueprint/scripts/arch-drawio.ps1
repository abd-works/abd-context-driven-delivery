<#
.SYNOPSIS
  CLI helper for managing the architecture-blueprint drawio diagrams.

.DESCRIPTION
  Three sub-commands (same as the architecture-outline CLI):

    init     Copy the two blueprint drawio templates (entity-relationships,
             component-overview) into <ProjectRoot>/docs/architecture/diagrams/.

    export   Render every <name>.drawio in the diagrams folder to <name>.png
             using draw.io Desktop.

    verify   Confirm that every diagram referenced from architecture-blueprint.md
             has a paired <name>.drawio source on disk under
             docs/architecture/diagrams/.

  Canonical filenames this skill expects:
    entity-relationships.drawio
    component-overview.drawio

.EXAMPLE
  .\arch-drawio.ps1 init -ProjectRoot C:\hero-desktop\city-of-heroes-virtual-tabletop

.EXAMPLE
  .\arch-drawio.ps1 export -ProjectRoot C:\hero-desktop\city-of-heroes-virtual-tabletop

.EXAMPLE
  .\arch-drawio.ps1 verify -ProjectRoot C:\hero-desktop\city-of-heroes-virtual-tabletop
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet('init','export','verify')]
    [string]$Command,

    [Parameter(Position=1)]
    [string]$ProjectRoot = (Get-Location).Path,

    [string]$DrawIoExe = "$env:LOCALAPPDATA\Programs\draw.io\draw.io.exe",

    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$scriptRoot   = $PSScriptRoot
$templatesDir = Join-Path (Split-Path $scriptRoot -Parent) 'templates'
$diagramsDir  = Join-Path $ProjectRoot 'docs\architecture\diagrams'
$blueprintMd  = Join-Path $ProjectRoot 'docs\architecture\architecture-blueprint.md'

function Initialize-Diagrams {
    if (-not (Test-Path $diagramsDir)) {
        New-Item -ItemType Directory -Path $diagramsDir -Force | Out-Null
        Write-Host "[init] Created $diagramsDir"
    }

    $templates = Get-ChildItem -Path $templatesDir -Filter '*.drawio'
    foreach ($t in $templates) {
        $target = Join-Path $diagramsDir $t.Name
        if ((Test-Path $target) -and -not $Force) {
            Write-Host "[init] SKIP $($t.Name) — already exists (use -Force to overwrite)"
            continue
        }
        Copy-Item -Path $t.FullName -Destination $target -Force
        Write-Host "[init] COPY $($t.Name) -> $target"
    }
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Open each .drawio in draw.io Desktop or app.diagrams.net and fill in the {Placeholders}."
    Write-Host "  2. Run '.\arch-drawio.ps1 export -ProjectRoot $ProjectRoot' to render PNGs."
    Write-Host "  3. Reference the PNGs from docs/architecture/architecture-blueprint.md."
}

function Export-Diagrams {
    if (-not (Test-Path $diagramsDir)) {
        throw "Diagrams folder not found: $diagramsDir. Run 'init' first."
    }
    if (-not (Test-Path $DrawIoExe)) {
        Write-Warning "draw.io binary not found at: $DrawIoExe"
        Write-Warning "Install draw.io Desktop from https://www.drawio.com/download or pass -DrawIoExe <path>."
        Write-Warning "Skipping export."
        return
    }

    $drawioFiles = Get-ChildItem -Path $diagramsDir -Filter '*.drawio'
    foreach ($f in $drawioFiles) {
        $pngPath = [System.IO.Path]::ChangeExtension($f.FullName, '.png')
        if ((Test-Path $pngPath) -and -not $Force) {
            $pngTime = (Get-Item $pngPath).LastWriteTime
            if ($pngTime -gt $f.LastWriteTime) {
                Write-Host "[export] SKIP $($f.Name) — PNG is newer than source"
                continue
            }
        }
        Write-Host "[export] $($f.Name) -> $($f.BaseName).png"
        & $DrawIoExe --export --format png --output $pngPath $f.FullName 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "draw.io export returned exit code $LASTEXITCODE for $($f.Name)"
        }
    }
}

function Test-Pairs {
    if (-not (Test-Path $blueprintMd)) {
        throw "Blueprint markdown not found: $blueprintMd"
    }
    if (-not (Test-Path $diagramsDir)) {
        throw "Diagrams folder not found: $diagramsDir"
    }

    $md = Get-Content $blueprintMd -Raw

    $imageRefs = [System.Text.RegularExpressions.Regex]::Matches(
        $md,
        '!\[[^\]]*\]\(([^)]+\.(?:png|svg))\)'
    ) | ForEach-Object { $_.Groups[1].Value }

    $linkRefs = [System.Text.RegularExpressions.Regex]::Matches(
        $md,
        '\[[^\]]+\]\(([^)]+\.drawio)\)'
    ) | ForEach-Object { $_.Groups[1].Value }

    $refs = @($imageRefs) + @($linkRefs) | Select-Object -Unique

    if (-not $refs) {
        Write-Warning "No diagram references found in $blueprintMd."
    }

    $errors = @()
    foreach ($ref in $refs) {
        $base = [System.IO.Path]::GetFileNameWithoutExtension($ref)
        $expectedDrawio = Join-Path $diagramsDir "$base.drawio"
        if (Test-Path $expectedDrawio) {
            Write-Host "[verify] OK   $ref -> $base.drawio exists"
        } else {
            Write-Host "[verify] MISS $ref -> $base.drawio NOT FOUND" -ForegroundColor Red
            $errors += $ref
        }
    }

    if ($errors.Count -gt 0) {
        Write-Host ""
        Write-Host "FAIL: $($errors.Count) diagram(s) missing a paired .drawio source." -ForegroundColor Red
        exit 1
    } else {
        Write-Host ""
        Write-Host "PASS: every referenced diagram has a paired .drawio source on disk." -ForegroundColor Green
    }
}

switch ($Command) {
    'init'   { Initialize-Diagrams }
    'export' { Export-Diagrams }
    'verify' { Test-Pairs }
}
