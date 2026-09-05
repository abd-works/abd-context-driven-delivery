#!/usr/bin/env node
// drawio-ux.mjs — IA diagram CLI for draw.io
//
// Builds a draw.io (.drawio / mxGraph XML) IA diagram from a sequence of
// commands. State is stored in .drawio-ux-state.json in the current working
// directory. Each command reads, mutates, and writes the state file; `save`
// converts state → mxGraph XML.
//
// Usage:
//   node drawio-ux.mjs open        <file.drawio>
//   node drawio-ux.mjs clear
//   node drawio-ux.mjs add-screen  <name> [--layout <template>] [--tab-of <parent>]
//   node drawio-ux.mjs add-chrome  <screen> <region> [--slot <slot>] [--dimmed]
//   node drawio-ux.mjs add-list    <screen> <region> --slot <slot> --fields "f1 · f2" --actions "a1 · a2"
//   node drawio-ux.mjs add-form    <screen> <region> --slot <slot> --fields "f1 · f2"
//   node drawio-ux.mjs connect     <from> <to> --label "text" [--dashed]
//   node drawio-ux.mjs add-callout <screen> --stories "s1 · s2" --terms "t1 · t2"
//   node drawio-ux.mjs templates
//   node drawio-ux.mjs status
//   node drawio-ux.mjs save
//
// Layout templates (--layout):
//   stack        — single column, default
//   modal        — single column, rounded border (dialogs, floating panels)
//   form         — single column (config forms, editors)
//   sidebar      — panel (35%) | body (65%)
//   split-screen — left (50%) | right (50%)
//   flyout       — body (65%) | panel (35%)
//   holy-grail   — header / nav (25%) | body (50%) | aside (25%) / footer
//
// Slots ('header' and 'footer' are always full-width bands):
//   stack/modal/form → body
//   sidebar          → panel, body
//   split-screen     → left, right
//   flyout           → body, panel
//   holy-grail       → header, nav, body, aside, footer
//
// --dimmed: grey fill (#f5f5f5) for chrome that repeats unchanged on sibling
//   tab screens. ONLY use for repeated chrome. Data rows are NEVER dimmed.

import { readFileSync, writeFileSync, existsSync } from 'fs'
import { resolve } from 'path'

// ─── Layout templates ─────────────────────────────────────────────────────────

const TEMPLATES = {
  stack: {
    desc: 'Single-column stack — default',
    ascii: [
      '+----------+',
      '|   body   |',
      '|          |',
      '+----------+',
    ],
    columns: [{ name: 'body', x: 0, w: 1.00 }],
    rounded: false,
  },
  modal: {
    desc: 'Centered overlay dialog — rounded border',
    ascii: [
      '+--[MODAL]--------+',
      '|                 |',
      '|    body         |',
      '|                 |',
      '+-----------------+',
    ],
    columns: [{ name: 'body', x: 0, w: 1.00 }],
    rounded: true,
  },
  form: {
    desc: 'Single-column form — stacked inputs top to bottom',
    ascii: [
      '+------------------+',
      '| [field]          |',
      '| [field]          |',
      '| [submit]         |',
      '+------------------+',
    ],
    columns: [{ name: 'body', x: 0, w: 1.00 }],
    rounded: false,
  },
  sidebar: {
    desc: 'Left panel + right workspace (tree, nav, filter)',
    ascii: [
      '+--------+----------+',
      '| panel  |  body    |',
      '|        |          |',
      '+--------+----------+',
    ],
    columns: [
      { name: 'panel', x: 0,    w: 0.35 },
      { name: 'body',  x: 0.35, w: 0.65 },
    ],
    rounded: false,
  },
  'split-screen': {
    desc: 'Two equal functional columns',
    ascii: [
      '+----------+----------+',
      '|  left    |  right   |',
      '|          |          |',
      '+----------+----------+',
    ],
    columns: [
      { name: 'left',  x: 0,   w: 0.50 },
      { name: 'right', x: 0.5, w: 0.50 },
    ],
    rounded: false,
  },
  flyout: {
    desc: 'Main content + contextual side panel (slides in from edge)',
    ascii: [
      '+---------------+------+',
      '|  body         |panel |',
      '|               |      |',
      '+---------------+------+',
    ],
    columns: [
      { name: 'body',  x: 0,    w: 0.65 },
      { name: 'panel', x: 0.65, w: 0.35 },
    ],
    rounded: false,
  },
  'holy-grail': {
    desc: 'Header + left nav + body + right aside + footer',
    ascii: [
      '+---------------------+',
      '|      header         |',
      '+-----+--------+------+',
      '| nav |  body  |aside |',
      '+-----+--------+------+',
      '|      footer         |',
      '+---------------------+',
    ],
    columns: [
      { name: 'nav',   x: 0,    w: 0.25 },
      { name: 'body',  x: 0.25, w: 0.50 },
      { name: 'aside', x: 0.75, w: 0.25 },
    ],
    rounded: false,
  },
}

