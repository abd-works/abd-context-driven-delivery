# Run the non-agent suite in the reporter each runner actually prints.
# Mamba's default is progress (dots). Documentation is the report: nested
# description / context / it lines, then the failure list.
# Story files are Mamba with a different loader, so they go through story_test.
# Agentic BDD (*_agent_spec.py that drive agent_bdd) stays out of this pass.
param(
    [ValidateSet("vanilla", "agent")]
    [string]$Suite = "vanilla"
)

$ErrorActionPreference = "Continue"
$repo = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $repo ".venv\Scripts\python.exe"
$venvMamba = Join-Path $repo ".venv\Scripts\mamba.exe"
$python = if (Test-Path $venvPython) { $venvPython } else { "python" }
$mamba = if (Test-Path $venvMamba) { $venvMamba } else { "mamba" }

$excludedDirs = [System.Collections.Generic.HashSet[string]]::new(
    [string[]]@(
        ".codeql", ".cq", ".venv", ".git", "node_modules", "__pycache__",
        ".ruff_cache", "sandbox", "fixtures", "seeds", "templates"
    ),
    [StringComparer]::OrdinalIgnoreCase
)

function Set-TestEnvironment {
    $roots = @(".", "actions", "tools", "practices", "patterns")
    # Leave the harness folder off the path so `import mcp` stays the SDK,
    # not harness/mcp. The repo root still exposes the harness package.
    $env:PYTHONPATH = (($roots | ForEach-Object { Join-Path $repo $_ }) -join [IO.Path]::PathSeparator)
    $env:PYTHONUTF8 = "1"
    $env:PYTHONIOENCODING = "utf-8"
}

function Get-RepoFiles {
    param([scriptblock]$IncludeName)
    $found = New-Object System.Collections.Generic.List[string]
    $pending = New-Object System.Collections.Generic.Stack[string]
    $pending.Push($repo)
    while ($pending.Count -gt 0) {
        $dir = $pending.Pop()
        try {
            $entries = [System.IO.Directory]::EnumerateFileSystemEntries($dir)
        } catch {
            continue
        }
        foreach ($entry in $entries) {
            $name = [System.IO.Path]::GetFileName($entry)
            if ([System.IO.Directory]::Exists($entry)) {
                if ($excludedDirs.Contains($name) -or $name.StartsWith(".examples")) { continue }
                $pending.Push($entry)
            } elseif (& $IncludeName $name) {
                $found.Add($entry)
            }
        }
    }
    foreach ($path in ($found.ToArray() | Sort-Object)) {
        Write-Output $path
    }
}

function Test-AgenticBdd {
    param([string]$Name)
    # sub_agent_spec.py is the SubAgent unit spec. It only shares the suffix.
    return $Name -match '(?<!sub_)agent_spec\.py$'
}

function Get-RelativePath {
    param([string]$FullName)
    return $FullName.Substring($repo.Length).TrimStart('\', '/').Replace('\', '/')
}

function Invoke-Reported {
    param(
        [string]$Label,
        [string[]]$Files,
        [scriptblock]$RunOne
    )
    Write-Host ""
    Write-Host "$Label ($($Files.Count))"
    if ($Files.Count -eq 0) {
        return
    }
    $index = 0
    foreach ($file in $Files) {
        $index++
        $relative = Get-RelativePath $file
        Write-Host ""
        Write-Host "[$index/$($Files.Count)] $relative"
        & $RunOne $relative
        if ($LASTEXITCODE -ne 0) {
            Write-Output $relative
        }
    }
}

Set-TestEnvironment
Push-Location $repo
try {
    $failures = New-Object System.Collections.Generic.List[string]

    if ($Suite -eq "vanilla") {
        $stories = @(Get-RepoFiles { param($name) $name -like "*_story.test.py" })
        $specs = @(Get-RepoFiles { param($name) $name -like "*_spec.py" } | Where-Object {
            -not (Test-AgenticBdd ([IO.Path]::GetFileName($_)))
        })
        $storyModule = Join-Path $repo "practices\stories\templates\py"
        $savedPath = $env:PYTHONPATH
        $env:PYTHONPATH = "$storyModule$([IO.Path]::PathSeparator)$savedPath"
        $storyFailures = Invoke-Reported "Python story tests" $stories {
            param($relative)
            & $python -m story_test --format documentation $relative
        }
        $env:PYTHONPATH = $savedPath
        $specFailures = Invoke-Reported "Mamba specs" $specs {
            param($relative)
            & $mamba --format documentation $relative
        }
        foreach ($relative in @($storyFailures) + @($specFailures)) {
            if ($relative) { $failures.Add($relative) | Out-Null }
        }
        $total = @($stories).Count + @($specs).Count
    } else {
        $agentSpecs = @(Get-RepoFiles { param($name) $name -like "*_spec.py" } | Where-Object {
            Test-AgenticBdd ([IO.Path]::GetFileName($_))
        })
        $agentFailures = Invoke-Reported "Agentic BDD" $agentSpecs {
            param($relative)
            & $mamba --format documentation $relative
        }
        foreach ($relative in @($agentFailures)) {
            if ($relative) { $failures.Add($relative) | Out-Null }
        }
        $total = @($agentSpecs).Count
    }
} finally {
    Pop-Location
}

$failed = @($failures | Where-Object { $_ })
$passed = $total - $failed.Count
Write-Host ""
Write-Host "$passed/$total files passed"
foreach ($relative in $failed) {
    Write-Host "FAILED $relative"
}
if ($failed.Count -gt 0) { exit 1 }
exit 0
