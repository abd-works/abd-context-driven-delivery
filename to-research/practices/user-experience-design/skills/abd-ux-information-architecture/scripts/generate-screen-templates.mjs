#!/usr/bin/env node
// generate-screen-templates.mjs
//
// Generates one .md (ASCII art reference) + one .drawio (XML fragment) per
// UX layout template.  The .drawio files are valid draw.io files whose
// [slot-name] placeholder cells can be:
//   1. Copied into a target .drawio file (paste as XML)
//   2. Slot labels replaced with real region cells (list rows / form fields / verb rows)
//   3. Screen cell repositioned by changing x/y on the outer screen cell
//   4. IDs renamed from *_tmpl → *_yourscreenname to avoid collisions
//
// Run from repo root:
//   node skills/user-experience-design/abd-information-architecture/scripts/generate-screen-templates.mjs

import { writeFileSync, mkdirSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dir  = dirname(fileURLToPath(import.meta.url))
const OUT_DIR = resolve(__dir, '../screen-templates')

// ─── Template catalogue ───────────────────────────────────────────────────────

const TEMPLATES = [

  // ── 1. Screen & Core Page Skeletons ─────────────────────────────────────

  { name: 'dashboard', category: 'Screen & Core Page Skeletons', cli: null,
    desc: 'Grid of modular widgets/cards for data viz and quick actions.',
    slots: ['header', 'nav', 'main'],
    layout: { fullWidthTop: ['header'], columns: [{ name: 'nav', x: 0, w: 0.2 }, { name: 'main', x: 0.2, w: 0.8 }] },
    ascii: `
[Dashboard Layout]
┌───────────────────────────────────────┐
│ [Header]                              │
├───────┬───────────────────────────────┤
│       │ [Metric 1] [Metric 2]         │
│ Nav   │ ┌────────┐ ┌────────┐         │
│ Bar   │ │ Graph  │ │ Recent │         │
│       │ │ Block  │ │ Activity         │
│       │ └────────┘ └────────┘         │
└───────┴───────────────────────────────┘` },

  { name: 'feed', category: 'Screen & Core Page Skeletons', cli: null,
    desc: 'Endless vertical scroll of dynamic content (chronological/algo).',
    slots: ['header', 'body'],
    layout: { fullWidthTop: ['header'], columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Feed Layout]
┌───────────────────────────────────────┐
│ [Header]                              │
├───────────────────────────────────────┤
│  ┌─────────────────────────────────┐  │
│  │ User Avatar · Time              │  │
│  │ Post content text goes here...  │  │
│  │ [Image Placeholder]             │  │
│  └─────────────────────────────────┘  │
│  ┌─────────────────────────────────┐  │
│  │ User Avatar · Time              │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘` },

  { name: 'split-screen', category: 'Screen & Core Page Skeletons', cli: 'split-screen',
    desc: '50/50 or fixed/fluid dual-panel layout (e.g., Map + List).',
    slots: ['left', 'right'],
    layout: { columns: [{ name: 'left', x: 0, w: 0.5 }, { name: 'right', x: 0.5, w: 0.5 }] },
    ascii: `
[Split-Screen Layout]
┌───────────────────┬───────────────────┐
│                   │                   │
│    Left Panel     │    Right Panel    │
│   (e.g., Map)     │   (e.g., List)    │
│                   │                   │
└───────────────────┴───────────────────┘` },

  { name: 'single-page-spa', category: 'Screen & Core Page Skeletons', cli: null,
    desc: 'One long-scrolling page with sticky anchor nav links.',
    slots: ['header', 'section-1', 'section-2'],
    layout: { fullWidthTop: ['header'], columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Single-Page Layout (SPA)]
┌───────────────────────────────────────┐
│ Logo   [Link1]  *[Link2]*  [Link3]    │
├───────────────────────────────────────┤
│ [Section 1: Hero Intro]               │
│                                       │
│ ~ ~ ~ ~ ~ ~ ~ Scroll ~ ~ ~ ~ ~ ~ ~ ~  │
│ *[Section 2: Features]*  <-- Viewport │
└───────────────────────────────────────┘` },

  { name: 'asymmetrical', category: 'Screen & Core Page Skeletons', cli: null,
    desc: 'Unbalanced grid elements to break monotony and guide focus.',
    slots: ['large', 'small-a', 'small-b'],
    layout: { columns: [{ name: 'large', x: 0, w: 0.55 }, { name: 'small', x: 0.55, w: 0.45 }] },
    ascii: `
[Asymmetrical Layout]
┌───────────────────────────────────────┐
│ [Header]                              │
├───────────────────┬───────────────────┤
│                   │  [Small Callout]  │
│    [Huge Bold     ├───────────────────┤
│     Headline]     │                   │
│                   │  [Image Box]      │
└───────────────────┴───────────────────┘` },

  { name: 'magazine-editorial', category: 'Screen & Core Page Skeletons', cli: null,
    desc: 'Multi-column, varied-size grids mimicking news print.',
    slots: ['main-story', 'side-story-1', 'side-story-2'],
    layout: { columns: [{ name: 'main-story', x: 0, w: 0.6 }, { name: 'sidebar', x: 0.6, w: 0.4 }] },
    ascii: `
[Magazine / Editorial Layout]
┌───────────────────────────────────────┐
│              MAIN LOGO                │
├───────────────────────────────────────┤
│ ┌───────────────────┐ ┌─────────────┐ │
│ │    BIG STORY      │ │ Side Story  │ │
│ │    HEADLINE       │ └─────────────┘ │
│ │                   │ ┌─────────────┐ │
│ │ [Large Image]     │ │ Side Story  │ │
│ └───────────────────┘ └─────────────┘ │
└───────────────────────────────────────┘` },

  { name: 'full-screen-media', category: 'Screen & Core Page Skeletons', cli: null,
    desc: 'Immersive background video/image with minimal overlay text.',
    slots: ['logo', 'menu', 'headline', 'cta'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Full-Screen Media Layout]
┌───────────────────────────────────────┐
│ [Logo]                       [Menu]   │
│                                       │
│        =======================        │
│        │ BACKGROUND VIDEO/IMG│        │
│        │  Centered Headline  │        │
│        │     [Button]        │        │
│        =======================        │
└───────────────────────────────────────┘` },

  { name: 'parallax', category: 'Screen & Core Page Skeletons', cli: null,
    desc: 'Multi-layered background/foreground scrolling at different speeds.',
    slots: ['layer-slow', 'layer-mid', 'layer-fast'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Parallax Layout]
┌───────────────────────────────────────┐
│ [Layer 3: Slow Foreground Stars]      │
│                                       │
│    [Layer 2: Midground Mountain]      │
│                                       │
│        [Layer 1: Fast Content Text]   │
└───────────────────────────────────────┘` },

  { name: 'infinite-canvas', category: 'Screen & Core Page Skeletons', cli: null,
    desc: 'Borderless 2D pan/zoom workspace (e.g., Miro, Figma).',
    slots: ['nodes', 'frames', 'viewport'],
    layout: { columns: [{ name: 'canvas', x: 0, w: 1.0 }] },
    ascii: `
[Infinite Canvas]
   - - - - - - - - - - - - - - - -
  │    [Node] ------> [Node]      │
  │      ^                        │
  │      |         ┌────────┐     │
  │    [Node]      │ Frame  │     │
   - - - - - - - - └────────┘ - -
  (Viewable area pans in any direction)` },

  { name: 'holy-grail', category: 'Screen & Core Page Skeletons', cli: 'holy-grail',
    desc: 'Header + footer + three columns: left nav, body, right aside.',
    slots: ['header', 'nav', 'body', 'aside', 'footer'],
    layout: { fullWidthTop: ['header'], fullWidthBottom: ['footer'],
              columns: [{ name: 'nav', x: 0, w: 0.25 }, { name: 'body', x: 0.25, w: 0.5 }, { name: 'aside', x: 0.75, w: 0.25 }] },
    ascii: `
[Holy Grail Layout]
┌───────────────────────────────────────┐
│                Header                 │
├───────────┬───────────────┬───────────┤
│  Left Nav │  Main Content │ Right Bar │
│           │               │           │
├───────────┴───────────────┴───────────┤
│                Footer                 │
└───────────────────────────────────────┘` },

  { name: 'card-based', category: 'Screen & Core Page Skeletons', cli: null,
    desc: 'Entire screen comprised of modular moveable masonry blocks.',
    slots: ['cards'],
    layout: { columns: [{ name: 'cards', x: 0, w: 1.0 }] },
    ascii: `
[Card-Based Layout]
┌───────────────────────────────────────┐
│ ┌───────────┐ ┌───────────┐ ┌───────┐ │
│ │ Card A    │ │ Card B    │ │ Card C│ │
│ └───────────┘ └───────────┘ └───────┘ │
│ ┌───────────┐ ┌───────────┐ ┌───────┐ │
│ │ Card D    │ │ Card E    │ │ Card F│ │
│ └───────────┘ └───────────┘ └───────┘ │
└───────────────────────────────────────┘` },

  // ── 2. Navigation & Navigation Housing ──────────────────────────────────

  { name: 'sidebar', category: 'Navigation & Navigation Housing', cli: 'sidebar',
    desc: 'Left/right fixed vertical panel beside a main workspace.',
    slots: ['panel', 'body'],
    layout: { columns: [{ name: 'panel', x: 0, w: 0.35 }, { name: 'body', x: 0.35, w: 0.65 }] },
    ascii: `
[Sidebar Layout]
┌───┬───────────────────────────────────┐
│ L │ [Header]                          │
│ o ├───────────────────────────────────┤
│ g │                                   │
│ o │                                   │
├───┤          Main Workspace           │
│ M │                                   │
│ e │                                   │
│ n │                                   │
│ u │                                   │
└───┴───────────────────────────────────┘` },

  { name: 'top-header', category: 'Navigation & Navigation Housing', cli: null,
    desc: 'Horizontal bar at the top of the viewport for core paths.',
    slots: ['logo', 'nav-links', 'profile', 'body'],
    layout: { fullWidthTop: ['header'], columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Top Header Layout]
┌───────────────────────────────────────┐
│ [Logo]  Link  Link  Link     [Profile]│
├───────────────────────────────────────┤
│                                       │
│             Page Content              │
│                                       │
└───────────────────────────────────────┘` },

  { name: 'bottom-bar', category: 'Navigation & Navigation Housing', cli: null,
    desc: 'Mobile-first sticky bottom navigation for thumb-reachability.',
    slots: ['body', 'nav-bar'],
    layout: { fullWidthBottom: ['nav-bar'], columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Bottom Bar Layout]
┌───────────────────────────────────────┐
│                                       │
│             Mobile Content            │
│                                       │
├───────────────────────────────────────┤
│  [Home]  [Search]  [Inbox]  [Profile] │
└───────────────────────────────────────┘` },

  { name: 'tabbed', category: 'Navigation & Navigation Housing', cli: null,
    desc: 'Inline tab headers used to switch views inside a wrapper.',
    slots: ['tab-bar', 'body'],
    layout: { fullWidthTop: ['tab-bar'], columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Tabbed Layout]
┌───────────────────────────────────────┐
│  [ Tab 1 ]  *[ Tab 2 ]*   [ Tab 3 ]  │
├───────────────────────────────────────┤
│ ┌───────────────────────────────────┐ │
│ │ Active Content for Tab 2          │ │
│ │                                   │ │
│ └───────────────────────────────────┘ │
└───────────────────────────────────────┘` },

  { name: 'mega-menu', category: 'Navigation & Navigation Housing', cli: null,
    desc: 'Massive multi-column dropdown panel exposed from main header.',
    slots: ['header', 'category-1', 'category-2', 'category-3'],
    layout: { fullWidthTop: ['header'],
              columns: [{ name: 'cat-1', x: 0, w: 0.33 }, { name: 'cat-2', x: 0.33, w: 0.34 }, { name: 'cat-3', x: 0.67, w: 0.33 }] },
    ascii: `
[Mega Menu Layout]
┌───────────────────────────────────────┐
│ [Logo]  *[Shop]*  About  Contact      │
├───────────────────────────────────────┤
│ │ Category 1 │ Category 2 │ Cat 3   │ │
│ │ - Item A   │ - Item X   │ - Ultra │ │
│ │ - Item B   │ - Item Y   │ - Mega  │ │
└───────────────────────────────────────┘` },

  { name: 'drawer-hamburger', category: 'Navigation & Navigation Housing', cli: null,
    desc: 'Off-screen overlay panel that slides into view when triggered.',
    slots: ['nav-links', 'dimmed-content'],
    layout: { columns: [{ name: 'drawer', x: 0, w: 0.3 }, { name: 'content', x: 0.3, w: 0.7 }] },
    ascii: `
[Drawer / Hamburger Layout]
┌───────┬───────────────────────────────┐
│ Menu  │                               │
│ Link1 │                               │
│ Link2 │         Dimmed Main           │
│ Link3 │           Content             │
│       │                               │
│ Close │                               │
└───────┴───────────────────────────────┘` },

  { name: 'breadcrumb', category: 'Navigation & Navigation Housing', cli: null,
    desc: 'Linear horizontal path tracking the user\'s location hierarchy.',
    slots: ['crumb-trail', 'body'],
    layout: { fullWidthTop: ['crumb-trail'], columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Breadcrumb Layout]
┌───────────────────────────────────────┐
│ Home > Settings > Security > Password │
├───────────────────────────────────────┤
│                                       │
│ [Input: Enter New Password]           │
└───────────────────────────────────────┘` },

  { name: 'fab-menu', category: 'Navigation & Navigation Housing', cli: null,
    desc: 'Circular floating trigger opening contextual action sub-menus.',
    slots: ['body', 'fab', 'fab-actions'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Floating Action Button (FAB) Menu]
┌───────────────────────────────────────┐
│                                       │
│                                ( O )  │
│                                ( O )  │
│                                [ X ]  │
└───────────────────────────────────────┘` },

  { name: 'rail-navigation', category: 'Navigation & Navigation Housing', cli: null,
    desc: 'Ultra-skinny vertical icon-only sidebar for high-density apps.',
    slots: ['rail', 'body'],
    layout: { columns: [{ name: 'rail', x: 0, w: 0.08 }, { name: 'body', x: 0.08, w: 0.92 }] },
    ascii: `
[Rail Navigation]
┌───┬───────────────────────────────────┐
│[*]│                                   │
│[*]│                                   │
│[*]│           Main Workspace          │
│[*]│                                   │
└───┴───────────────────────────────────┘` },

  { name: 'tree-navigation', category: 'Navigation & Navigation Housing', cli: null,
    desc: 'Collapsible nested list layout for deep file/concept directories.',
    slots: ['tree'],
    layout: { columns: [{ name: 'tree', x: 0, w: 1.0 }] },
    ascii: `
[Tree Navigation]
┌───────────────────────────────────────┐
│ [-] Documents                         │
│   |-- [+] Project A                   │
│   \`-- [-] Project B                   │
│         |-- budget.xls                │
│         \`-- notes.txt                 │
└───────────────────────────────────────┘` },

  // ── 3. Content & Data Organization ──────────────────────────────────────

  { name: 'grid', category: 'Content & Data Organization', cli: null,
    desc: 'Symmetrical rows and columns of uniform cards or asset previews.',
    slots: ['items'],
    layout: { columns: [{ name: 'items', x: 0, w: 1.0 }] },
    ascii: `
[Grid Layout]
┌───────────────┬───────────────┬───────┐
│ ┌───────────┐ │ ┌───────────┐ │ ┌───┐ │
│ │   Item    │ │ │   Item    │ │ │   │ │
│ └───────────┘ │ └───────────┘ │ └───┘ │
├───────────────┼───────────────┼───────┤
│ ┌───────────┐ │ ┌───────────┐ │ ┌───┐ │
│ │   Item    │ │ │   Item    │ │ │   │ │
│ └───────────┘ │ └───────────┘ │ └───┘ │
└───────────────┴───────────────┴───────┘` },

  { name: 'list', category: 'Content & Data Organization', cli: 'stack',
    desc: 'Single-column vertical stack ideal for scanning text-dense items.',
    slots: ['rows'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[List Layout]
┌───────────────────────────────────────┐
│ [Img]  Title Row - Subtitle Info      │
├───────────────────────────────────────┤
│ [Img]  Title Row - Subtitle Info      │
├───────────────────────────────────────┤
│ [Img]  Title Row - Subtitle Info      │
└───────────────────────────────────────┘` },

  { name: 'masonry', category: 'Content & Data Organization', cli: null,
    desc: 'Staggered-height columns fitting uneven content fluidly (Pinterest).',
    slots: ['col-1', 'col-2', 'col-3'],
    layout: { columns: [{ name: 'col-1', x: 0, w: 0.33 }, { name: 'col-2', x: 0.33, w: 0.34 }, { name: 'col-3', x: 0.67, w: 0.33 }] },
    ascii: `
[Masonry Layout]
┌────────────┬────────────┬────────────┐
│ ┌────────┐ │ ┌────────┐ │ ┌────────┐ │
│ │ Short  │ │ │ Tall   │ │ │ Medium │ │
│ └────────┘ │ │        │ │ └────────┘ │
│ ┌────────┐ │ │        │ │ ┌────────┐ │
│ │ Medium │ │ └────────┘ │ │ Short  │ │
│ └────────┘ │ ┌────────┐ │ └────────┘ │
└────────────┴────────────┴────────────┘` },

  { name: 'carousel-slider', category: 'Content & Data Organization', cli: null,
    desc: 'Linear horizontal row of elements scrolled via touch/arrows.',
    slots: ['prev', 'cards', 'next'],
    layout: { columns: [{ name: 'cards', x: 0, w: 1.0 }] },
    ascii: `
[Carousel / Slider Layout]
┌───────────────────────────────────────┐
│    ┌────────┐  ┌────────┐  ┌────────┐ │
│ <  │ Card 1 │  │ Card 2 │  │ Card 3 │>│
│    └────────┘  └────────┘  └────────┘ │
└───────────────────────────────────────┘` },

  { name: 'accordion', category: 'Content & Data Organization', cli: null,
    desc: 'Vertically stacked headers that expand to reveal content blocks.',
    slots: ['section-headers', 'expanded-content'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Accordion Layout]
┌───────────────────────────────────────┐
│ [+] Section Title One                 │
├───────────────────────────────────────┤
│ [-] Section Title Two                 │
│   Hidden details and paragraphs       │
│   expand smoothly right here.         │
├───────────────────────────────────────┤
│ [+] Section Title Three               │
└───────────────────────────────────────┘` },

  { name: 'timeline', category: 'Content & Data Organization', cli: null,
    desc: 'Central vertical/horizontal line tracking sequential events.',
    slots: ['events'],
    layout: { columns: [{ name: 'events', x: 0, w: 1.0 }] },
    ascii: `
[Timeline Layout]
┌───────────────────────────────────────┐
│ 2024 --(o)-- Project Kickoff Event    │
│          │                            │
│ 2025 --(o)-- Version 1.0 Launch Ready │
│          │                            │
│ 2026 --(o)-- Scale Infrastructure     │
└───────────────────────────────────────┘` },

  { name: 'kanban-board', category: 'Content & Data Organization', cli: null,
    desc: 'Vertical columns representing workflow status stages.',
    slots: ['todo', 'in-progress', 'done'],
    layout: { columns: [{ name: 'todo', x: 0, w: 0.33 }, { name: 'in-progress', x: 0.33, w: 0.34 }, { name: 'done', x: 0.67, w: 0.33 }] },
    ascii: `
[Kanban Board Layout]
┌───────────┬───────────┬───────────────┐
│ To Do     │ In Prog   │ Done          │
├───────────┼───────────┼───────────────┤
│ [Task 1]  │ [Task 3]  │ [Task 5]      │
│ [Task 2]  │           │ [Task 6]      │
└───────────┴───────────┴───────────────┘` },

  { name: 'comparison-matrix', category: 'Content & Data Organization', cli: null,
    desc: 'Side-by-side spec sheets/tables for product options.',
    slots: ['features', 'plan-columns'],
    layout: { columns: [{ name: 'features', x: 0, w: 0.35 }, { name: 'plan-a', x: 0.35, w: 0.325 }, { name: 'plan-b', x: 0.675, w: 0.325 }] },
    ascii: `
[Comparison Matrix Layout]
┌────────────┬────────────┬─────────────┐
│ Feature    │ Plan Basic │ Plan Pro    │
├────────────┼────────────┼─────────────┤
│ Storage    │ 10 GB      │ Unlimited   │
│ Support    │ Email      │ 24/7 Phone  │
└────────────┴────────────┴─────────────┘` },

  { name: 'f-pattern', category: 'Content & Data Organization', cli: null,
    desc: 'Content aligned to a top-heavy, left-to-right scanning habit.',
    slots: ['headline', 'subhead', 'list-items'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[F-Pattern Layout]
┌───────────────────────────────────────┐
│ [================= HEADLINE ========] │
│ [========= Subhead =====]             │
│ [=] Text                              │
│ [=] Text                              │
└───────────────────────────────────────┘` },

  { name: 'z-pattern', category: 'Content & Data Organization', cli: null,
    desc: 'Landing page elements placed along a diagonal zig-zag visual path.',
    slots: ['logo', 'top-right', 'value-prop', 'cta'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Z-Pattern Layout]
┌───────────────────────────────────────┐
│ [Logo]-------------------------[Login]│
│                             /         │
│                           /           │
│                         /             │
│                       /               │
│ [Big Value Prop]----------------[CTA] │
└───────────────────────────────────────┘` },

  { name: 'hero-banner', category: 'Content & Data Organization', cli: null,
    desc: 'High-impact top section with headline, graphic, and core CTA.',
    slots: ['headline', 'subtext', 'cta'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Hero Layout]
┌───────────────────────────────────────┐
│                                       │
│         WE BUILD THE FUTURE           │
│     Get started with us today.        │
│                                       │
│          [ Create Account ]           │
│                                       │
└───────────────────────────────────────┘` },

  { name: 'spreadsheet', category: 'Content & Data Organization', cli: null,
    desc: 'Infinite rows and columns of dense editable cells.',
    slots: ['column-headers', 'row-headers', 'cells'],
    layout: { columns: [{ name: 'row-headers', x: 0, w: 0.1 }, { name: 'cells', x: 0.1, w: 0.9 }] },
    ascii: `
[Matrix / Spreadsheet Layout]
┌───┬──────┬──────┬──────┬──────┬───────┐
│   │  A   │  B   │  C   │  D   │   E   │
├───┼──────┼──────┼──────┼──────┼───────┤
│ 1 │ Data │ Data │ Data │ Data │ Data  │
│ 2 │ Data │ Data │ Data │ Data │ Data  │
└───┴──────┴──────┴──────┴──────┴───────┘` },

  // ── 4. User Actions, Overlays & Component States ─────────────────────────

  { name: 'wizard-stepper', category: 'User Actions & Overlays', cli: null,
    desc: 'Linear multi-screen setup for complex sequential tasks.',
    slots: ['step-bar', 'body', 'back', 'continue'],
    layout: { fullWidthTop: ['step-bar'], columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Wizard / Stepper Layout]
┌───────────────────────────────────────┐
│ (1) Shipping -> *(2) Payment* -> (3) Review
├───────────────────────────────────────┤
│                                       │
│     [ Card Number Input         ]     │
│                                       │
│ [ Back ]                  [ Continue ]│
└───────────────────────────────────────┘` },

  { name: 'form', category: 'User Actions & Overlays', cli: 'form',
    desc: 'Clean single-column layout optimised for fast data entry.',
    slots: ['body'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Form Layout]
┌───────────────────────────────────────┐
│ First Name                            │
│ [===================================] │
│ Email Address                         │
│ [===================================] │
│ [ Submit ]                            │
└───────────────────────────────────────┘` },

  { name: 'search-filter', category: 'User Actions & Overlays', cli: null,
    desc: 'Search/Omnibox paired with a persistent filtering pane.',
    slots: ['search-bar', 'filters', 'results'],
    layout: { fullWidthTop: ['search-bar'], columns: [{ name: 'filters', x: 0, w: 0.3 }, { name: 'results', x: 0.3, w: 0.7 }] },
    ascii: `
[Search & Filter Layout]
┌───────────────────────────────────────┐
│ [ Search items...                 ]   │
├───────────┬───────────────────────────┤
│ Filters   │                           │
│ [ ] Cat A │     Search Results        │
│ [ ] Cat B │     Grid or List Area     │
└───────────┴───────────────────────────┘` },

  { name: 'modal-dialog', category: 'User Actions & Overlays', cli: 'modal',
    desc: 'Locked, centered modal window dimming out the backdrop.',
    slots: ['body'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }], rounded: true },
    ascii: `
[Modal / Dialog Layout]
┌───────────────────────────────────────┐
│ ╔════════ MODAL WINDOW ═════════════╗ │
│ ║                                   ║ │
│ ║   Are you sure you want to exit?  ║ │
│ ║                                   ║ │
│ ║   [ Cancel ]       [ Confirm ]    ║ │
│ ╚═══════════════════════════════════╝ │
└───────────────────────────────────────┘` },

  { name: 'flyout-panel', category: 'User Actions & Overlays', cli: 'flyout',
    desc: 'Contextual side-sheet sliding out over the main content.',
    slots: ['body', 'panel'],
    layout: { columns: [{ name: 'body', x: 0, w: 0.65 }, { name: 'panel', x: 0.65, w: 0.35 }] },
    ascii: `
[Detail View / Flyout Panel]
┌───────────────────────────────────┬───┐
│                                   │ D │
│                                   │ e │
│       Main App Grid View          │ t │
│       (Dimmed out)                │ a │
│                                   │ i │
│                                   │ l │
└───────────────────────────────────┴───┘` },

  { name: 'empty-state', category: 'User Actions & Overlays', cli: null,
    desc: 'Educational, graphic-rich layout shown when no data exists yet.',
    slots: ['icon', 'headline', 'subtext', 'cta'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Empty State Layout]
┌───────────────────────────────────────┐
│                                       │
│                (  !  )                │
│           No Messages Yet             │
│    Click the plus button below to     │
│         start a conversation.         │
│                                       │
│             [ + Start ]               │
└───────────────────────────────────────┘` },

  { name: 'tooltip-popover', category: 'User Actions & Overlays', cli: null,
    desc: 'Floating micro-box pointing directly to an interface element.',
    slots: ['trigger', 'tooltip-content'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Tooltip / Popover Layout]
┌───────────────────────────────────────┐
│               [Hover Me]              │
│                   /\\                  │
│           ┌────────┬────────┐         │
│           │ This edits your │         │
│           │ profile picture.│         │
│           └─────────────────┘         │
└───────────────────────────────────────┘` },

  { name: 'skeleton-loading', category: 'User Actions & Overlays', cli: null,
    desc: 'Wireframe-like shapes animating while actual data fetches.',
    slots: ['placeholder-rows'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Skeleton Loading Layout]
┌───────────────────────────────────────┐
│ [///]  //////////////////////////////  │
├───────────────────────────────────────┤
│ [///]  //////////                      │
├───────────────────────────────────────┤
│ [///]  /////////////////               │
└───────────────────────────────────────┘` },

  { name: 'toast-snackbar', category: 'User Actions & Overlays', cli: null,
    desc: 'Low-priority micro-banner floating momentarily at a screen edge.',
    slots: ['message', 'action'],
    layout: { fullWidthBottom: ['toast'], columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Toast / Snackbar Layout]
┌───────────────────────────────────────┐
│                                       │
│                                       │
│ ┌───────────────────────────────────┐ │
│ │ Item deleted permanently.  [Undo] │ │
│ └───────────────────────────────────┘ │
└───────────────────────────────────────┘` },

  { name: 'coachmarks-walkthrough', category: 'User Actions & Overlays', cli: null,
    desc: 'Guided overlay highlighting interface features sequentially.',
    slots: ['target-element', 'callout-text', 'step-nav'],
    layout: { columns: [{ name: 'body', x: 0, w: 1.0 }] },
    ascii: `
[Coachmarks / Walkthrough Layout]
┌───────────────────────────────────────┐
│ ┌────────┐  Step 1 of 3               │
│ │ BUTTON │<-- This tool exports       │
│ └────────┘    your analytics data.    │
│               [Next]                  │
└───────────────────────────────────────┘` },

]

// ─── Layout constants (mirrors drawio-ux.mjs) ────────────────────────────────

const SCREEN_W   = 420
const SCREEN_HDR = 32
const PAD        = 8
const CHROME_H   = 28
const SLOT_H     = 20 + 22 * 2 + 24 + 8   // list_hdr + 2 rows + verb + pad

// ─── Generators ───────────────────────────────────────────────────────────────

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function idSafe(s) {
  return s.replace(/[^a-z0-9]+/gi, '_').replace(/^_|_$/g, '')
}

function generateMd(t) {
  const cliLine = t.cli
    ? `**CLI template:** \`--layout ${t.cli}\``
    : `**CLI template:** *(reference only — not in drawio-ux)*`
  const slotsLine = `**Slots:** ${t.slots.map(s => `\`${s}\``).join(' · ')}`

  return `# ${t.name.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}

**Category:** ${t.category}
${cliLine}
${slotsLine}

${t.desc}

## ASCII template

\`\`\`
${t.ascii.replace(/^\n/, '')}
\`\`\`

## Fill guide

Replace each \`[slot-name]\` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use \`············\` dotted lines instead of solid \`---\`/\`|\`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: \`${t.name}.drawio\` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target \`.drawio\` file.
`
}

function generateDrawio(t) {
  const lay  = t.layout
  const sid  = `s_${idSafe(t.name)}_tmpl`
  const cw   = SCREEN_W - PAD * 2

  const topBands    = (lay.fullWidthTop    || []).length
  const bottomBands = (lay.fullWidthBottom || []).length
  const totalH = SCREEN_HDR + PAD + topBands * CHROME_H + SLOT_H + bottomBands * CHROME_H + PAD

  const isRounded = lay.rounded || t.cli === 'modal'
  const screenStyle = isRounded
    ? 'rounded=1;arcSize=4;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;strokeWidth=2;fontStyle=1;fontSize=13;verticalAlign=top;align=center;'
    : 'rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;strokeWidth=2;fontStyle=1;fontSize=13;verticalAlign=top;align=center;'
  const slotStyle = 'whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=1;fontStyle=1;fontSize=11;verticalAlign=middle;align=center;'
  const bandStyle = 'whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=1;fontStyle=2;fontSize=11;verticalAlign=middle;align=center;'

  const cells = []

  cells.push(
    `    <mxCell id="${sid}" value="${esc(t.name)}" style="${screenStyle}" vertex="1" parent="1">\n` +
    `      <mxGeometry x="50" y="50" width="${SCREEN_W}" height="${totalH}" as="geometry" />\n` +
    `    </mxCell>`
  )

  let ry = SCREEN_HDR + PAD

  for (const band of (lay.fullWidthTop || [])) {
    const bid = `${sid}_${idSafe(band)}`
    cells.push(
      `    <mxCell id="${bid}" value="[${band}]" style="${bandStyle}" vertex="1" parent="${sid}">\n` +
      `      <mxGeometry x="${PAD}" y="${ry}" width="${cw}" height="${CHROME_H}" as="geometry" />\n` +
      `    </mxCell>`
    )
    ry += CHROME_H
  }

  for (const col of lay.columns) {
    const cx  = PAD + Math.round(col.x * cw)
    const colw = Math.round(col.w * cw)
    const cid = `${sid}_${idSafe(col.name)}`
    cells.push(
      `    <mxCell id="${cid}" value="[${col.name}]" style="${slotStyle}" vertex="1" parent="${sid}">\n` +
      `      <mxGeometry x="${cx}" y="${ry}" width="${colw}" height="${SLOT_H}" as="geometry" />\n` +
      `    </mxCell>`
    )
  }
  ry += SLOT_H

  for (const band of (lay.fullWidthBottom || [])) {
    const bid = `${sid}_${idSafe(band)}`
    cells.push(
      `    <mxCell id="${bid}" value="[${band}]" style="${bandStyle}" vertex="1" parent="${sid}">\n` +
      `      <mxGeometry x="${PAD}" y="${ry}" width="${cw}" height="${CHROME_H}" as="geometry" />\n` +
      `    </mxCell>`
    )
    ry += CHROME_H
  }

  return `<?xml version="1.0" encoding="UTF-8"?>
<!-- Template fragment: ${t.name}
     Category: ${t.category}
     Slots: ${t.slots.join(', ')}
     CLI: ${t.cli ? '--layout ' + t.cli : 'n/a'}

     Usage:
       1. Open this file in draw.io to preview the slot layout.
       2. Copy the <mxCell> elements into your target .drawio file (Edit > XML).
       3. Replace each [slot-name] placeholder cell with real region cells
          (list rows, form field rows, verb rows — see companion .md).
       4. Adjust x="50" y="50" on the screen cell to reposition on the canvas.
       5. Rename all IDs: replace "_tmpl" with "_<yourscreenname>"
          to avoid ID collisions in the target file.
-->
<mxfile host="Electron" version="29.0.3">
  <diagram id="${t.name}-template" name="${t.name}">
    <mxGraphModel dx="800" dy="400" grid="0" gridSize="10" guides="1" tooltips="1"
      connect="1" arrows="1" fold="1" page="1" pageScale="1"
      pageWidth="1200" pageHeight="900" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
${cells.join('\n')}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
`
}

// ─── Write all files ──────────────────────────────────────────────────────────

mkdirSync(OUT_DIR, { recursive: true })

for (const t of TEMPLATES) {
  writeFileSync(resolve(OUT_DIR, `${t.name}.md`),     generateMd(t),     'utf8')
  writeFileSync(resolve(OUT_DIR, `${t.name}.drawio`), generateDrawio(t), 'utf8')
  console.log(`  ${t.name}`)
}

console.log(`\ndone — ${TEMPLATES.length} templates × 2 files = ${TEMPLATES.length * 2} files`)
console.log(`output: ${OUT_DIR}`)