function getTemplate(layoutName) {
  return TEMPLATES[layoutName] || TEMPLATES.stack
}

// ─── Layout constants ─────────────────────────────────────────────────────────

const SCREEN_W   = 720   // screen box width
const SCREEN_HDR = 32    // height of bold name bar at top of screen
const CHROME_H   = 28    // height of a chrome region band
const ROW_H      = 22    // height of one representative list row
const ROW_COUNT  = 2     // number of representative rows shown
const VERB_H     = 24    // height of the verb-row strip (shown ABOVE data rows)
const FORM_ROW_H = 22    // height of a form field row
const LIST_HDR_H = 20    // region header label height
const PAD        = 12    // internal padding inside screens
const COL_GAP    = 10    // gap between side-by-side columns inside a screen
const GAP_X      = 120   // horizontal gap between screens
const GAP_Y      = 100   // vertical gap between stacked screens in same column
const START_X    = 50
const START_Y    = 200

// ─── Style contract ───────────────────────────────────────────────────────────
//
// Grey (fillColor=#f5f5f5 / strokeColor=#cccccc) is used ONLY via --dimmed
// on chrome that repeats unchanged across sibling tab screens.
// Data rows carry NO stroke border — they are content, not chrome.
// Verb rows use a light fill (#f0f0f0) to distinguish actions from data.

const S = {
  screen:
    'rounded=0;whiteSpace=wrap;html=1;' +
    'fillColor=#ffffff;strokeColor=#000000;strokeWidth=2;' +
    'fontStyle=1;fontSize=13;verticalAlign=top;align=center;',
  screenModal:
    'rounded=1;arcSize=4;whiteSpace=wrap;html=1;' +
    'fillColor=#ffffff;strokeColor=#000000;strokeWidth=2;' +
    'fontStyle=1;fontSize=13;verticalAlign=top;align=center;',
  chrome:
    'whiteSpace=wrap;html=1;' +
    'fillColor=#ffffff;strokeColor=#000000;strokeWidth=1;' +
    'fontStyle=2;fontSize=11;verticalAlign=middle;align=left;',
  chromeDimmed:
    'whiteSpace=wrap;html=1;' +
    'fillColor=#f5f5f5;strokeColor=#cccccc;strokeWidth=1;' +
    'fontStyle=2;fontSize=11;verticalAlign=middle;align=left;',
  listRegion:
    'whiteSpace=wrap;html=1;' +
    'fillColor=#ffffff;strokeColor=#000000;strokeWidth=1;' +
    'fontStyle=1;fontSize=11;verticalAlign=top;align=left;',
  row:
    'whiteSpace=nowrap;html=1;overflow=hidden;' +
    'fillColor=#ffffff;strokeColor=none;strokeWidth=0;' +
    'fontSize=10;verticalAlign=middle;align=left;',
  verbRow:
    'whiteSpace=wrap;html=1;' +
    'fillColor=#f0f0f0;strokeColor=#000000;strokeWidth=1;' +
    'fontStyle=0;fontSize=10;verticalAlign=top;align=left;',
  formRegion:
    'whiteSpace=wrap;html=1;' +
    'fillColor=#ffffff;strokeColor=#000000;strokeWidth=1;' +
    'fontStyle=1;fontSize=11;verticalAlign=top;align=left;',
  formRow:
    'whiteSpace=wrap;html=1;' +
    'fillColor=#ffffff;strokeColor=none;strokeWidth=0;' +
    'fontSize=10;verticalAlign=middle;align=left;',
  edge:
    'edgeStyle=orthogonalEdgeStyle;html=1;' +
    'strokeColor=#000000;endArrow=block;endFill=1;fontSize=10;',
  edgeDashed:
    'edgeStyle=orthogonalEdgeStyle;html=1;dashed=1;' +
    'strokeColor=#000000;endArrow=open;endFill=0;fontSize=10;',
  callout:
    'text;html=1;strokeColor=none;fillColor=none;' +
    'align=left;verticalAlign=top;whiteSpace=wrap;overflow=hidden;fontSize=10;',
}

