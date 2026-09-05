#!/usr/bin/env node
/**
 * drawio-mockup.mjs — Lo-fi wireframe generator for Draw.io
 *
 * Reads a state JSON file describing screens, regions, and UI elements
 * and outputs a .drawio file with lo-fi wireframe shapes.
 *
 * State JSON schema  (save from AI or build incrementally):
 *
 *   {
 *     "target": "docs/ux/lo-fi.drawio",
 *     "screens": [{
 *       "name": "crowd manager — identities",
 *       "layout": "sidebar",           // sidebar|form|split-screen|modal|flyout|stack
 *       "col": 0, "row": 0,            // grid position
 *       "regions": [{
 *         "name": "tab bar",
 *         "slot": "body",              // panel|body|header|footer|left|right
 *         "type": "nav-tabs",          // nav-tabs|form|list|toolbar|button-bar|chrome
 *         "tabs": [{ "label": "Identities", "active": true }, ...]
 *       },{
 *         "name": "character tree",
 *         "slot": "panel",
 *         "type": "tree",
 *         "nodes": [
 *           { "label": "All Characters", "indent": 0, "expanded": true, "icon": "group" },
 *           { "label": "Crowd 1", "indent": 1, "expanded": true, "icon": "crowd" },
 *           { "label": "Character 1", "indent": 2, "icon": "character" }
 *         ]
 *       },{
 *         "name": "active roster",
 *         "slot": "body",
 *         "type": "listbox",
 *         "items": [
 *           { "label": "Character 1", "icon": "character" },
 *           { "label": "Character 2", "icon": "character", "selected": true }
 *         ]
 *       },{
 *         "name": "character actions",
 *         "slot": "body",
 *         "type": "context-menu",
 *         "groups": [
 *           { "items": [{ "label": "New", "shortcut": "Ctrl+N" }, { "label": "Edit", "shortcut": "Ctrl+E" }] },
 *           { "items": [{ "label": "Cut", "shortcut": "Ctrl+X" }, { "label": "Paste", "shortcut": "Ctrl+V" }] }
 *         ]
 *       },{
 *         "name": "explorer toolbar",
 *         "slot": "header",
 *         "type": "toolbar-icons",
 *         "buttons": [
 *           { "icon": "new-file", "tooltip": "New" },
 *           { "icon": "cut", "tooltip": "Cut" },
 *           { "icon": "add-crowd", "tooltip": "Add Crowd", "active": true }
 *         ]
 *       },{
 *         "name": "character filter",
 *         "slot": "panel",
 *         "type": "filter-bar",
 *         "placeholder": "Search characters…",
 *         "value": "Spyder"
 *       },{
 *         "name": "browse characters",
 *         "slot": "body",
 *         "type": "browse-panel",
 *         "categories": [
 *           { "label": "All Characters", "icon": "group" },
 *           { "label": "Heroes", "icon": "hero" }
 *         ]
 *       },{
 *         "name": "identity list",
 *         "slot": "body",
 *         "type": "list",
 *         "columns": ["name","type","active","default"],
 *         "rows": 3,
 *         "actions": [{ "label": "Add" }, { "label": "Remove", "primary": true }]
 *       },{
 *         "name": "ability config",
 *         "slot": "body",
 *         "type": "form",
 *         "fields": [
 *           { "label": "Name",           "input": "text" },
 *           { "label": "Activation Key", "input": "text" },
 *           { "label": "Persistent",     "input": "checkbox" },
 *           { "label": "Type",           "input": "dropdown", "options": ["Model","Costume"] }
 *         ],
 *         "buttons": [{ "label": "Save", "primary": true }, { "label": "Cancel" }]
 *       },{
 *         "name": "main toolbar",
 *         "slot": "header",
 *         "type": "toolbar",
 *         "buttons": [{ "label": "File" }, { "label": "Edit" }, { "label": "View" }]
 *       }]
 *     }],
 *     "connections": [
 *       { "from": "screen A", "to": "screen B", "label": "saves" }
 *     ]
 *   }
 *
 * Commands:
 *   save --state <path>  --out <path>
 *   init --out <path>
 */

import { readFileSync, writeFileSync, existsSync } from 'fs'
import { resolve, dirname } from 'path'

// ─── Layout templates (slot names per layout) ────────────────────────────────
const TEMPLATES = {
  sidebar:      { columns: [{ name: 'panel', w: 0.33 }, { name: 'body',  w: 0.67 }] },
  'split-screen':{ columns: [{ name: 'left',  w: 0.50 }, { name: 'right', w: 0.50 }] },
  flyout:       { columns: [{ name: 'body',  w: 0.65 }, { name: 'panel', w: 0.35 }] },
  form:         { columns: [{ name: 'body',  w: 1.00 }] },
  modal:        { columns: [{ name: 'body',  w: 1.00 }] },
  stack:        { columns: [{ name: 'body',  w: 1.00 }] },
}
function getTemplate(layoutName) {
  return TEMPLATES[layoutName] || TEMPLATES.stack
}

