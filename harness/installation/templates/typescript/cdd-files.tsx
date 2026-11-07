/** @jsxRuntime automatic @jsxImportSource react */
import Editor, { type OnMount } from '@monaco-editor/react'
import { useEffect, useState, type ReactNode } from 'react'

import type { CddApi } from './cdd-shared'
import { FileManagerClientGenerated, type FolderData } from '__FILE_MANAGER__'

// Shared views over the session's file manager. Every application shows a file through these rather than writing its own.

const LANGUAGES: Record<string, string> = {
  ts: 'typescript',
  tsx: 'typescript',
  js: 'javascript',
  jsx: 'javascript',
  py: 'python',
  md: 'markdown',
  json: 'json',
  yaml: 'yaml',
  yml: 'yaml',
  html: 'html',
  css: 'css',
}

const languageOf = (path: string): string => LANGUAGES[path.split('.').pop()?.toLowerCase() ?? ''] ?? 'plaintext'

export type SourceViewProps = { api: CddApi; path: string; line?: number | null; startLine?: number | null; endLine?: number | null }

// A file's text in Monaco, read-only, scrolled to its line and with that line, or the range, marked.
export function SourceViewGenerated({ api, path, line, startLine, endLine }: SourceViewProps): ReactNode {
  const [text, setText] = useState<string | null>(null)
  useEffect(() => {
    let current = true
    void new FileManagerClientGenerated(api).read(path).then(file => {
      if (current && file) setText(file.text)
    })
    return () => {
      current = false
    }
  }, [api, path])
  const first = startLine ?? line ?? null
  const last = endLine ?? first
  const marked: OnMount = (editor, monaco) => {
    if (first === null || last === null) return
    editor.revealLineInCenter(first)
    editor.createDecorationsCollection([{ range: new monaco.Range(first, 1, last, 1), options: { isWholeLine: true, className: 'cdd-source-marked' } }])
  }
  return (
    <section className="cdd-view cdd-source">
      <header className="cdd-source-path">{path}</header>
      {text === null ? (
        <p className="cdd-source-reading">Reading {path}</p>
      ) : (
        <Editor height="100%" value={text} language={languageOf(path)} options={{ readOnly: true, minimap: { enabled: false } }} onMount={marked} />
      )}
    </section>
  )
}

export type FileListViewProps = { api: CddApi; folder?: string; onOpen?: (path: string) => void }

// The entries of one folder under the session's roots. A folder opens in place; a file opens through onOpen, or in the
// source view below the list when the page gives none.
export function FileListViewGenerated({ api, folder = '', onOpen }: FileListViewProps): ReactNode {
  const [listed, setListed] = useState<FolderData | null>(null)
  const [opened, setOpened] = useState<string | null>(null)
  const list = (path: string): void => {
    void new FileManagerClientGenerated(api).list(path).then(found => found && setListed(found))
  }
  useEffect(() => list(folder), [api, folder])
  const open = (path: string): void => (onOpen ? onOpen(path) : setOpened(path))
  return (
    <section className="cdd-view cdd-file-list">
      <header className="cdd-file-list-folder">{listed?.folder || '.'}</header>
      <ul>
        {listed && listed.folder !== folder && (
          <li className="cdd-file-list-folder-entry">
            <button type="button" onClick={() => list(listed.folder.split('/').slice(0, -1).join('/'))}>
              ..
            </button>
          </li>
        )}
        {listed?.entries.map(entry => (
          <li key={entry.path} className={entry.is_folder ? 'cdd-file-list-folder-entry' : 'cdd-file-list-file'}>
            <button type="button" onClick={() => (entry.is_folder ? list(entry.path) : open(entry.path))}>
              {entry.name}
            </button>
          </li>
        ))}
      </ul>
      {opened && <SourceViewGenerated api={api} path={opened} />}
    </section>
  )
}

// A data field Python annotates as a file: a link that opens the source view at that file and its line or range.
export function SourceField({ api, label, ...source }: { label: string } & SourceViewProps): ReactNode {
  const [isOpen, setOpen] = useState(false)
  return (
    <div className="cdd-field cdd-field-source">
      <span className="cdd-field-label">{label}</span>
      <button type="button" className="cdd-field-value" onClick={() => setOpen(!isOpen)}>
        {source.path}
        {source.line ? `:${source.line}` : ''}
      </button>
      {isOpen && <SourceViewGenerated api={api} {...source} />}
    </div>
  )
}
