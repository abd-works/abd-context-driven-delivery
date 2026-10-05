# Start the Knowledge Graph explorer (Vite UI + API).
# Usage:  .\Start.ps1
# Stops both processes on Ctrl+C.
$ErrorActionPreference = "Stop"
$App = $PSScriptRoot

function Test-PortInUse([int]$Port) {
    try {
        $tcp = [System.Net.Sockets.TcpListener]::new(
            [System.Net.IPAddress]::Loopback,
            $Port
        )
        $tcp.Start()
        $tcp.Stop()
        return $false
    } catch {
        return $true
    }
}

function Find-PortPair {
    foreach ($ui in 3000, 3010, 3020, 3030, 3040) {
        $api = $ui + 1
        if (-not (Test-PortInUse $ui) -and -not (Test-PortInUse $api)) {
            return @{ Ui = $ui; Api = $api }
        }
    }
    throw "No free UI/API port pair (tried 3000/3001 through 3040/3041)."
}

function Wait-Port([int]$Port, [int]$Seconds = 40) {
    $until = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $until) {
        if (Test-PortInUse $Port) {
            return
        }
        Start-Sleep -Milliseconds 300
    }
    throw "Timed out waiting for port $Port"
}

function Stop-Tree([int]$Id) {
    if ($Id -le 0) {
        return
    }
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.ParentProcessId -eq $Id } |
        ForEach-Object { Stop-Tree $_.ProcessId }
    Stop-Process -Id $Id -Force -ErrorAction SilentlyContinue
}

Set-Location $App
if (-not (Test-Path (Join-Path $App "node_modules"))) {
    npm install
}

$ports = Find-PortPair
$env:VITE_PORT = [string]$ports.Ui
$env:PORT = [string]$ports.Api

$npm = (Get-Command npm.cmd -ErrorAction SilentlyContinue).Source
if (-not $npm) {
    $npm = (Get-Command npm).Source
}

$server = Start-Process -FilePath $npm -ArgumentList "run", "dev:server" `
    -WorkingDirectory $App -PassThru -NoNewWindow
$ui = Start-Process -FilePath $npm -ArgumentList "run", "dev" `
    -WorkingDirectory $App -PassThru -NoNewWindow

try {
    Wait-Port $ports.Api
    Wait-Port $ports.Ui
    $url = "http://localhost:$($ports.Ui)/"
    Write-Host "Knowledge Graph explorer: $url"
    Write-Host "API: http://localhost:$($ports.Api)/"
    Start-Process $url
    Write-Host "Press Ctrl+C to stop."
    while ($true) {
        if ($server.HasExited -or $ui.HasExited) {
            break
        }
        Start-Sleep -Seconds 1
    }
} finally {
    Stop-Tree $server.Id
    Stop-Tree $ui.Id
}