// ─── Constants ────────────────────────────────────────────────────────────────
const SCREEN_W    = 760
const SCREEN_HDR  = 32
const PAD         = 12
const COL_GAP     = 10
const GAP_X       = 140
const GAP_Y       = 80
const START_X     = 60
const START_Y     = 60

const CHROME_H    = 28
const TAB_H       = 30
const TOOLBAR_H   = 34
const REGION_HDR  = 22
const LIST_COL_H  = 22
const LIST_ROW_H  = 22
const FIELD_H     = 28
const FIELD_GAP   = 4
const BTN_ROW_H   = 34
const BTN_MIN_W   = 80
const BTN_GAP     = 6

// Tree-specific
const TREE_NODE_H   = 24
const TREE_INDENT_W = 20

// Listbox-specific
const LISTBOX_ITEM_H = 28

// Context menu
const CTX_ITEM_H     = 22
const CTX_SEP_H      = 8
const CTX_MENU_W     = 180

// Toolbar icons
const ICON_BTN_SIZE  = 28
const ICON_BTN_GAP   = 4

// Filter bar
const FILTER_BAR_H   = 30

// Browse panel
const BROWSE_BTN_W   = 100
const BROWSE_BTN_H   = 36
const BROWSE_GAP     = 6

// ─── Icon glyphs (Unicode approximations for lo-fi) ──────────────────────────
const ICON_GLYPHS = {
  'group':         '👥',
  'crowd':         '👥',
  'character':     '👤',
  'folder':        '📁',
  'file':          '📄',
  'ability':       '⚡',
  'movement':      '🏃',
  'power':         '💪',
  'fx':            '✨',
  'sound':         '♪',
  'sequence':      '▶',
  'identity':      '🎭',
  'hero':          '🦸',
  'villain':       '😈',
  'new-file':      '📄',
  'cut':           '✂',
  'copy':          '📋',
  'paste':         '📌',
  'add-crowd':     '👥+',
  'add-character': '👤+',
  'edit':          '✏',
  'delete':        '🗑',
  'save':          '💾',
  'link':          '🔗',
  'spawn':         '⊕',
  'place':         '📍',
  'navigate':      '🧭',
  'target':        '🎯',
}
function iconGlyph(iconName) {
  return ICON_GLYPHS[iconName] || '■'
}

