# Run the non-agent suite in the reporter each runner actually prints.
# Mamba's default is progress (dots). Documentation is the report: nested
# description / context / it lines, then the failure list.
# Story files are Mamba with a different loader, so they go through story_test.
# Agentic BDD (*_agent_spec.py that drive agent_bdd) stays out of this pass.
# Heavy specs (*_heavy_spec.py) drive a browser, start servers or subprocesses,
# or build indexes; they run only with -Suite heavy so the default pass stays fast.
param(
    [ValidateSet("vanilla", "heavy", "agent")]
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
        ".ruff_cache", "sandbox", "fixtures", "seeds", "templates", "retired", ".retired", "_retired", ".claude", ".cursor"
    ),
    [StringComparer]::OrdinalIgnoreCase
)

function Set-TestEnvironment {
    $roots = @(".", "cdd_guidance/actions", "tools", "cdd_guidance/practices", "cdd_guidance/patterns")
    # Leave the harness folder off the path so `import mcp` stays the SDK,
    # not harness/mcp. The repo root still exposes the harness package.
    $env:PYTHONPATH = (($roots | ForEach-Object { Join-Path $repo $_ }) -join [IO.Path]::PathSeparator)
    $env:PYTHONUTF8 = "1"
    $env:PYTHONIOENCODING = "utf-8"
    # Every spec process imports the framework and its packages (mcp, pydantic, httpx, coverage) anew. A Claude Code
    # chat runs its commands with PYTHONDONTWRITEBYTECODE set, which would make each one compile them all again, so the
    # run writes bytecode, in the checkout's one bytecode folder, as the cdd server and hook daemon do.
    Remove-Item Env:PYTHONDONTWRITEBYTECODE -ErrorAction SilentlyContinue
    $env:PYTHONPYCACHEPREFIX = Join-Path $repo ".pycache"
    # Specs keep what chats have open in a cdd home of their own, never the one the running cdd server uses, and no
    # spec answers as the chat that started the run.
    $env:CDD_HOME = Join-Path ([IO.Path]::GetTempPath()) ("cdd-spec-home-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force $env:CDD_HOME | Out-Null
    Remove-Item Env:CLAUDE_CODE_SESSION_ID -ErrorAction SilentlyContinue
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

function Test-Heavy {
    param([string]$Name)
    return $Name -like "*_heavy_spec.py"
}

function Get-RelativePath {
    param([string]$FullName)
    return $FullName.Substring($repo.Length).TrimStart('\', '/').Replace('\', '/')
}

# Spec files run one batch per module folder: each batch is one process, which imports the framework once for all of
# that folder's files, and the batches run side by side. Each batch gets its own cdd home, so no two batches write the
# same open-sessions.json.
$parallelBatches = [Math]::Max(2, [Environment]::ProcessorCount - 2)
# How many folders deep a batch reaches: `space/kanban`, `harness/mcp`, `cdd_guidance/practices/stories`.
$batchDepth = 3

function Get-BatchKey {
    param([string]$Relative)
    $folders = @($Relative.Split('/') | Select-Object -SkipLast 1)
    if ($folders.Count -eq 0) { return "." }
    return ($folders | Select-Object -First $batchDepth) -join '/'
}

# A folder with many spec files, such as space/kanban, would otherwise run them one after another in one process while
# the other batches finish early; its files are dealt into several batches, each with its own cdd home.
$filesPerBatch = 4

function Split-LargeBatches {
    param($Groups)
    foreach ($group in $Groups) {
        $files = [string[]]$group.Group
        if ($files.Count -le $filesPerBatch) {
            [pscustomobject]@{ Name = $group.Name; Group = $files; Count = $files.Count }
            continue
        }
        for ($start = 0; $start -lt $files.Count; $start += $filesPerBatch) {
            $part = [string[]]($files[$start..([Math]::Min($start + $filesPerBatch, $files.Count) - 1)])
            [pscustomobject]@{ Name = "$($group.Name) #$($start / $filesPerBatch + 1)"; Group = $part; Count = $part.Count }
        }
    }
}

# The run cannot end before its slowest batch, so the seconds each file took last time order the next run: a file that
# took $soloSeconds or more runs in a batch of its own, and the batches expected to take longest start first. The
# seconds live beside the bytecode, out of git; a file never timed counts as $unknownSeconds.
$timesFile = Join-Path $repo ".pycache\spec-seconds.json"
$soloSeconds = 20
$unknownSeconds = 5

function Read-SpecSeconds {
    $seconds = @{}
    try {
        $saved = Get-Content $timesFile -Raw -ErrorAction Stop | ConvertFrom-Json
        foreach ($property in $saved.PSObject.Properties) { $seconds[$property.Name] = [double]$property.Value }
    } catch { }
    return $seconds
}

function Save-SpecSeconds {
    param([hashtable]$Seconds)
    New-Item -ItemType Directory -Force (Split-Path $timesFile) | Out-Null
    $Seconds | ConvertTo-Json | Set-Content -Path $timesFile -Encoding utf8
}

function Get-ExpectedSeconds {
    param([hashtable]$Seconds, [string[]]$Relatives)
    $total = 0.0
    foreach ($relative in $Relatives) { $total += $(if ($Seconds.ContainsKey($relative)) { $Seconds[$relative] } else { $unknownSeconds }) }
    return $total
}

function Get-Batches {
    param([string[]]$Relatives, [hashtable]$Seconds)
    $slow = @($Relatives | Where-Object { $Seconds.ContainsKey($_) -and $Seconds[$_] -ge $soloSeconds })
    $rest = @($Relatives | Where-Object { $slow -notcontains $_ })
    $batches = @(foreach ($relative in $slow) { [pscustomobject]@{ Name = $relative; Group = [string[]]@($relative); Count = 1 } })
    if ($rest.Count -gt 0) { $batches += @(Split-LargeBatches ($rest | Group-Object { Get-BatchKey $_ })) }
    return $batches | Sort-Object { Get-ExpectedSeconds $Seconds ([string[]]$_.Group) } -Descending
}

function Start-SpecBatch {
    param([string]$Executable, [string[]]$Arguments, [string]$Key, [string[]]$Relatives, [string]$OutputFolder)
    $env:CDD_HOME = Join-Path $OutputFolder ("home-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force $env:CDD_HOME | Out-Null
    $out = Join-Path $OutputFolder ([guid]::NewGuid().ToString("N") + ".out")
    $process = Start-Process -FilePath $Executable -ArgumentList ($Arguments + $Relatives) -WorkingDirectory $repo `
        -NoNewWindow -PassThru -RedirectStandardOutput $out -RedirectStandardError "$out.err"
    # Windows PowerShell reads a started process's exit code only when its handle was taken while it ran.
    $null = $process.Handle
    return [pscustomobject]@{ Process = $process; Key = $Key; Relatives = $Relatives; Out = $out; Clock = [Diagnostics.Stopwatch]::StartNew(); Seconds = 0.0 }
}

function Get-FailedFiles {
    param($Batch)
    # Mamba names the spec file of each failed example on its Failure/Error line.
    $text = Get-Content $Batch.Out, "$($Batch.Out).err" -Raw -ErrorAction SilentlyContinue
    $failed = @($Batch.Relatives | Where-Object { $text -match [regex]::Escape("Failure/Error: " + $_.Replace('/', '\')) -or $text -match [regex]::Escape("Failure/Error: " + $_) })
    if ($Batch.Process.ExitCode -ne 0 -and $failed.Count -eq 0) { return @($Batch.Key) }
    return $failed
}

function Invoke-Reported {
    param(
        [string]$Label,
        [string[]]$Files,
        [string]$Executable,
        [string[]]$Arguments,
        [int]$Parallel = $parallelBatches
    )
    Write-Host ""
    Write-Host "$Label ($($Files.Count))"
    if ($Files.Count -eq 0) {
        return
    }
    $outputFolder = Join-Path ([IO.Path]::GetTempPath()) ("cdd-spec-run-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force $outputFolder | Out-Null
    $seconds = Read-SpecSeconds
    $batches = Get-Batches ([string[]]@($Files | ForEach-Object { Get-RelativePath $_ })) $seconds
    $pending = [System.Collections.Generic.Queue[object]]::new([object[]]@($batches))
    $running = New-Object System.Collections.Generic.List[object]
    $finished = New-Object System.Collections.Generic.List[object]
    while ($pending.Count -gt 0 -or $running.Count -gt 0) {
        while ($pending.Count -gt 0 -and $running.Count -lt $Parallel) {
            $group = $pending.Dequeue()
            $running.Add((Start-SpecBatch $Executable $Arguments $group.Name ([string[]]$group.Group) $outputFolder))
        }
        foreach ($batch in @($running | Where-Object { $_.Process.HasExited })) {
            $batch.Process.WaitForExit()
            $batch.Seconds = $batch.Clock.Elapsed.TotalSeconds
            # A batch's files share its seconds evenly: Mamba times the batch, not each file in it.
            foreach ($relative in $batch.Relatives) { $seconds[$relative] = [Math]::Round($batch.Seconds / $batch.Relatives.Count, 1) }
            $finished.Add($batch)
            $running.Remove($batch) | Out-Null
        }
        Start-Sleep -Milliseconds 200
    }
    Save-SpecSeconds $seconds
    foreach ($batch in ($finished | Sort-Object Key)) {
        Write-Host ""
        Write-Host "[$($batch.Key)] $($batch.Relatives.Count) files, $([Math]::Round($batch.Seconds, 1)) s"
        Get-Content $batch.Out, "$($batch.Out).err" -ErrorAction SilentlyContinue | Out-Host
        Get-FailedFiles $batch | ForEach-Object { Write-Output $_ }
    }
    Remove-Item -Recurse -Force $outputFolder -ErrorAction SilentlyContinue
}

Set-TestEnvironment
# Only the agent suite may start a real agent; in the others a spec that opens the agent command line fails at once.
if ($Suite -ne "agent") { $env:CDD_AGENT_RUNS_OFF = "1" } else { Remove-Item Env:CDD_AGENT_RUNS_OFF -ErrorAction SilentlyContinue }
Push-Location $repo
try {
    $failures = New-Object System.Collections.Generic.List[string]

    if ($Suite -eq "vanilla") {
        # A story channel's rendered outputs under _examples/actual import an examples module that is not rendered
        # beside them; the channel feature checks them, so they do not run as story tests here.
        $stories = @(Get-RepoFiles { param($name) $name -like "*_story.test.py" } | Where-Object {
            $_ -notlike "*\_examples\actual\*"
        })
        # A sub-epic's story tiers, `{sub_epic}.story.domain.spec.py` and `.story.server.spec.py`, are its acceptance tests.
        $specs = @(Get-RepoFiles { param($name) $name -like "*_spec.py" -or $name -like "*.story.*.spec.py" } | Where-Object {
            $name = [IO.Path]::GetFileName($_)
            -not (Test-AgenticBdd $name) -and -not (Test-Heavy $name)
        })
        $storyModule = Join-Path $repo "cdd_guidance\practices\stories\templates\py"
        $savedPath = $env:PYTHONPATH
        $env:PYTHONPATH = "$storyModule$([IO.Path]::PathSeparator)$savedPath"
        $storyFailures = Invoke-Reported "Python story tests" $stories $python @("-m", "story_test", "--format", "documentation")
        $env:PYTHONPATH = $savedPath
        $specFailures = Invoke-Reported "Mamba specs" $specs $mamba @("--format", "documentation")
        foreach ($relative in @($storyFailures) + @($specFailures)) {
            if ($relative) { $failures.Add($relative) | Out-Null }
        }
        $total = @($stories).Count + @($specs).Count
    } elseif ($Suite -eq "heavy") {
        $heavySpecs = @(Get-RepoFiles { param($name) Test-Heavy $name })
        # Heavy specs start servers and browsers, so each runs in its own process, one at a time.
        $heavyFailures = @()
        foreach ($heavy in $heavySpecs) {
            $heavyFailures += Invoke-Reported "Heavy spec" @($heavy) $mamba @("--format", "documentation") -Parallel 1
        }
        foreach ($relative in @($heavyFailures)) {
            if ($relative) { $failures.Add($relative) | Out-Null }
        }
        $total = @($heavySpecs).Count
    } else {
        $agentSpecs = @(Get-RepoFiles { param($name) $name -like "*_spec.py" } | Where-Object {
            Test-AgenticBdd ([IO.Path]::GetFileName($_))
        })
        $agentFailures = Invoke-Reported "Agentic BDD" $agentSpecs $mamba @("--format", "documentation")
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
