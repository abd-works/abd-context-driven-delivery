// What the Files server runs to show a file or folder in the system's file browser, by the system it runs on, as the
// story Open File In File Browser asks (review_files_in_files_app_story.test.md).
import { describe, expect, it } from 'vitest'

import { FileExplorer } from './file-explorer'

describe('Open File In File Browser', () => {
  describe('on Windows', () => {
    const explorer = new FileExplorer('win32')

    it('should open Explorer with the file selected', () => {
      expect(explorer.commandFor('C:/dev/work/.context/story-map.md', false)).toEqual({ program: 'explorer.exe', args: ['/select,C:\\dev\\work\\.context\\story-map.md'] })
    })

    it('should open Explorer on a folder', () => {
      expect(explorer.commandFor('C:/dev/work/.context', true)).toEqual({ program: 'explorer.exe', args: ['C:\\dev\\work\\.context'] })
    })
  })

  describe('on a Mac', () => {
    const explorer = new FileExplorer('darwin')

    it('should reveal the file in Finder', () => {
      expect(explorer.commandFor('/work/.context/story-map.md', false)).toEqual({ program: 'open', args: ['-R', '/work/.context/story-map.md'] })
    })

    it('should open a folder in Finder', () => {
      expect(explorer.commandFor('/work/.context', true)).toEqual({ program: 'open', args: ['/work/.context'] })
    })
  })

  describe('on Linux', () => {
    it("should open the file's folder in the desktop's file manager", () => {
      expect(new FileExplorer('linux').commandFor('/work/.context/story-map.md', false)).toEqual({ program: 'xdg-open', args: ['/work/.context'] })
    })
  })
})