// ─── Styles ──────────────────────────────────────────────────────────────────
const S = {
  screen:
    'rounded=0;whiteSpace=wrap;html=1;' +
    'fillColor=#ffffff;strokeColor=#000000;strokeWidth=2;' +
    'fontStyle=1;fontSize=13;verticalAlign=top;align=center;',
  screenModal:
    'rounded=1;arcSize=3;whiteSpace=wrap;html=1;' +
    'fillColor=#ffffff;strokeColor=#000000;strokeWidth=2;' +
    'fontStyle=1;fontSize=13;verticalAlign=top;align=center;',
  regionBox:
    'whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;strokeWidth=1;' +
    'fontStyle=1;fontSize=11;verticalAlign=top;align=left;',
  regionLabel:
    'text;html=1;strokeColor=none;fillColor=none;align=left;' +
    'verticalAlign=middle;fontStyle=1;fontSize=11;',
  chrome:
    'whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#cccccc;strokeWidth=1;' +
    'fontSize=11;fontStyle=2;verticalAlign=middle;align=left;',
  tabStrip:
    'whiteSpace=wrap;html=1;fillColor=#e8e8e8;strokeColor=#cccccc;strokeWidth=1;',
  tabActive:
    'rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;' +
    'fontStyle=1;fontSize=11;verticalAlign=bottom;align=center;',
  tabInactive:
    'rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#cccccc;' +
    'fontSize=11;verticalAlign=bottom;align=center;',
  toolbar:
    'whiteSpace=wrap;html=1;fillColor=#f0f0f0;strokeColor=#cccccc;strokeWidth=1;',
  toolbarBtn:
    'rounded=1;arcSize=20;whiteSpace=wrap;html=1;fillColor=#ffffff;' +
    'strokeColor=#999999;fontSize=10;',
  // Toolbar icon buttons (square)
  iconBtn:
    'rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=#ffffff;' +
    'strokeColor=#999999;fontSize=14;verticalAlign=middle;align=center;',
  iconBtnActive:
    'rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=#dae8fc;' +
    'strokeColor=#6c8ebf;fontSize=14;verticalAlign=middle;align=center;strokeWidth=2;',
  // Tree
  treeNodeExpanded:
    'text;html=1;strokeColor=none;fillColor=none;align=left;' +
    'verticalAlign=middle;fontSize=10;fontStyle=1;',
  treeNodeCollapsed:
    'text;html=1;strokeColor=none;fillColor=none;align=left;' +
    'verticalAlign=middle;fontSize=10;fontStyle=1;',
  treeNodeLeaf:
    'text;html=1;strokeColor=none;fillColor=none;align=left;' +
    'verticalAlign=middle;fontSize=10;',
  treeNodeSelected:
    'whiteSpace=wrap;html=1;fillColor=#c8e6c9;strokeColor=#4caf50;' +
    'fontSize=10;fontStyle=1;verticalAlign=middle;align=left;rounded=1;arcSize=8;',
  // Listbox
  listboxItem:
    'whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e0e0e0;' +
    'fontSize=10;verticalAlign=middle;align=left;spacingLeft=8;',
  listboxItemSelected:
    'whiteSpace=wrap;html=1;fillColor=#c8e6c9;strokeColor=#4caf50;' +
    'fontSize=10;fontStyle=1;verticalAlign=middle;align=left;spacingLeft=8;',
  listboxItemDimmed:
    'whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#e0e0e0;' +
    'fontSize=10;fontStyle=2;fontColor=#999999;verticalAlign=middle;align=left;spacingLeft=8;',
  // Context menu
  ctxMenuBox:
    'rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;' +
    'strokeWidth=1;shadow=1;',
  ctxMenuItem:
    'text;html=1;strokeColor=none;fillColor=none;align=left;' +
    'verticalAlign=middle;fontSize=10;',
  ctxMenuSep:
    'line;strokeWidth=1;strokeColor=#cccccc;fillColor=none;',
  // Filter bar
  filterBar:
    'whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;' +
    'fontSize=10;verticalAlign=middle;align=left;spacingLeft=8;',
  filterClear:
    'ellipse;whiteSpace=wrap;html=1;fillColor=#f0f0f0;strokeColor=#999999;' +
    'fontSize=8;verticalAlign=middle;align=center;',
  // Browse panel
  browseBtn:
    'rounded=1;arcSize=15;whiteSpace=wrap;html=1;fillColor=#f5f5f5;' +
    'strokeColor=#999999;fontSize=10;verticalAlign=middle;align=center;',
  browseBtnIcon:
    'text;html=1;strokeColor=none;fillColor=none;align=center;' +
    'verticalAlign=middle;fontSize=16;',
  // List
  listColHdr:
    'whiteSpace=wrap;html=1;fillColor=#e8e8e8;strokeColor=#cccccc;' +
    'fontStyle=1;fontSize=10;verticalAlign=middle;align=left;',
  listRow:
    'whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#cccccc;' +
    'fontSize=10;verticalAlign=middle;align=left;',
  listActionBtn:
    'rounded=1;arcSize=30;whiteSpace=wrap;html=1;fillColor=#f5f5f5;' +
    'strokeColor=#999999;fontSize=10;',
  listActionBtnPrimary:
    'rounded=1;arcSize=30;whiteSpace=wrap;html=1;fillColor=#dae8fc;' +
    'strokeColor=#6c8ebf;fontSize=10;fontStyle=1;',
  // Form
  fieldLabel:
    'text;html=1;strokeColor=none;fillColor=none;align=right;' +
    'verticalAlign=middle;fontSize=10;',
  fieldInput:
    'whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;' +
    'fontSize=10;verticalAlign=middle;align=left;',
  fieldInputFocus:
    'whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;strokeWidth=2;' +
    'fontSize=10;verticalAlign=middle;align=left;',
  fieldCheck:
    'text;html=1;strokeColor=none;fillColor=none;align=left;' +
    'verticalAlign=middle;fontSize=10;',
  fieldDropdown:
    'whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;' +
    'fontSize=10;verticalAlign=middle;align=left;',
  btnPrimary:
    'rounded=1;arcSize=25;whiteSpace=wrap;html=1;fillColor=#dae8fc;' +
    'strokeColor=#6c8ebf;fontStyle=1;fontSize=10;',
  btnSecondary:
    'rounded=1;arcSize=25;whiteSpace=wrap;html=1;fillColor=#f5f5f5;' +
    'strokeColor=#999999;fontSize=10;',
  // Connection
  edge:
    'edgeStyle=orthogonalEdgeStyle;html=1;' +
    'strokeColor=#000000;endArrow=block;endFill=1;fontSize=10;',
  callout:
    'text;html=1;strokeColor=none;fillColor=none;' +
    'align=left;verticalAlign=top;whiteSpace=wrap;overflow=hidden;fontSize=10;',
}

// ─── XML helpers ─────────────────────────────────────────────────────────────
function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

let _id = 2
function nextId() { return _id++ }
function resetIds() { _id = 2 }

function cell({ id, value = '', style, vertex, edge, parent = '1',
                x, y, w, h, source, target, waypoints = [] }) {
  const geo = waypoints.length
    ? `<mxGeometry relative="1" as="geometry"><Array as="points">${
        waypoints.map(([px, py]) => `<mxPoint x="${px}" y="${py}"/>`).join('')
      }</Array></mxGeometry>`
    : `<mxGeometry x="${x ?? 0}" y="${y ?? 0}" width="${w ?? 100}" height="${h ?? 40}" as="geometry"/>`
  const vAttr   = vertex ? ' vertex="1"' : ''
  const eAttr   = edge   ? ' edge="1"'   : ''
  const srcAttr = source ? ` source="${source}"` : ''
  const tgtAttr = target ? ` target="${target}"` : ''
  return `                <mxCell id="${id}" value="${esc(value)}" style="${style}"${vAttr}${eAttr}${srcAttr}${tgtAttr} parent="${parent}">\n                    ${geo}\n                </mxCell>`
}

