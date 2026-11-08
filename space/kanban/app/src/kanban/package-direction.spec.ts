import { readdirSync, readFileSync, statSync } from 'node:fs'
import { dirname, join, relative, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

// The board page's packages, from the composition root down. A package imports at run time only from a package below
// it: board wires the page from ticket, chat and backlog-item, which draw on shared, which imports none of them.
// TypeScript erases an `import type`, so naming a class for an annotation is no run-time dependency and is not counted.
const LAYERS: Record<string, number> = { board: 3, ticket: 2, chat: 1, 'backlog-item': 1, shared: 0 }

const KANBAN = dirname(fileURLToPath(import.meta.url))
const IMPORT = /^\s*(import|export)\s+(type\s+)?([^'"]*?)\s*from\s+'(\.[^']+)'/gm

function sourcesIn(folder: string): string[] {
  return readdirSync(folder).flatMap(name => {
    const path = join(folder, name)
    if (statSync(path).isDirectory()) return sourcesIn(path)
    return /\.tsx?$/.test(name) && !name.endsWith('.spec.ts') ? [path] : []
  })
}

const packageOf = (path: string): string => relative(KANBAN, path).split(sep)[0]

// An import that brings in a value: not `import type`, and not a list whose every name is marked `type`.
function isValueImport(isTypeOnly: boolean, names: string): boolean {
  if (isTypeOnly) return false
  const listed = names.match(/^\{([^}]*)\}$/)
  if (!listed) return true
  const entries = listed[1].split(',').map(entry => entry.trim()).filter(Boolean)
  return entries.some(entry => !entry.startsWith('type '))
}

// Every run-time import from one package of the page into another, as `from-package/file -> to-package/file`.
function crossPackageImports(): { from: string; to: string }[] {
  return sourcesIn(KANBAN).flatMap(path => {
    const text = readFileSync(path, 'utf-8')
    return [...text.matchAll(IMPORT)]
      .filter(([, , typeWord, names]) => isValueImport(Boolean(typeWord), names))
      .map(([, , , , target]) => ({ from: path, to: resolve(dirname(path), target) }))
      .filter(({ from, to }) => packageOf(from) !== packageOf(to))
  })
}

describe('the board page packages', () => {
  it('should each be one the direction check knows', () => {
    const packages = readdirSync(KANBAN).filter(name => statSync(join(KANBAN, name)).isDirectory())
    expect(packages.filter(name => !(name in LAYERS))).toEqual([])
  })

  it('should import at run time only from a package below them', () => {
    const upward = crossPackageImports()
      .filter(({ from, to }) => LAYERS[packageOf(to)] >= LAYERS[packageOf(from)])
      .map(({ from, to }) => `${relative(KANBAN, from)} -> ${relative(KANBAN, to)}`)
    expect(upward).toEqual([])
  })
})