// ─── State ────────────────────────────────────────────────────────────────────

const STATE_FILE = resolve(process.cwd(), '.drawio-ux-state.json')

function load() {
  if (!existsSync(STATE_FILE)) return { target: null, screens: [], connections: [] }
  return JSON.parse(readFileSync(STATE_FILE, 'utf8'))
}

function persist(state) {
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8')
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function slug(name) {
  return String(name).toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '')
}

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function parseArgs(args) {
  const flags = {}
  const pos   = []
  let i = 0
  while (i < args.length) {
    if (args[i].startsWith('--')) {
      const key  = args[i].slice(2)
      const next = args[i + 1]
      if (next !== undefined && !next.startsWith('--')) {
        flags[key] = next; i += 2
      } else {
        flags[key] = true; i++
      }
    } else {
      pos.push(args[i]); i++
    }
  }
  return { flags, pos }
}

function splitDot(str) {
  return String(str).split('·').map(s => s.trim()).filter(Boolean)
}

// ─── Region height ────────────────────────────────────────────────────────────

// Estimate the height needed for a verb/action row that wraps.
// availW: pixel width of the cell content area.
// Uses ~5.8px per character at fontSize=10 as a rough baseline.
function verbRowH(actions, availW) {
  if (!actions || actions.length === 0) return VERB_H
  const text = (actions).join(' · ')
  const charsPerLine = Math.max(12, Math.floor(availW / 5.8))
  const lines = Math.ceil(text.length / charsPerLine)
  return Math.max(VERB_H, lines * 15 + 6)  // 15px line-height + 6px padding
}

// estimatedPanelW: used by regionH when we don't yet know the actual column width.
// For sidebar (35% panel), use 35% of contentW; default to full contentW.
const EST_PANEL_W = Math.round((SCREEN_W - PAD * 2) * 0.35) - 8
const EST_BODY_W  = SCREEN_W - PAD * 2 - 8

function regionH(r, estW) {
  if (r.type === 'chrome') return CHROME_H
  if (r.type === 'list') {
    const w = estW ?? EST_BODY_W
    return LIST_HDR_H + verbRowH(r.actions, w) + ROW_H * ROW_COUNT + PAD
  }
  if (r.type === 'form')   return LIST_HDR_H + FORM_ROW_H * (r.fields?.length || 3) + PAD
  return 0
}

// ─── Region grouping ──────────────────────────────────────────────────────────
//
// 'header' and 'footer' slots are always full-width bands (top / bottom).
// All other slots are column regions. Unknown / missing slots fall back to
// the first column defined in the template ('body' for single-column templates).

function groupRegions(screen) {
  const tmpl       = getTemplate(screen.layout || 'stack')
  const knownSlots = new Set(tmpl.columns.map(c => c.name))
  const defaultSlot = tmpl.columns[0]?.name || 'body'

  const headers   = screen.regions.filter(r => r.slot === 'header')
  const footers   = screen.regions.filter(r => r.slot === 'footer')
  const colRegions = screen.regions
    .filter(r => r.slot !== 'header' && r.slot !== 'footer')
    .map(r => ({
      ...r,
      slot: (r.slot && knownSlots.has(r.slot)) ? r.slot : defaultSlot,
    }))

  return { headers, footers, colRegions, tmpl }
}

// ─── Screen height ────────────────────────────────────────────────────────────

function screenHeight(screen) {
  const { headers, footers, colRegions, tmpl } = groupRegions(screen)
  const contentW  = SCREEN_W - PAD * 2
  const adjustedW = contentW - (tmpl.columns.length - 1) * COL_GAP

  let h = SCREEN_HDR + PAD
  for (const r of headers) h += CHROME_H
  for (const r of footers) h += CHROME_H

  // Column section: height is the tallest column
  let maxColH = 0
  for (const col of tmpl.columns) {
    const colW  = Math.round(col.w * adjustedW) - 8
    const colH  = colRegions
      .filter(r => r.slot === col.name)
      .reduce((s, r) => s + regionH(r, colW), 0)
    if (colH > maxColH) maxColH = colH
  }
  h += maxColH

  return h + PAD
}