// ─── Region height estimation ─────────────────────────────────────────────────
function regionHeight(r, colW) {
  if (!r) return 0
  switch (r.type) {
    case 'chrome':      return CHROME_H
    case 'toolbar':
    case 'button-bar':  return TOOLBAR_H
    case 'toolbar-icons': return ICON_BTN_SIZE + PAD * 2
    case 'nav-tabs':    return TAB_H + PAD
    case 'filter-bar':  return FILTER_BAR_H + PAD
    case 'tree': {
      const nodes = r.nodes?.length ?? 3
      return REGION_HDR + TREE_NODE_H * nodes + PAD
    }
    case 'listbox': {
      const items = r.items?.length ?? 3
      return REGION_HDR + LISTBOX_ITEM_H * items + PAD
    }
    case 'context-menu': {
      const groups = r.groups ?? []
      let totalItems = 0
      groups.forEach((g, i) => {
        totalItems += g.items?.length ?? 0
        if (i < groups.length - 1) totalItems += 0.4 // separator
      })
      return REGION_HDR + CTX_ITEM_H * totalItems + CTX_SEP_H * Math.max(0, groups.length - 1) + PAD
    }
    case 'browse-panel': {
      const cats = r.categories?.length ?? 0
      const cols = Math.max(1, Math.floor((colW - PAD) / (BROWSE_BTN_W + BROWSE_GAP)))
      const rows = Math.ceil(cats / cols)
      return REGION_HDR + (BROWSE_BTN_H + BROWSE_GAP) * rows + PAD
    }
    case 'list': {
      const rows    = r.rows ?? 3
      const actions = r.actions?.length ?? 0
      const btnRow  = actions > 0 ? BTN_ROW_H : 0
      return REGION_HDR + LIST_COL_H + LIST_ROW_H * rows + btnRow + PAD
    }
    case 'form': {
      const fields  = r.fields?.length ?? 0
      const buttons = r.buttons?.length ?? 0
      const btnRow  = buttons > 0 ? BTN_ROW_H : 0
      return REGION_HDR + FIELD_H * fields + FIELD_GAP * Math.max(0, fields - 1) + btnRow + PAD
    }
    default: return REGION_HDR + LIST_ROW_H * 3 + PAD
  }
}

// ─── Screen height ────────────────────────────────────────────────────────────
function screenHeight(screen) {
  const tmpl     = getTemplate(screen.layout)
  const regions  = screen.regions ?? []
  const contentW = SCREEN_W - PAD * 2
  const adjW     = contentW - (tmpl.columns.length - 1) * COL_GAP
  const knownSlots = new Set(tmpl.columns.map(c => c.name))
  const defSlot    = tmpl.columns[0]?.name ?? 'body'

  const headers  = regions.filter(r => r.slot === 'header')
  const footers  = regions.filter(r => r.slot === 'footer')
  const colRegs  = regions
    .filter(r => r.slot !== 'header' && r.slot !== 'footer')
    .map(r => ({ ...r, slot: knownSlots.has(r.slot) ? r.slot : defSlot }))

  let h = SCREEN_HDR + PAD
  headers.forEach(r => { h += regionHeight(r, contentW) })
  footers.forEach(r => { h += regionHeight(r, contentW) })

  let maxColH = 0
  for (const col of tmpl.columns) {
    const cw   = Math.round(col.w * adjW)
    const colH = colRegs.filter(r => r.slot === col.name).reduce((s, r) => s + regionHeight(r, cw), 0)
    if (colH > maxColH) maxColH = colH
  }
  return h + maxColH + PAD
}

// ─── Region renderers ─────────────────────────────────────────────────────────

function renderTree(r, cells, sid, rx, ry, rw) {
  const nodes = r.nodes ?? []

  cells.push(cell({ id: nextId(), value: `<b>${r.name}</b>`, style: S.regionLabel, vertex: true, parent: sid, x: rx, y: ry, w: rw, h: REGION_HDR }))
  let cy = ry + REGION_HDR

  for (const node of nodes) {
    const indent = (node.indent ?? 0) * TREE_INDENT_W
    const icon = node.icon ? iconGlyph(node.icon) + ' ' : ''
    let chevron = ''
    if (node.expanded === true) chevron = '▼ '
    else if (node.expanded === false) chevron = '▶ '

    const label = `${chevron}${icon}${node.label}`

    if (node.selected) {
      cells.push(cell({ id: nextId(), value: label, style: S.treeNodeSelected,
        vertex: true, parent: sid,
        x: rx + indent, y: cy, w: rw - indent, h: TREE_NODE_H }))
    } else {
      const style = node.expanded !== undefined ? S.treeNodeExpanded : S.treeNodeLeaf
      cells.push(cell({ id: nextId(), value: label, style,
        vertex: true, parent: sid,
        x: rx + indent, y: cy, w: rw - indent, h: TREE_NODE_H }))
    }
    cy += TREE_NODE_H
  }

  return cy - ry + PAD
}

