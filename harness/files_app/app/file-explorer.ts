import { spawn } from 'node:child_process'
import { statSync } from 'node:fs'
import { dirname, resolve, win32 } from 'node:path'

// A program and its arguments, as the system's file browser is started.
export type ExplorerCommand = { program: string; args: string[] }

export class FileNotThere extends Error {
  constructor(path: string) {
    super(`${path} is not there`)
    this.name = 'FileNotThere'
  }
}

// The system's file browser, on the machine the Files server runs on, which is the person's own: Windows Explorer with
// the file selected, Finder revealing it on a Mac, and elsewhere the file's folder in the desktop's file manager.
export class FileExplorer {
  constructor(private readonly platform: NodeJS.Platform = process.platform) {}

  // What starts the file browser on path, a file or, when isFolder, a folder, written as an absolute path.
  commandFor(path: string, isFolder: boolean): ExplorerCommand {
    if (this.platform === 'win32') {
      const shown = win32.normalize(path)
      return { program: 'explorer.exe', args: isFolder ? [shown] : [`/select,${shown}`] }
    }
    if (this.platform === 'darwin') return { program: 'open', args: isFolder ? [path] : ['-R', path] }
    return { program: 'xdg-open', args: [isFolder ? path : dirname(path)] }
  }

  // Shows path, named from project's folder or absolute, in the file browser, which outlives this server.
  reveal(project: string, path: string): void {
    const absolute = resolve(project, path)
    const isFolder = this.isFolder(absolute)
    const { program, args } = this.commandFor(absolute, isFolder)
    spawn(program, args, { detached: true, stdio: 'ignore' }).unref()
  }

  private isFolder(absolute: string): boolean {
    try {
      return statSync(absolute).isDirectory()
    } catch {
      throw new FileNotThere(absolute)
    }
  }
}
