import type { EngineInterface } from 'claude-code'

// The system's own folder picker, as each system offers one to a program with no window: Windows' folder browser, kept
// on top of the Claude app so it is not opened behind it, macOS's choose folder, and zenity on Linux. Mods have no
// folder dialog of their own, so the first picker this system has is run.
const WINDOWS_PICKER = [
  'Add-Type -AssemblyName System.Windows.Forms',
  '$owner = New-Object System.Windows.Forms.Form -Property @{ TopMost = $true }',
  '$dialog = New-Object System.Windows.Forms.FolderBrowserDialog',
  "$dialog.Description = 'Choose the folder this chat works in'",
  "if ($dialog.ShowDialog($owner) -eq 'OK') { $dialog.SelectedPath }",
].join('; ')

const PICKERS = [
  ['powershell', '-NoProfile', '-STA', '-Command', WINDOWS_PICKER],
  ['osascript', '-e', 'POSIX path of (choose folder with prompt "Choose the folder this chat works in")'],
  ['zenity', '--file-selection', '--directory', '--title=Choose the folder this chat works in'],
]

// The folder the person chose; empty when they cancelled or this system has no picker.
export async function chosenFolder($: EngineInterface): Promise<string> {
  for (const argv of PICKERS) {
    const picked = await $.process.run(argv).catch(() => null)
    if (picked === null) continue
    return picked.exitCode === 0 ? picked.stdout.trim() : ''
  }
  return ''
}