function renderListbox(r, cells, sid, rx, ry, rw) {
  const items = r.items ?? []

  cells.push(cell({ id: nextId(), value: `<b>${r.name}</b>`, style: S.regionLabel, vertex: true, parent: sid, x: rx, y: ry, w: rw, h: REGION_HDR }))
  let cy = ry + REGION_HDR

  for (const item of items) {
    const icon = item.icon ? iconGlyph(item.icon) + ' ' : ''
    const label = `${icon}${item.label}`
    let style = S.listboxItem
    if (item.selected) style = S.listboxItemSelected
    else if (item.dimmed) style = S.listboxItemDimmed

    cells.push(cell({ id: nextId(), value: label, style,
      vertex: true, parent: sid,
      x: rx, y: cy, w: rw, h: LISTBOX_ITEM_H }))
    cy += LISTBOX_ITEM_H
  }

  return cy - ry + PAD
}

function renderContextMenu(r, cells, sid, rx, ry, rw) {
  const groups = r.groups ?? []
  const menuW = Math.min(CTX_MENU_W, rw)

  cells.push(cell({ id: nextId(), value: `<b>${r.name}</b>`, style: S.regionLabel, vertex: true, parent: sid, x: rx, y: ry, w: rw, h: REGION_HDR }))
  let cy = ry + REGION_HDR

  // Menu container height
  let menuH = 0
  groups.forEach((g, i) => {
    menuH += (g.items?.length ?? 0) * CTX_ITEM_H
    if (i < groups.length - 1) menuH += CTX_SEP_H
  })
  menuH += 8 // top/bottom padding

  const menuId = nextId()
  cells.push(cell({ id: menuId, value: '', style: S.ctxMenuBox, vertex: true, parent: sid, x: rx, y: cy, w: menuW, h: menuH }))

  let iy = cy + 4
  for (let gi = 0; gi < groups.length; gi++) {
    const group = groups[gi]
    for (const item of (group.items ?? [])) {
      const shortcut = item.shortcut ?? ''
      const padded = shortcut ? `${item.label}${'  '.repeat(Math.max(1, Math.floor((menuW - item.label.length * 6 - shortcut.length * 6) / 12)))}${shortcut}` : item.label
      cells.push(cell({ id: nextId(), value: padded, style: S.ctxMenuItem,
        vertex: true, parent: sid,
        x: rx + 4, y: iy, w: menuW - 8, h: CTX_ITEM_H }))
      iy += CTX_ITEM_H
    }
    if (gi < groups.length - 1) {
      cells.push(cell({ id: nextId(), value: '', style: S.ctxMenuSep,
        vertex: true, parent: sid,
        x: rx + 4, y: iy + 3, w: menuW - 8, h: 1 }))
      iy += CTX_SEP_H
    }
  }

  return (iy - ry) + 4 + PAD
}

function renderToolbarIcons(r, cells, sid, rx, ry, rw) {
  const btns = r.buttons ?? []

  cells.push(cell({ id: nextId(), value: '', style: S.toolbar, vertex: true, parent: sid, x: rx, y: ry, w: rw, h: ICON_BTN_SIZE + PAD * 2 }))

  let bx = rx + PAD
  for (const b of btns) {
    const glyph = iconGlyph(b.icon)
    const style = b.active ? S.iconBtnActive : S.iconBtn
    cells.push(cell({ id: nextId(), value: glyph, style,
      vertex: true, parent: sid,
      x: bx, y: ry + PAD, w: ICON_BTN_SIZE, h: ICON_BTN_SIZE }))
    bx += ICON_BTN_SIZE + ICON_BTN_GAP
  }

  return ICON_BTN_SIZE + PAD * 2
}

function renderFilterBar(r, cells, sid, rx, ry, rw) {
  const displayText = r.value || r.placeholder || 'Search…'

  cells.push(cell({ id: nextId(), value: displayText, style: S.filterBar,
    vertex: true, parent: sid,
    x: rx, y: ry, w: rw - 24, h: FILTER_BAR_H }))

  // Clear button
  cells.push(cell({ id: nextId(), value: '✕', style: S.filterClear,
    vertex: true, parent: sid,
    x: rx + rw - 22, y: ry + 4, w: 22, h: 22 }))

  return FILTER_BAR_H + PAD
}

function renderBrowsePanel(r, cells, sid, rx, ry, rw) {
  const categories = r.categories ?? []

  cells.push(cell({ id: nextId(), value: `<b>${r.name}</b>`, style: S.regionLabel, vertex: true, parent: sid, x: rx, y: ry, w: rw, h: REGION_HDR }))
  let cy = ry + REGION_HDR

  const cols = Math.max(1, Math.floor((rw - PAD) / (BROWSE_BTN_W + BROWSE_GAP)))
  let col = 0
  let rowY = cy

  for (const cat of categories) {
    const bx = rx + col * (BROWSE_BTN_W + BROWSE_GAP)
    const icon = cat.icon ? iconGlyph(cat.icon) : ''
    const label = icon ? `${icon} ${cat.label}` : cat.label
    cells.push(cell({ id: nextId(), value: label, style: S.browseBtn,
      vertex: true, parent: sid,
      x: bx, y: rowY, w: BROWSE_BTN_W, h: BROWSE_BTN_H }))
    col++
    if (col >= cols) {
      col = 0
      rowY += BROWSE_BTN_H + BROWSE_GAP
    }
  }
  if (col > 0) rowY += BROWSE_BTN_H + BROWSE_GAP

  return rowY - ry + PAD
}