// ─── Canvas layout ────────────────────────────────────────────────────────────
//
// Each screen may declare { col, row } (both 0-based integers).
// Screens in the same col are stacked top-to-bottom by row.
// Cols are placed left-to-right by col index.
// Screens without col/row default to col=0, row=auto.

function layout(screens) {
  const pos = {}

  // Group by col, sort each col by row
  const cols = {}
  for (const s of screens) {
    const c = s.col ?? 0
    if (!cols[c]) cols[c] = []
    cols[c].push(s)
  }
  for (const c of Object.keys(cols)) {
    cols[c].sort((a, b) => (a.row ?? 0) - (b.row ?? 0))
  }

  let x = START_X
  for (const ci of Object.keys(cols).map(Number).sort((a, b) => a - b)) {
    let y = START_Y
    for (const s of cols[ci]) {
      const h = screenHeight(s)
      pos[s.name] = { x, y, w: SCREEN_W, h }
      y += h + GAP_Y
    }
    x += SCREEN_W + GAP_X
  }

  return pos
}

// ─── XML generation ───────────────────────────────────────────────────────────
//
// The VS Code draw.io extension requires sequential numeric cell IDs.
// We thread a plain counter object { v: number } through all helpers.

function mkCell(counter, { value, style, vertex, edge, source, target, parent, x, y, w, h, waypoints }) {
  const id = String(++counter.v)
  const parts = [
    `id="${id}"`,
    `value="${esc(value)}"`,
    `style="${style}"`,
    vertex ? 'vertex="1"' : '',
    edge   ? 'edge="1"'   : '',
    source ? `source="${source}"` : '',
    target ? `target="${target}"` : '',
    `parent="${parent}"`,
  ].filter(Boolean).join(' ')

  let geo
  if (waypoints?.length) {
    const pts = waypoints.map(p => `                            <mxPoint x="${p.x}" y="${p.y}"/>`).join('\n')
    geo = [
      `                    <mxGeometry relative="1" as="geometry">`,
      `                        <Array as="points">`,
      pts,
      `                        </Array>`,
      `                    </mxGeometry>`,
    ].join('\n')
  } else if (edge || x === undefined) {
    geo = `                    <mxGeometry relative="1" as="geometry"/>`
  } else {
    geo = `                    <mxGeometry x="${x}" y="${y}" width="${w}" height="${h}" as="geometry"/>`
  }

  return { id, xml: `                <mxCell ${parts}>\n${geo}\n                </mxCell>` }
}

function renderRegion(r, cells, counter, sid, rx, ry, rw) {
  if (r.type === 'chrome') {
    cells.push(mkCell(counter, {
      value: r.name,
      style: r.dimmed ? S.chromeDimmed : S.chrome,
      vertex: true, parent: sid,
      x: rx, y: ry, w: rw, h: CHROME_H,
    }).xml)
    return CHROME_H
  }

  if (r.type === 'list') {
    const vH  = verbRowH(r.actions, rw - 8)
    const rh  = LIST_HDR_H + vH + ROW_H * ROW_COUNT
    cells.push(mkCell(counter, {
      value: `<b>${r.name}</b>`, style: S.listRegion,
      vertex: true, parent: sid,
      x: rx, y: ry, w: rw, h: rh,
    }).xml)
    // Actions strip immediately below region header label (wraps as needed)
    const actions = (r.actions || []).join(' · ')
    cells.push(mkCell(counter, {
      value: actions, style: S.verbRow,
      vertex: true, parent: sid,
      x: rx + 4, y: ry + LIST_HDR_H, w: rw - 8, h: vH,
    }).xml)
    // Representative data rows below the action strip
    const fields = (r.fields || []).join(' · ')
    for (let i = 0; i < ROW_COUNT; i++) {
      cells.push(mkCell(counter, {
        value: fields, style: S.row,
        vertex: true, parent: sid,
        x: rx + 4, y: ry + LIST_HDR_H + vH + i * ROW_H, w: rw - 8, h: ROW_H,
      }).xml)
    }
    return rh + PAD
  }

  if (r.type === 'form') {
    const fieldCount = r.fields?.length || 3
    const rh = LIST_HDR_H + FORM_ROW_H * fieldCount
    cells.push(mkCell(counter, {
      value: `<b>${r.name}</b>`, style: S.formRegion,
      vertex: true, parent: sid,
      x: rx, y: ry, w: rw, h: rh,
    }).xml)
    for (let i = 0; i < fieldCount; i++) {
      cells.push(mkCell(counter, {
        value: (r.fields || [])[i] || '', style: S.formRow,
        vertex: true, parent: sid,
        x: rx + 4, y: ry + LIST_HDR_H + i * FORM_ROW_H, w: rw - 8, h: FORM_ROW_H,
      }).xml)
    }
    return rh + PAD
  }

  return 0
}

