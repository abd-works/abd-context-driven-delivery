# Reads and presses the Board pane in the running Claude desktop app through Windows UI Automation.
# list prints every element of the app as JSON, press invokes the one at -X -Y, colour prints one pixel.
param(
    [ValidateSet("list", "press", "colour")]
    [string]$Command = "list",
    [string]$Name = "",
    [int]$X = 0,
    [int]$Y = 0
)

$ErrorActionPreference = "Stop"
Add-Type -Namespace DesktopPane -Name Dpi -MemberDefinition '[System.Runtime.InteropServices.DllImport("user32.dll")] public static extern bool SetProcessDPIAware();'
[DesktopPane.Dpi]::SetProcessDPIAware() | Out-Null
Add-Type -AssemblyName System.Drawing, UIAutomationClient, UIAutomationTypes

function Get-AppWindow {
    $named = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, "Claude")
    $window = [System.Windows.Automation.AutomationElement]::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Children, $named)
    if (-not $window) { throw "The Claude desktop app has no window open" }
    return $window
}

function Get-AppElements {
    return (Get-AppWindow).FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
}

if ($Command -eq "colour") {
    $bitmap = New-Object System.Drawing.Bitmap 1, 1
    [System.Drawing.Graphics]::FromImage($bitmap).CopyFromScreen($X, $Y, 0, 0, $bitmap.Size)
    $pixel = $bitmap.GetPixel(0, 0)
    "#{0:X2}{1:X2}{2:X2}" -f $pixel.R, $pixel.G, $pixel.B
    return
}

if ($Command -eq "press") {
    foreach ($element in Get-AppElements) {
        $box = $element.Current.BoundingRectangle
        if ($element.Current.Name -eq $Name -and [int]$box.X -eq $X -and [int]$box.Y -eq $Y) {
            $element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
            return
        }
    }
    throw "No element named '$Name' at $X,$Y"
}

$window = (Get-AppWindow).Current.BoundingRectangle
$found = foreach ($element in Get-AppElements) {
    $box = $element.Current.BoundingRectangle
    if ($box.Width -le 0) { continue }
    [pscustomobject]@{
        kind = $element.Current.ControlType.ProgrammaticName.Replace("ControlType.", "")
        name = ($element.Current.Name -replace "\s+", " ").Trim()
        left = [int]$box.X
        top = [int]$box.Y
        width = [int]$box.Width
        height = [int]$box.Height
        is_offscreen = [bool]$element.Current.IsOffscreen
    }
}
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
@{ window_bottom = [int]$window.Bottom; elements = @($found) } | ConvertTo-Json -Depth 3 -Compress