function renderNavTabs(r, cells, sid, rx, ry, rw) {
  const tabs    = r.tabs ?? []
  const stripId = nextId()
  cells.push(cell({ id: stripId, value: '', style: S.tabStrip, vertex: true, parent: sid, x: rx, y: ry, w: rw, h: TAB_H }))
  const tabW = Math.max(80, Math.round(rw / Math.max(1, tabs.length)))
  tabs.forEach((t, i) => {
    cells.push(cell({ id: nextId(), value: t.label, style: t.active ? S.tabActive : S.tabInactive,
      vertex: true, parent: sid,
      x: rx + i * tabW, y: ry, w: tabW, h: TAB_H }))
  })
  return TAB_H + PAD
}

function renderToolbar(r, cells, sid, rx, ry, rw) {
  const btns = r.buttons ?? []
  cells.push(cell({ id: nextId(), value: '', style: S.toolbar, vertex: true, parent: sid, x: rx, y: ry, w: rw, h: TOOLBAR_H }))
  let bx = rx + 6
  btns.forEach(b => {
    const bw = Math.max(BTN_MIN_W, b.label.length * 7 + 16)
    cells.push(cell({ id: nextId(), value: b.label, style: S.toolbarBtn, vertex: true, parent: sid, x: bx, y: ry + 4, w: bw, h: TOOLBAR_H - 8 }))
    bx += bw + BTN_GAP
  })
  return TOOLBAR_H
}

function renderList(r, cells, sid, rx, ry, rw) {
  const cols    = r.columns ?? []
  const rows    = r.rows ?? 3
  const actions = r.actions ?? []

  cells.push(cell({ id: nextId(), value: `<b>${r.name}</b>`, style: S.regionLabel, vertex: true, parent: sid, x: rx, y: ry, w: rw, h: REGION_HDR }))
  let cy = ry + REGION_HDR

  const colW = cols.length > 0 ? Math.floor(rw / cols.length) : rw
  cols.forEach((c, i) => {
    cells.push(cell({ id: nextId(), value: c, style: S.listColHdr, vertex: true, parent: sid, x: rx + i * colW, y: cy, w: colW, h: LIST_COL_H }))
  })
  cy += LIST_COL_H

  for (let row = 0; row < rows; row++) {
    const rowStyle = row % 2 === 0 ? S.listRow : S.listRow.replace('#ffffff', '#fafafa')
    if (cols.length > 0) {
      cols.forEach((_, i) => {
        cells.push(cell({ id: nextId(), value: row === 0 ? '···' : '', style: rowStyle, vertex: true, parent: sid, x: rx + i * colW, y: cy, w: colW, h: LIST_ROW_H }))
      })
    } else {
      cells.push(cell({ id: nextId(), value: row === 0 ? '···' : '', style: rowStyle, vertex: true, parent: sid, x: rx, y: cy, w: rw, h: LIST_ROW_H }))
    }
    cy += LIST_ROW_H
  }

  if (actions.length > 0) {
    let bx = rx
    actions.forEach(a => {
      const bw = Math.max(BTN_MIN_W, a.label.length * 6 + 16)
      cells.push(cell({ id: nextId(), value: a.label,
        style: a.primary ? S.listActionBtnPrimary : S.listActionBtn,
        vertex: true, parent: sid, x: bx, y: cy + 4, w: bw, h: BTN_ROW_H - 8 }))
      bx += bw + BTN_GAP
    })
    cy += BTN_ROW_H
  }

  return cy - ry + PAD
}

function renderForm(r, cells, sid, rx, ry, rw) {
  const fields  = r.fields ?? []
  const buttons = r.buttons ?? []
  const LABEL_W = Math.round(rw * 0.36)
  const INPUT_W = rw - LABEL_W - 4

  cells.push(cell({ id: nextId(), value: `<b>${r.name}</b>`, style: S.regionLabel, vertex: true, parent: sid, x: rx, y: ry, w: rw, h: REGION_HDR }))
  let cy = ry + REGION_HDR

  fields.forEach((f, i) => {
    const gap = i > 0 ? FIELD_GAP : 0
    cy += gap

    if (f.input === 'checkbox' || f.input === 'radio') {
      const prefix = f.input === 'checkbox' ? '☐' : '○'
      cells.push(cell({ id: nextId(), value: `${prefix}  ${f.label}`,
        style: S.fieldCheck, vertex: true, parent: sid,
        x: rx + LABEL_W + 4, y: cy, w: INPUT_W, h: FIELD_H }))
    } else {
      cells.push(cell({ id: nextId(), value: f.label,
        style: S.fieldLabel, vertex: true, parent: sid,
        x: rx, y: cy, w: LABEL_W, h: FIELD_H }))
      let inputValue = ''
      if (f.input === 'dropdown') inputValue = (f.options?.[0] ?? '') + '  ▾'
      const inputStyle = f.input === 'dropdown' ? S.fieldDropdown : S.fieldInput
      cells.push(cell({ id: nextId(), value: inputValue,
        style: inputStyle, vertex: true, parent: sid,
        x: rx + LABEL_W + 4, y: cy, w: INPUT_W, h: FIELD_H }))
    }
    cy += FIELD_H
  })

  if (buttons.length > 0) {
    cy += FIELD_GAP * 2
    let bx = rx + LABEL_W + 4
    buttons.forEach(b => {
      const bw = Math.max(BTN_MIN_W, b.label.length * 7 + 20)
      cells.push(cell({ id: nextId(), value: b.label,
        style: b.primary ? S.btnPrimary : S.btnSecondary,
        vertex: true, parent: sid,
        x: bx, y: cy, w: bw, h: BTN_ROW_H - 8 }))
      bx += bw + BTN_GAP
    })
    cy += BTN_ROW_H
  }

  return cy - ry + PAD
}