function generateXml(state) {
  const positions = layout(state.screens)
  const cells     = []
  const counter   = { v: 1 }   // starts at 1; cell "0" and "1" are root stubs

  // Pre-assign numeric IDs to screens so edges can reference them by name
  const screenNumId = {}
  for (const screen of state.screens) {
    screenNumId[screen.name] = String(++counter.v)
  }

  for (const screen of state.screens) {
    const pos = positions[screen.name]
    if (!pos) continue

    const sid     = screenNumId[screen.name]
    const tmplObj = getTemplate(screen.layout || 'stack')
    const style   = tmplObj.rounded ? S.screenModal : S.screen

    // Push screen cell directly with its pre-assigned id (don't call mkCell which auto-increments)
    const geoParts = `x="${pos.x}" y="${pos.y}" width="${pos.w}" height="${pos.h}" as="geometry"`
    const attrParts = `id="${sid}" value="${esc(screen.name)}" style="${style}" vertex="1" parent="1"`
    cells.push(`                <mxCell ${attrParts}>\n                    <mxGeometry ${geoParts}/>\n                </mxCell>`)

    const { headers, footers, colRegions, tmpl } = groupRegions(screen)
    const contentW = pos.w - PAD * 2
    let ry = SCREEN_HDR + PAD

    for (const r of headers) {
      ry += renderRegion(r, cells, counter, sid, PAD, ry, contentW)
    }

    const colSectionY = ry
    const numCols = tmpl.columns.length
    const adjustedW = contentW - (numCols - 1) * COL_GAP
    let colX = PAD
    for (const col of tmpl.columns) {
      const cw  = Math.round(col.w * adjustedW)
      let   cry = colSectionY
      for (const r of colRegions.filter(r2 => r2.slot === col.name)) {
        cry += renderRegion(r, cells, counter, sid, colX, cry, cw)
      }
      colX += cw + COL_GAP
    }

    let maxColH = 0
    for (const col of tmpl.columns) {
      const colH = colRegions
        .filter(r => r.slot === col.name)
        .reduce((s, r) => s + regionH(r), 0)
      if (colH > maxColH) maxColH = colH
    }
    ry += maxColH

    for (const r of footers) {
      ry += renderRegion(r, cells, counter, sid, PAD, ry, contentW)
    }

    // Callout annotation
    const lines = [
      screen.stories?.length ? `<b>Stories:</b> ${screen.stories.join(' · ')}` : '',
      screen.terms?.length   ? `<b>Domain terms:</b> ${screen.terms.join(' · ')}` : '',
    ].filter(Boolean)
    if (lines.length) {
      cells.push(mkCell(counter, {
        value: lines.join('<br>'),
        style: S.callout, vertex: true, parent: '1',
        x: pos.x, y: pos.y + pos.h + 6, w: pos.w, h: 52,
      }).xml)
    }
  }

  // Merge A→B + B→A into one bidirectional arrow
  const allConnKeys  = new Set(state.connections.map(c => `${c.from}|${c.to}`))
  const renderedConn = new Set()
  for (const conn of state.connections) {
    const key    = `${conn.from}|${conn.to}`
    const revKey = `${conn.to}|${conn.from}`
    if (renderedConn.has(key) || renderedConn.has(revKey)) continue
    const src = screenNumId[conn.from]
    const tgt = screenNumId[conn.to]
    if (!src || !tgt) continue

    const srcPos = positions[conn.from]
    const tgtPos = positions[conn.to]

    const isBidi  = allConnKeys.has(revKey)
    const revConn = isBidi ? state.connections.find(c => c.from === conn.to && c.to === conn.from) : null
    const label   = isBidi && revConn?.label && revConn.label !== (conn.label || '')
      ? `${conn.label || ''} / ${revConn.label || ''}`.replace(/^ \/ | \/ $/g, '')
      : (conn.label || '')

    // Same-column connections (options stacked vertically): exit left side of
    // source, route via a waypoint to the left, enter left side of target.
    const sameCol = srcPos && tgtPos && srcPos.x === tgtPos.x
    let waypoints
    let edgeStyle = conn.dashed ? S.edgeDashed : S.edge
    if (isBidi) edgeStyle = edgeStyle.replace('endArrow=block', 'startArrow=block;startFill=1;endArrow=block')
    if (sameCol) {
      const wx = srcPos.x - 30
      waypoints = [
        { x: wx, y: srcPos.y + srcPos.h },
        { x: wx, y: tgtPos.y },
      ]
      edgeStyle += 'exitX=0;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0;entryDx=0;entryDy=0;'
    }

    cells.push(mkCell(counter, {
      value: label,
      style: edgeStyle,
      edge: true, source: src, target: tgt, parent: '1',
      waypoints,
    }).xml)
    renderedConn.add(key)
    if (isBidi) renderedConn.add(revKey)
  }

  return [
    '<mxfile host="drawio-ux">',
    '    <diagram id="ia-diagram" name="Detailed IA">',
    '        <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="3300" pageHeight="2550" math="0" shadow="0">',
    '            <root>',
    '                <mxCell id="0"/>',
    '                <mxCell id="1" parent="0"/>',
    ...cells,
    '            </root>',
    '        </mxGraphModel>',
    '    </diagram>',
    generateSiteMapPage(state),
    '</mxfile>',
  ].join('\n')
}

