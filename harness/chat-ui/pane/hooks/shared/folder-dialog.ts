import type { EngineInterface } from 'claude-code'

import { reasonOf } from '../error-display/failure-client'

// The system's own folder picker, as each system offers one to a program with no window: Windows' folder browser, kept
// on top of the Claude app so it is not opened behind it, macOS's choose folder, and zenity on Linux. Mods have no
// folder dialog of their own, so the first picker this system has is run.

// What the picker asks for, and the folder it opens at; with none, the system's own starting folder.
export type FolderRequest = { purpose: string; startIn?: string }

const CHAT_FOLDER: FolderRequest = { purpose: 'Choose the folder this chat works in' }

// A text the picker's script holds in single quotes, each quote doubled as PowerShell and AppleScript read it.
const quotedForPowerShell = (text: string): string => `'${text.replace(/'/g, "''")}'`
const quotedForAppleScript = (text: string): string => `"${text.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`

function windowsPicker({ purpose, startIn }: FolderRequest): string[] {
  const script = [
    'Add-Type -AssemblyName System.Windows.Forms',
    '$owner = New-Object System.Windows.Forms.Form -Property @{ TopMost = $true }',
    '$dialog = New-Object System.Windows.Forms.FolderBrowserDialog',
    `$dialog.Description = ${quotedForPowerShell(purpose)}`,
    ...(startIn ? [`$dialog.SelectedPath = ${quotedForPowerShell(startIn)}`] : []),
    "if ($dialog.ShowDialog($owner) -eq 'OK') { $dialog.SelectedPath }",
  ].join('; ')
  return ['powershell', '-NoProfile', '-STA', '-Command', script]
}

function macPicker({ purpose, startIn }: FolderRequest): string[] {
  const from = startIn ? ` default location (POSIX file ${quotedForAppleScript(startIn)})` : ''
  return ['osascript', '-e', `POSIX path of (choose folder with prompt ${quotedForAppleScript(purpose)}${from})`]
}

function linuxPicker({ purpose, startIn }: FolderRequest): string[] {
  return ['zenity', '--file-selection', '--directory', `--title=${purpose}`, ...(startIn ? [`--filename=${startIn.replace(/\/?$/, '/')}`] : [])]
}

// The folder the person chose; empty when they cancelled. Throws, with each picker's reason, when none would run.
export async function chosenFolder($: EngineInterface, request: FolderRequest = CHAT_FOLDER): Promise<string> {
  const reasons: string[] = []
  for (const argv of [windowsPicker(request), macPicker(request), linuxPicker(request)]) {
    try {
      const picked = await $.process.run(argv)
      return picked.exitCode === 0 ? picked.stdout.trim() : ''
    } catch (failure) {
      reasons.push(`${argv[0]}: ${reasonOf(failure)}`)
    }
  }
  throw new Error(`no folder picker would run (${reasons.join('; ')})`)
}