function renderRegion(r, cells, sid, rx, ry, rw) {
  switch (r.type) {
    case 'chrome':
      cells.push(cell({ id: nextId(), value: r.name, style: S.chrome, vertex: true, parent: sid, x: rx, y: ry, w: rw, h: CHROME_H }))
      return CHROME_H
    case 'tree':
      return renderTree(r, cells, sid, rx, ry, rw)
    case 'listbox':
      return renderListbox(r, cells, sid, rx, ry, rw)
    case 'context-menu':
      return renderContextMenu(r, cells, sid, rx, ry, rw)
    case 'toolbar-icons':
      return renderToolbarIcons(r, cells, sid, rx, ry, rw)
    case 'filter-bar':
      return renderFilterBar(r, cells, sid, rx, ry, rw)
    case 'browse-panel':
      return renderBrowsePanel(r, cells, sid, rx, ry, rw)
    case 'nav-tabs':
      return renderNavTabs(r, cells, sid, rx, ry, rw)
    case 'toolbar':
    case 'button-bar':
      return renderToolbar(r, cells, sid, rx, ry, rw)
    case 'list':
      return renderList(r, cells, sid, rx, ry, rw)
    case 'form':
      return renderForm(r, cells, sid, rx, ry, rw)
    default:
      return 0
  }
}

// ─── Layout: assign x, y to each screen ──────────────────────────────────────
function layoutScreens(screens) {
  const byCol = {}
  for (const s of screens) {
    const col = s.col ?? 0
    if (!byCol[col]) byCol[col] = []
    byCol[col].push(s)
  }
  for (const col of Object.values(byCol)) {
    col.sort((a, b) => (a.row ?? 0) - (b.row ?? 0))
  }

  const cols = Object.keys(byCol).map(Number).sort((a, b) => a - b)
  const colX = {}
  let x = START_X
  for (const col of cols) {
    colX[col] = x
    x += SCREEN_W + GAP_X
  }

  const pos = {}
  for (const col of cols) {
    let y = START_Y
    for (const s of byCol[col]) {
      const h = screenHeight(s)
      pos[s.name] = { x: colX[col], y, w: SCREEN_W, h }
      y += h + GAP_Y
    }
  }
  return pos
}