// ─── Site map page ─────────────────────────────────────────────────────────────
// Second diagram page: one titled box per screen, labeled connector arrows only.
// Positioned using the same col/row grid as the detailed page (260px col, 90px row).

function generateSiteMapPage(state) {
  const screens = state.screens || []
  const conns   = state.connections || []

  const COL_W = 260
  const ROW_H = 90
  const BOX_W = 200
  const BOX_H = 48
  const PAD_X = 40
  const PAD_Y = 40

  // Group by col so rows within a col stack properly
  const colMap = {}
  for (const s of screens) {
    const col = s.col !== undefined ? s.col : 0
    if (!colMap[col]) colMap[col] = []
    colMap[col].push(s)
  }

  let idCtr = 5000
  const cells = []
  const nameToId = {}

  for (const [col, group] of Object.entries(colMap)) {
    const colNum = Number(col)
    // Sort by explicit row if present, else keep insertion order
    const sorted = [...group].sort((a, b) =>
      (a.row !== undefined ? a.row : 999) - (b.row !== undefined ? b.row : 999)
    )
    sorted.forEach((s, i) => {
      const row = s.row !== undefined ? s.row : i
      const x = PAD_X + colNum * COL_W
      const y = PAD_Y + row * ROW_H
      const id = String(++idCtr)
      nameToId[s.name] = id
      cells.push(
        `                <mxCell id="${id}" value="${esc(s.name)}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;strokeWidth=2;fontStyle=1;fontSize=12;verticalAlign=middle;align=center;" vertex="1" parent="1">`,
        `                    <mxGeometry x="${x}" y="${y}" width="${BOX_W}" height="${BOX_H}" as="geometry"/>`,
        `                </mxCell>`
      )
    })
  }

  // Connector arrows — merge A→B + B→A into one bidirectional arrow
  const siteConnSet  = new Set(conns.map(c => `${c.from}|${c.to}`))
  const siteRendered = new Set()
  for (const conn of conns) {
    const key    = `${conn.from}|${conn.to}`
    const revKey = `${conn.to}|${conn.from}`
    if (siteRendered.has(key) || siteRendered.has(revKey)) continue
    const srcId = nameToId[conn.from]
    const tgtId = nameToId[conn.to]
    if (!srcId || !tgtId) continue
    const id      = String(++idCtr)
    const isBidi  = siteConnSet.has(revKey)
    const revConn = isBidi ? conns.find(c => c.from === conn.to && c.to === conn.from) : null
    const label   = isBidi && revConn?.label && revConn.label !== (conn.label || '')
      ? `${conn.label || ''} / ${revConn.label || ''}`.replace(/^ \/ | \/ $/g, '')
      : (conn.label || '')
    const baseStyle = conn.dashed
      ? 'html=1;strokeColor=#000000;endArrow=block;endFill=1;fontSize=10;dashed=1;'
      : 'html=1;strokeColor=#000000;endArrow=block;endFill=1;fontSize=10;'
    const style = isBidi
      ? baseStyle.replace('endArrow=block', 'startArrow=block;startFill=1;endArrow=block')
      : baseStyle
    cells.push(
      `                <mxCell id="${id}" value="${esc(label)}" style="${style}" edge="1" source="${srcId}" target="${tgtId}" parent="1">`,
      `                    <mxGeometry relative="1" as="geometry"/>`,
      `                </mxCell>`
    )
    siteRendered.add(key)
    if (isBidi) siteRendered.add(revKey)
  }

  return [
    '    <diagram id="site-map" name="Site Map">',
    '        <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="3300" pageHeight="2550" math="0" shadow="0">',
    '            <root>',
    '                <mxCell id="0"/>',
    '                <mxCell id="1" parent="0"/>',
    ...cells,
    '            </root>',
    '        </mxGraphModel>',
    '    </diagram>',
  ].join('\n')
}