// ─── XML generator ────────────────────────────────────────────────────────────
function generateXml(state) {
  resetIds()
  const screens     = state.screens ?? []
  const connections = state.connections ?? []
  const cells       = []
  cells.push(`                <mxCell id="0"/>`)
  cells.push(`                <mxCell id="1" parent="0"/>`)

  const pos = layoutScreens(screens)
  const sidMap = {}

  for (const screen of screens) {
    const p      = pos[screen.name]
    const sid    = nextId()
    sidMap[screen.name] = sid
    const style  = screen.layout === 'modal' ? S.screenModal : S.screen

    cells.push(cell({ id: sid, value: screen.name, style, vertex: true, parent: '1', x: p.x, y: p.y, w: p.w, h: p.h }))

    const tmpl      = getTemplate(screen.layout)
    const regions   = screen.regions ?? []
    const contentW  = p.w - PAD * 2
    const adjW      = contentW - (tmpl.columns.length - 1) * COL_GAP
    const knownSlots = new Set(tmpl.columns.map(c => c.name))
    const defSlot    = tmpl.columns[0]?.name ?? 'body'

    const headers  = regions.filter(r => r.slot === 'header')
    const footers  = regions.filter(r => r.slot === 'footer')
    const colRegs  = regions
      .filter(r => r.slot !== 'header' && r.slot !== 'footer')
      .map(r => ({ ...r, slot: knownSlots.has(r.slot) ? r.slot : defSlot }))

    let ry = SCREEN_HDR + PAD
    for (const r of headers) {
      ry += renderRegion(r, cells, sid, PAD, ry, contentW)
    }

    const colSectionY = ry
    let colX = PAD
    for (const col of tmpl.columns) {
      const cw  = Math.round(col.w * adjW)
      let   cry = colSectionY
      for (const r of colRegs.filter(r2 => r2.slot === col.name)) {
        cry += renderRegion(r, cells, sid, colX, cry, cw)
      }
      colX += cw + COL_GAP
    }

    let maxColH = 0
    for (const col of tmpl.columns) {
      const cw   = Math.round(col.w * adjW)
      const colH = colRegs.filter(r => r.slot === col.name).reduce((s, r) => s + regionHeight(r, cw), 0)
      if (colH > maxColH) maxColH = colH
    }
    ry += maxColH

    for (const r of footers) {
      ry += renderRegion(r, cells, sid, PAD, ry, contentW)
    }
  }

  // Merge A→B + B→A into one bidirectional arrow
  const connSet    = new Set(connections.map(c => `${c.from}|${c.to}`))
  const renderedConn = new Set()
  for (const conn of connections) {
    const key    = `${conn.from}|${conn.to}`
    const revKey = `${conn.to}|${conn.from}`
    if (renderedConn.has(key) || renderedConn.has(revKey)) continue
    const src = sidMap[conn.from]
    const tgt = sidMap[conn.to]
    if (!src || !tgt) continue
    const isBidi   = connSet.has(revKey)
    const revConn  = isBidi ? connections.find(c => c.from === conn.to && c.to === conn.from) : null
    const label    = isBidi && revConn?.label && revConn.label !== (conn.label ?? '')
      ? `${conn.label ?? ''} / ${revConn.label ?? ''}`.replace(/^ \/ | \/ $/g, '')
      : (conn.label ?? '')
    const style    = isBidi
      ? S.edge.replace('endArrow=block', 'startArrow=block;startFill=1;endArrow=block')
      : S.edge
    cells.push(cell({ id: nextId(), value: label, style, edge: true, parent: '1', source: src, target: tgt }))
    renderedConn.add(key)
    if (isBidi) renderedConn.add(revKey)
  }

  const totalW = Math.max(...Object.values(pos).map(p => p.x + p.w)) + 200
  const totalH = Math.max(...Object.values(pos).map(p => p.y + p.h)) + 200

  return `<mxfile host="drawio-mockup">
    <diagram id="lo-fi" name="Lo-fi Wireframe">
        <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="${totalW}" pageHeight="${totalH}" math="0" shadow="0">
            <root>
${cells.join('\n')}
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>`
}

// ─── Commands ─────────────────────────────────────────────────────────────────
function getArg(args, flag) {
  const i = args.indexOf(flag)
  return i !== -1 ? args[i + 1] : null
}

function cmdSave(args) {
  const statePath = getArg(args, '--state')
  const outPath   = getArg(args, '--out')
  if (!statePath || !outPath) {
    console.error('Usage: drawio-mockup.mjs save --state <state.json> --out <file.drawio>')
    process.exit(1)
  }
  const raw   = readFileSync(resolve(statePath), 'utf8').replace(/^\uFEFF/, '')
  const state = JSON.parse(raw)
  const xml   = generateXml(state)
  writeFileSync(resolve(outPath), xml, 'utf8')
  console.log(`[drawio-mockup] saved → ${resolve(outPath)}  (${state.screens?.length ?? 0} screens, ${state.connections?.length ?? 0} connections)`)
}

function cmdInit(args) {
  const outPath = getArg(args, '--out')
  if (!outPath) { console.error('Usage: drawio-mockup.mjs init --out <state.json>'); process.exit(1) }
  const template = {
    target: outPath.replace('.json', '.drawio'),
    screens: [],
    connections: [],
  }
  writeFileSync(resolve(outPath), JSON.stringify(template, null, 2), 'utf8')
  console.log(`[drawio-mockup] initialized → ${resolve(outPath)}`)
}

// ─── Entry point ──────────────────────────────────────────────────────────────
const [cmd, ...rest] = process.argv.slice(2)
if (cmd === 'save') cmdSave(rest)
else if (cmd === 'init') cmdInit(rest)
else {
  console.log(`drawio-mockup.mjs — Lo-fi wireframe generator

Commands:
  save --state <state.json> --out <lo-fi.drawio>
  init --out <state.json>

State JSON types:
  tree          → nodes: [{ label, indent, expanded, icon, selected }]
  listbox       → items: [{ label, icon, selected, dimmed }]
  context-menu  → groups: [{ items: [{ label, shortcut }] }]
  toolbar-icons → buttons: [{ icon, tooltip, active }]
  filter-bar    → placeholder, value
  browse-panel  → categories: [{ label, icon }]
  nav-tabs      → tabs: [{ label, active }]
  form          → fields: [{ label, input: text|textarea|dropdown|checkbox|radio, options? }]
                  buttons: [{ label, primary? }]
  list          → columns: [...], rows: N, actions: [{ label, primary? }]
  toolbar       → buttons: [{ label }]
  button-bar    → buttons: [{ label, primary? }]
  chrome        → name (plain labelled band)

Layouts: sidebar | split-screen | form | modal | flyout | stack
Slots:   panel | body | left | right | header | footer

Icons:   group, crowd, character, folder, file, ability, movement, power,
         fx, sound, sequence, identity, hero, villain, new-file, cut, copy,
         paste, add-crowd, add-character, edit, delete, save, link, spawn,
         place, navigate, target
`)
}