// ─── Command dispatch ─────────────────────────────────────────────────────────

const [,, cmd, ...rawArgs] = process.argv
const { flags, pos } = parseArgs(rawArgs)
const state = load()

switch (cmd) {

  case 'open': {
    state.target      = resolve(pos[0])
    state.screens     = state.screens     || []
    state.connections = state.connections || []
    persist(state)
    console.log(`[drawio-ux] target → ${state.target}`)
    break
  }

  case 'clear': {
    state.screens     = []
    state.connections = []
    persist(state)
    console.log('[drawio-ux] diagram cleared')
    break
  }

  case 'add-screen': {
    const name = pos[0]
    if (!name) { console.error('Usage: add-screen <name> [--layout <template>] [--col N] [--row N] [--tab-of <parent>]'); process.exit(1) }
    if (state.screens.find(s => s.name === name)) {
      console.log(`[drawio-ux] screen "${name}" already exists — skipping`)
      break
    }
    const layout = flags.layout || 'stack'
    if (!TEMPLATES[layout]) {
      console.error(`Unknown layout "${layout}". Run: node drawio-ux.mjs templates`)
      process.exit(1)
    }
    if (flags.col === undefined || flags.row === undefined) {
      console.warn(`[drawio-ux] WARNING: "${name}" added without --col/--row. Layout will be unpredictable.`)
      console.warn(`  Rule: always-visited screens go in row 0 (linear); optional screens stack in the same col as their trigger (options).`)
    }
    const entry = {
      name,
      layout,
      tabOf:   flags['tab-of'] || null,
      regions: [],
      stories: [],
      terms:   [],
    }
    if (flags.col !== undefined) entry.col = Number(flags.col)
    if (flags.row !== undefined) entry.row = Number(flags.row)
    state.screens.push(entry)
    persist(state)
    const pos_ = [layout, flags.col !== undefined ? `col ${flags.col}` : null, flags.row !== undefined ? `row ${flags.row}` : null].filter(Boolean).join(', ')
    console.log(`[drawio-ux] add-screen "${name}" (${pos_})`)
    break
  }

  case 'add-chrome': {
    const [screenName, regionName] = pos
    const screen = state.screens.find(s => s.name === screenName)
    if (!screen) { console.error(`Screen "${screenName}" not found`); process.exit(1) }
    const slot = flags.slot || 'body'
    screen.regions.push({
      name:   regionName,
      type:   'chrome',
      slot,
      dimmed: !!flags.dimmed,
    })
    persist(state)
    const opts = [slot !== 'body' ? `slot:${slot}` : '', flags.dimmed ? 'dimmed' : ''].filter(Boolean)
    console.log(`[drawio-ux] add-chrome "${regionName}" → "${screenName}"${opts.length ? ' (' + opts.join(', ') + ')' : ''}`)
    break
  }

  case 'add-list': {
    const [screenName, regionName] = pos
    const screen = state.screens.find(s => s.name === screenName)
    if (!screen) { console.error(`Screen "${screenName}" not found`); process.exit(1) }
    screen.regions.push({
      name:    regionName,
      type:    'list',
      slot:    flags.slot || 'body',
      fields:  splitDot(flags.fields  || ''),
      actions: splitDot(flags.actions || ''),
    })
    persist(state)
    console.log(`[drawio-ux] add-list "${regionName}" → "${screenName}" (slot: ${flags.slot || 'body'})`)
    break
  }

  case 'add-form': {
    const [screenName, regionName] = pos
    const screen = state.screens.find(s => s.name === screenName)
    if (!screen) { console.error(`Screen "${screenName}" not found`); process.exit(1) }
    screen.regions.push({
      name:   regionName,
      type:   'form',
      slot:   flags.slot || 'body',
      fields: splitDot(flags.fields || ''),
    })
    persist(state)
    console.log(`[drawio-ux] add-form "${regionName}" → "${screenName}" (slot: ${flags.slot || 'body'})`)
    break
  }

  case 'connect': {
    const [from, to] = pos
    if (!from || !to) { console.error('Usage: connect <from> <to> --label "text" [--dashed]'); process.exit(1) }
    state.connections.push({ from, to, label: flags.label || '', dashed: !!flags.dashed })
    persist(state)
    console.log(`[drawio-ux] connect "${from}" → "${to}" (${flags.label || ''})`)
    break
  }

  case 'add-callout': {
    const screenName = pos[0]
    const screen = state.screens.find(s => s.name === screenName)
    if (!screen) { console.error(`Screen "${screenName}" not found`); process.exit(1) }
    if (flags.stories) screen.stories = splitDot(flags.stories)
    if (flags.terms)   screen.terms   = splitDot(flags.terms)
    persist(state)
    console.log(`[drawio-ux] add-callout → "${screenName}"`)
    break
  }

  case 'save': {
    if (!state.target) { console.error('No target — run: open <file.drawio>'); process.exit(1) }
    writeFileSync(state.target, generateXml(state), 'utf8')
    console.log(`[drawio-ux] saved → ${state.target}  (${state.screens.length} screens, ${state.connections.length} connections)`)
    break
  }

  case 'templates': {
    for (const [name, tmpl] of Object.entries(TEMPLATES)) {
      console.log(`\n${name}  —  ${tmpl.desc}`)
      console.log(tmpl.ascii.join('\n'))
      console.log(`Slots: ${tmpl.columns.map(c => c.name).join(', ')}`)
    }
    break
  }

  case 'status': {
    console.log(`target:      ${state.target || '(none)'}`)
    console.log(`screens:     ${state.screens.length}`)
    for (const s of state.screens) {
      const tab = s.tabOf ? ` [tab of: ${s.tabOf}]` : ''
      console.log(`  • ${s.name}  layout:${s.layout || 'stack'}${tab}  (${s.regions.length} regions)`)
    }
    console.log(`connections: ${state.connections.length}`)
    for (const c of state.connections) {
      console.log(`  • "${c.from}" → "${c.to}"  (${c.label})`)
    }
    break
  }

  default: {
    console.log(`drawio-ux — draw.io IA diagram CLI

Commands:
  open        <file.drawio>
  clear
  add-screen  <name> [--layout <template>] [--tab-of <parent>]
  add-chrome  <screen> <region> [--slot <slot>] [--dimmed]
  add-list    <screen> <region> --slot <slot> --fields "f1 · f2" --actions "a1 · a2"
  add-form    <screen> <region> --slot <slot> --fields "f1 · f2"
  connect     <from> <to> --label "text" [--dashed]
  add-callout <screen> --stories "s1 · s2" --terms "t1 · t2"
  templates   (list all layout templates with ASCII diagrams)
  status
  save        (always writes two pages: "Detailed IA" + "Site Map")

Layout templates (--layout):
  stack        single column — default
  modal        single column, rounded border
  form         single column, form style
  sidebar      panel (35%) | body (65%)
  split-screen left (50%) | right (50%)
  flyout       body (65%) | panel (35%)
  holy-grail   header / nav | body | aside / footer

Special slots:
  header  full-width band above columns
  footer  full-width band below columns

Style rules:
  --dimmed  Chrome fills with grey (#f5f5f5). Use ONLY for chrome that repeats
            unchanged on sibling tab screens. Data rows are NEVER dimmed.

State is stored in .drawio-ux-state.json (cwd). No dependencies required.`)
  }
}
