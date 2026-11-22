// The Story UI editor's views: the story map as epics, sub-epics, stories and scenarios, edited in place. The views
// draw the nodes the map makes from what the Python story model sends (StoryMapClient over the generated StoryMap
// client, story-map-nodes.ts), and each card edits through its own node, which saves it through that node's own tool;
// nothing here holds a story map of its own.

import React, { Component, useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore, type ErrorInfo, type ReactNode } from 'react';
import { ChatClientGenerated } from '@cdd/harness/chat/chat';
import { useStoryMap } from '@cdd/practices/stories/model/story-map-views';

import { StoryMapApi } from './story-map-api';
import { StoryMapClient } from './story-map-client';
import type { StoryMapFailures } from './story-map-failures';
import {
  STEP_KEYWORDS,
  type Answer,
  type EpicOnPage,
  type IncrementOnPage,
  type ScenarioOnPage,
  type StepKeyword,
  type StepOnPage,
  type StoryOnPage,
  type StoryNodeOnPage,
} from './story-map-nodes';

// The page reads its map again this often, so an edit the agent made through the tools shows without a reload, and a
// page following the open session shows the ticket activated last.
const READ_EVERY_MILLISECONDS = 2_000;

type EditStatus = 'synced' | 'saving' | 'error';

// An edit a view makes: a call on a node, or on the map, that answers the map as its file now holds it.
type Change = () => Answer;
// What a view hands every edit to: the page's edit, which shows it saving and says why one failed.
type Edit = (change: Change) => void;

// What a page's reads and edits share, made once for its failures: the calls it makes, where their failures go, and
// whether an edit is under way.
interface StoryMapPageCalls {
  api: StoryMapApi;
  failures: StoryMapFailures;
  editing: React.MutableRefObject<boolean>;
}

// The map the page shows, read when the page opens and again every READ_EVERY_MILLISECONDS, except while an edit is
// under way. A read of the file already shown is taken on by the client the views hold.
function useStoryMapReading(file: string | null, calls: StoryMapPageCalls) {
  const [client, setClient] = useState<StoryMapClient | null>(null);
  useEffect(() => {
    const { api, failures, editing } = calls;
    let stopped = false;
    let held: StoryMapClient | null = null;
    const read = async () => {
      if (editing.current) return;
      const next = file ? await (held ?? new StoryMapClient(api, null, file)).show() : await StoryMapClient.inOpenSession(api);
      if (stopped || !next) return;
      if (held && held.file === next.file) return void (next !== held && held.takeOn(next));
      held = next;
      setClient(next);
    };
    const readReporting = (context: string) => read().catch((thrown: unknown) => failures.failWith(thrown, context));
    void readReporting('Opening the story map in the Story UI');
    const timer = setInterval(() => void readReporting('Reading the story map again every two seconds'), READ_EVERY_MILLISECONDS);
    return () => { stopped = true; clearInterval(timer); };
  }, [calls, file]);
  return client;
}

// An edit answers the map as its file now holds it; one that fails leaves the map as it was and says why.
function useStoryMapEdit(client: StoryMapClient | null, calls: StoryMapPageCalls) {
  const [status, setStatus] = useState<EditStatus>('synced');
  const edit = useCallback(async (change: Change) => {
    if (!client) return;
    const { failures, editing } = calls;
    editing.current = true;
    setStatus('saving');
    try {
      const answered = await change();
      setStatus(answered ? 'synced' : 'error');
    } catch (thrown) {
      setStatus('error');
      failures.failWith(thrown, 'An edit in the Story UI');
    } finally {
      editing.current = false;
    }
  }, [client, calls]);
  return { status, edit };
}

// The story map a page shows: the file its link names, else the story map of the session open in the project. Every
// failure, from a call, a read or an edit, goes through failures.fail: shown on the page and sent to the opening chat.
export function useStoryMapPage(file: string | null, failures: StoryMapFailures) {
  const failure = useSyncExternalStore(failures.subscribe, () => failures.shown);
  const editing = useRef(false);
  const calls = useMemo<StoryMapPageCalls>(() => ({ api: new StoryMapApi(failures.fail), failures, editing }), [failures]);
  const { api } = calls;
  const client = useStoryMapReading(file, calls);
  const { status, edit } = useStoryMapEdit(client, calls);

  // A story's acceptance-test file is read in the chat bar's file viewer of the chat this page was opened beside, never
  // here: the chat takes it at its next check-in.
  const showInChat = useCallback((path: string) => {
    ChatClientGenerated.named(api, failures.chat).send('open_file', path)
      .catch((thrown: unknown) => failures.failWith(thrown, `Showing ${path} in the chat from the Story UI`));
  }, [api, failures]);

  return { client, failure, status, edit, showInChat, dismissFailure: () => failures.dismiss() };
}

// Which nodes the person has opened, by id.
function useExpandedNodes() {
  const [expandedNodeIds, setExpandedNodeIds] = useState<ReadonlySet<string>>(new Set());
  const expandNode = useCallback((nodeId: string) => setExpandedNodeIds((shown) => new Set([...shown, nodeId])), []);
  const collapseNode = useCallback((nodeId: string) => {
    setExpandedNodeIds((shown) => new Set([...shown].filter((each) => each !== nodeId)));
  }, []);
  const expandDescendants = useCallback((nodeId: string, descendantIds: string[]) => {
    setExpandedNodeIds((shown) => new Set([...shown, nodeId, ...descendantIds]));
  }, []);
  const collapseAll = useCallback(() => setExpandedNodeIds(new Set()), []);
  return { expandedNodeIds, expandNode, collapseNode, expandDescendants, collapseAll };
}

// How the person is looking at the map: the map or its increments, with or without scenarios, scoped to the ticket or
// whole, and which nodes are open.
export function useStoryMapViewState() {
  const [viewMode, setViewMode] = useState<'map' | 'increment'>('map');
  const [showScenarios, setShowScenarios] = useState(false);
  // A map opened on a ticket shows the part its session covers until the person asks for the whole map.
  const [scoped, setScoped] = useState(true);
  const toggleViewMode = useCallback(() => setViewMode((mode) => (mode === 'map' ? 'increment' : 'map')), []);
  return {
    viewMode,
    showScenarios,
    scoped,
    toggleViewMode,
    toggleShowScenarios: () => setShowScenarios((shown) => !shown),
    toggleScoped: () => setScoped((isScoped) => !isScoped),
    ...useExpandedNodes(),
  };
}

// ---------------------------------------------------------------------------
// Drag-to-reorder — shared, dependency-free HTML5 DnD wiring.
// A single ref per rendering scope tracks the dragged node id; makeDragHandlers
// is a plain function (not a hook) so it is safe to call from inside .map().
// ---------------------------------------------------------------------------

function reorderIds(ids: string[], draggedId: string, dropTargetId: string): string[] {
  if (draggedId === dropTargetId || !ids.includes(draggedId) || !ids.includes(dropTargetId)) return ids;
  const next = ids.filter((id) => id !== draggedId);
  next.splice(next.indexOf(dropTargetId), 0, draggedId);
  return next;
}

function makeDragHandlers(
  dragRef: { current: string | null },
  id: string,
  getIds: () => string[],
  onReorder: (ids: string[]) => void,
) {
  return {
    draggable: true,
    onDragStart: (e: React.DragEvent<Element>) => {
      dragRef.current = id;
      try {
        e.dataTransfer?.setData('text/plain', id);
      } catch {
        /* jsdom in tests may not implement a full DataTransfer — ref fallback covers it */
      }
    },
    onDragOver: (e: React.DragEvent<Element>) => {
      e.preventDefault();
    },
    onDrop: (e: React.DragEvent<Element>) => {
      e.preventDefault();
      const draggedId = dragRef.current ?? e.dataTransfer?.getData('text/plain') ?? null;
      dragRef.current = null;
      if (!draggedId) return;
      onReorder(reorderIds(getIds(), draggedId, id));
    },
  };
}

// ---------------------------------------------------------------------------
// Cross-parent drag — Story cards and SubEpic lanes accept drops from a sibling
// under a DIFFERENT parent (any SubEpic under any Epic; any Epic), in addition to
// same-parent reorder. Instead of a floating mouse-following ghost, the dragged
// card/lane itself is rendered in place at its would-land position — grayed out
// and dashed — while every sibling reflows around it exactly as if the drop had
// already happened (see computeDisplayIds/computeColumnLayout below). Nothing is
// actually persisted until the drop completes.
// ---------------------------------------------------------------------------

interface DropEdge { listKey: string; beforeId: string | null; }

/** Epic/SubEpic/Story share one dragRef (for cross-parent drops) — this tags which
 *  level is actually being dragged so a zone for one level (e.g. a SubEpic lane)
 *  never reacts to a drag of another level (e.g. a Story) passing over it. */
type DragKind = 'epic' | 'sub-epic' | 'story';

/** The node currently being dragged, and the list it started out in (its `listKey` —
 *  a SubEpic id for a Story, an Epic id for a SubEpic, or EPIC_LIST_KEY for an Epic). */
interface DragState { kind: DragKind; id: string; originListKey: string; }

/** One list a drag can reorder or land in: its key, and the kind of node it holds. */
interface DragList { listKey: string; kind: DragKind; }

/** What a drag under way shows: the node dragged and the edge it would land on. */
type DragPreview = { dragState: DragState | null; dropEdge: DropEdge | null };

/** Shared top-level "list key" for Epics — Epics have only one list (there's no parent
 *  to move between), so every Epic-kind drag/drop always targets this same key. */
const EPIC_LIST_KEY = '__epics__';

/** Imperative controls shared by every cross-parent-aware drag handler in one render pass. */
interface DragVisualControls {
  start: (kind: DragKind, id: string, originListKey: string) => void;
  end: () => void;
  setEdge: (listKey: string, beforeId: string | null) => void;
  /** Drop the landing preview without ending the drag — used when the cursor is over a
   *  target that can't accept the current kind, so the container shows the not-allowed
   *  cursor (dropEffect none) instead of a stale "move" from the last valid hover. */
  clearEdge: () => void;
  dragState: DragState | null;
  dropEdge: DropEdge | null;
  /** Synchronously-updated mirror of `dropEdge` for reading inside native drag event
   *  handlers, where the render-closure `dropEdge` can lag a frame behind the latest
   *  setEdge/clearEdge call. The container `onDrop` commits from this. */
  dropEdgeRef: { current: DropEdge | null };
}

/** Native HTML5 drag renders its own screenshot-style ghost of the dragged element;
 *  since the in-place placeholder card already gives full drop-position feedback,
 *  suppress the native one with a blank image so the two don't visibly stack. */
let emptyDragImage: HTMLImageElement | null = null;
function suppressNativeDragImage(dragStart: React.DragEvent<Element>) {
  try {
    if (!emptyDragImage) {
      emptyDragImage = new Image();
      emptyDragImage.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBTAA7';
    }
    dragStart.dataTransfer?.setDragImage(emptyDragImage, 0, 0);
  } catch { /* jsdom / unsupported browsers just keep the native ghost */ }
}

// The drag starts on the next task on purpose: restyling the drag SOURCE from inside its
// own dragstart handler (here `.being-dragged`, which also sets pointer-events:none)
// makes Chrome abort the native drag outright — no dragover, no drop, nothing moves.
// Synthetic dispatchEvent-driven tests never hit this, only a real mouse does.
function startDragOnNextTask(
  setDragState: (state: DragState) => void,
  dropEdgeRef: { current: DropEdge | null },
  writeEdge: (next: DropEdge | null) => void,
): DragVisualControls['start'] {
  return (kind, id, originListKey) => {
    setTimeout(() => {
      setDragState({ kind, id, originListKey });
      // Only seeds the "in place" edge — a dragover that already landed keeps its edge.
      if (dropEdgeRef.current === null) writeEdge({ listKey: originListKey, beforeId: id });
    }, 0);
  };
}

function useDragVisuals(): DragVisualControls {
  const [dragState, setDragState] = useState<DragState | null>(null);
  const [dropEdge, setDropEdge] = useState<DropEdge | null>(null);
  const dropEdgeRef = useRef<DropEdge | null>(null);
  const writeEdge = (next: DropEdge | null) => { dropEdgeRef.current = next; setDropEdge(next); };
  return {
    start: startDragOnNextTask(setDragState, dropEdgeRef, writeEdge),
    end: () => { setDragState(null); writeEdge(null); },
    setEdge: (listKey, beforeId) => {
      const shown = dropEdgeRef.current;
      if (shown?.listKey === listKey && shown?.beforeId === beforeId) return;
      writeEdge({ listKey, beforeId });
    },
    clearEdge: () => { if (dropEdgeRef.current !== null) writeEdge(null); },
    dragState,
    dropEdge,
    dropEdgeRef,
  };
}

/** Real midpoint check in browsers; falls back to "insert before" under jsdom
 *  (zero-size rect), preserving existing same-parent reorder test behavior. */
function computeBeforeId(dragOver: React.DragEvent<Element>, ids: string[], targetId: string): string | null {
  const rect = (dragOver.currentTarget as Element).getBoundingClientRect();
  const before = rect.width === 0 || dragOver.clientX < rect.left + rect.width / 2;
  return before ? targetId : (ids[ids.indexOf(targetId) + 1] ?? null);
}

function insertBeforeId(ids: string[], draggedId: string, beforeId: string | null): string[] {
  const next = ids.filter((i) => i !== draggedId);
  if (beforeId === null) { next.push(draggedId); return next; }
  const idx = next.indexOf(beforeId);
  next.splice(idx === -1 ? next.length : idx, 0, draggedId);
  return next;
}

/** The live "as if you'd already dropped it here" order for one list (a SubEpic's
 *  Stories, an Epic's SubEpics, or the top-level Epics). `listKey` identifies which
 *  list this is; `realIds` is that list's actual (unchanged) order. Any other list
 *  this dragged node used to belong to loses it from its preview order (isOrigin),
 *  and whichever list is the current drop target gains it, inserted at the precise
 *  edge (isTarget) — so exactly one list ever shows the dragged id at a time. */
function computeDisplayIds(realIds: string[], list: DragList, preview: DragPreview): string[] {
  const { dragState, dropEdge } = preview;
  if (!dragState || dragState.kind !== list.kind) return realIds;
  if (dropEdge?.listKey === list.listKey) {
    return insertBeforeId(realIds.filter((id) => id !== dragState.id), dragState.id, dropEdge.beforeId);
  }
  if (dragState.originListKey === list.listKey && dropEdge) {
    return realIds.filter((id) => id !== dragState.id);
  }
  return realIds;
}

/** True while `nodeId` is the node currently being dragged — the dashed/grayed "landing
 *  here" styling hook (see .being-dragged in workspace.css). */
function isBeingDragged(dragState: DragState | null, kind: DragKind, nodeId: string): boolean {
  return dragState?.kind === kind && dragState.id === nodeId;
}

function dragStartedOnInteractiveControl(target: EventTarget | null): boolean {
  const node = target as Node | null;
  if (!node) return false;
  const el = node instanceof Element ? node : node.parentElement;
  return !!el?.closest('input, textarea, select, button, a, [role="button"]');
}

/** Inline-edit name fields cover nearly the whole surface of a draggable card/lane
 *  (Epic, SubEpic, Story, Increment). A mousedown inside a text input starts caret
 *  placement / text selection, which suppresses the draggable ancestor's HTML5 drag —
 *  so the card looks undraggable everywhere except its tiny ⠿ handle. The fields are
 *  therefore pointer-transparent until focused (see .node-label / .story-name-input /
 *  .increment-name-input in workspace.css); this hands the pointer back on double-click
 *  so the whole card stays a drag source while the name is still editable in place. */
function focusNameFieldOnDoubleClick(doubleClick: React.MouseEvent<Element>) {
  const field = doubleClick.currentTarget.querySelector<HTMLElement>('.node-label, .story-name-input, .increment-name-input');
  if (!field) return;
  field.focus();
  selectWholeName(field);
}

/** An epic's and an increment's name is an input, which selects its own text; a story's name is a content-editable
 *  div, which has no select(), so its text is selected through the document's selection. */
function selectWholeName(field: HTMLElement) {
  if (field instanceof HTMLInputElement) {
    field.select();
    return;
  }
  const whole = document.createRange();
  whole.selectNodeContents(field);
  window.getSelection()?.removeAllRanges();
  window.getSelection()?.addRange(whole);
}

/** Drag handlers for one Story card. `getTargetIds` returns the current Story ids of
 *  the SubEpic this card lives in — dropping here always calls onMove against that
 *  SubEpic, so the same handler covers same-parent reorder and moving in from a
 *  different SubEpic (even one under a different Epic). */
function makeStoryDragHandlers(
  dragRef: { current: string | null },
  dragKindRef: { current: DragKind | null },
  storyId: string,
  subEpicId: string,
  getTargetIds: () => string[],
  onMove: (storyId: string, targetSubEpicId: string, storyOrders: string[]) => void,
  visuals: DragVisualControls,
) {
  return {
    draggable: true,
    onDragStart: (e: React.DragEvent<Element>) => {
      if (dragStartedOnInteractiveControl(e.target)) {
        e.preventDefault();
        return;
      }
      dragRef.current = storyId;
      dragKindRef.current = 'story';
      try { e.dataTransfer?.setData('text/plain', storyId); } catch { /* jsdom fallback */ }
      suppressNativeDragImage(e);
      visuals.start('story', storyId, subEpicId);
    },
    onDragOver: (e: React.DragEvent<Element>) => {
      e.preventDefault(); // always suppress native drop behavior (e.g. text pasted into a nearby input)
      if (dragKindRef.current !== 'story') { // Stories only ever accept other Stories
        if (e.dataTransfer) e.dataTransfer.dropEffect = 'none'; // honest not-allowed cursor for the mismatched kind
        visuals.clearEdge(); // wrong row → drop the preview so the container also reads "not allowed"
        return;
      }
      if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
      // Hovering the dragged card's own (now-relocated) placeholder: its rect sits wherever
      // the previous edge put it, so recomputing here would flip-flop before/after itself
      // every frame (the ghost preview flickering as the edge value bounces) — keep the edge.
      if (dragRef.current === storyId) return;
      visuals.setEdge(subEpicId, computeBeforeId(e, getTargetIds(), storyId));
    },
    // Commit + cleanup handled once at the container level (see containerDragHandlers)
    // via onDrop / onDragEnd. dragEnd bubbles to the container from the drag source, so
    // the container sees it regardless of which reflowed fragment is under the cursor.
    onDragEnd: () => {},
  };
}

/** Drag handlers for one SubEpic lane — moves the SubEpic, and every Story nested
 *  inside it, to the target Epic (or reorders it within the same Epic). */
function makeSubEpicDragHandlers(
  dragRef: { current: string | null },
  dragKindRef: { current: DragKind | null },
  subEpicId: string,
  epicId: string,
  getTargetIds: () => string[],
  onMove: (subEpicId: string, targetEpicId: string, subEpicOrders: string[]) => void,
  visuals: DragVisualControls,
) {
  return {
    draggable: true,
    onDragStart: (e: React.DragEvent<Element>) => {
      if (dragStartedOnInteractiveControl(e.target)) {
        e.preventDefault();
        return;
      }
      dragRef.current = subEpicId;
      dragKindRef.current = 'sub-epic';
      try { e.dataTransfer?.setData('text/plain', subEpicId); } catch { /* jsdom fallback */ }
      suppressNativeDragImage(e);
      visuals.start('sub-epic', subEpicId, epicId);
    },
    onDragOver: (e: React.DragEvent<Element>) => {
      e.preventDefault(); // always suppress native drop behavior (e.g. text pasted into a nearby input)
      if (dragKindRef.current !== 'sub-epic') { // a Story hovering a SubEpic's title bar is not a valid drop — Stories can't live at that level
        if (e.dataTransfer) e.dataTransfer.dropEffect = 'none'; // honest not-allowed cursor for the mismatched kind
        visuals.clearEdge();
        return;
      }
      if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
      // Hovering the dragged lane's own (now-relocated) placeholder — see the matching
      // guard in makeStoryDragHandlers for why recomputing here would flicker the ghost.
      if (dragRef.current === subEpicId) return;
      visuals.setEdge(epicId, computeBeforeId(e, getTargetIds(), subEpicId));
    },
    // Commit + cleanup handled at the container level; do not clear refs/edge here.
    onDragEnd: () => {},
  };
}

/** Drag handlers for one Epic lane — flat top-level reorder only (Epics have no parent
 *  to move between), but still shares dragRef/dragKindRef so an Epic drag never gets
 *  misread as a SubEpic/Story drop elsewhere, and gets the same in-place placeholder
 *  + sibling-reflow treatment via EPIC_LIST_KEY. */
function makeEpicDragHandlers(
  dragRef: { current: string | null },
  dragKindRef: { current: DragKind | null },
  epicId: string,
  getIds: () => string[],
  onReorder: (ids: string[]) => void,
  visuals: DragVisualControls,
) {
  return {
    draggable: true,
    onDragStart: (e: React.DragEvent<Element>) => {
      if (dragStartedOnInteractiveControl(e.target)) {
        e.preventDefault();
        return;
      }
      dragRef.current = epicId;
      dragKindRef.current = 'epic';
      try { e.dataTransfer?.setData('text/plain', epicId); } catch { /* jsdom fallback */ }
      suppressNativeDragImage(e);
      visuals.start('epic', epicId, EPIC_LIST_KEY);
    },
    onDragOver: (e: React.DragEvent<Element>) => {
      e.preventDefault(); // always suppress native drop behavior (e.g. text pasted into a nearby input)
      if (dragKindRef.current !== 'epic') {
        if (e.dataTransfer) e.dataTransfer.dropEffect = 'none'; // honest not-allowed cursor for the mismatched kind
        visuals.clearEdge();
        return;
      }
      if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
      // Hovering the dragged lane's own (now-relocated) placeholder \u2014 see the matching
      // guard in makeStoryDragHandlers for why recomputing here would flicker the ghost.
      if (dragRef.current === epicId) return;
      visuals.setEdge(EPIC_LIST_KEY, computeBeforeId(e, getIds(), epicId));
    },
    // Commit + cleanup handled at the container level; do not clear refs/edge here.
    onDragEnd: () => {},
  };
}

/** Drop-only zone for an EMPTY SubEpic/Epic — there is no sibling card to drop onto,
 *  so the "+"-button placeholder itself accepts the drop and appends at the end. */
function makeEmptyParentDropZone(
  dragRef: { current: string | null },
  dragKindRef: { current: DragKind | null },
  expectedKind: DragKind,
  targetParentId: string,
  onMove: (draggedId: string, targetParentId: string, orders: string[]) => void,
  visuals: DragVisualControls,
) {
  return {
    onDragOver: (e: React.DragEvent<Element>) => {
      e.preventDefault(); // always suppress native drop behavior (e.g. text pasted into a nearby input)
      if (dragKindRef.current !== expectedKind) {
        if (e.dataTransfer) e.dataTransfer.dropEffect = 'none'; // honest not-allowed cursor for the mismatched kind
        visuals.clearEdge();
        return;
      }
      if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
      visuals.setEdge(targetParentId, null);
    },
    // Commit handled once at the container level (see containerDragHandlers); the
    // dragover above records this empty parent as the drop edge (beforeId: null → append).
  };
}

/** True while `listKey` is the active cross-parent drop scope — highlights the lane/column. */
function isDropScopeActive(dropEdge: DropEdge | null, listKey: string): boolean {
  return dropEdge?.listKey === listKey;
}

/** Classnames for the specific card that is the current "insert before" target. */
function dropIndicatorClass(dropEdge: DropEdge | null, listKey: string, nodeId: string): string {
  return dropEdge?.listKey === listKey && dropEdge.beforeId === nodeId ? ' drop-indicator' : '';
}

// ---------------------------------------------------------------------------
// Column layout — every row (Epic / SubEpic / Spine / Increment) shares one
// grid-column template so a Story's card sits in the same horizontal slot in
// every row it can appear in (spine or any increment), and SubEpic/Epic lanes
// span exactly the accumulated width of their leaf Story columns.
// SubEpicModel has no nested sub_epics — all SubEpics under one Epic render
// in a single row, side by side (not staggered into two rows).
// ---------------------------------------------------------------------------

interface ColumnLayout {
  epicCols: Map<string, { start: number; span: number }>;
  subEpicCols: Map<string, { start: number; span: number }>;
  storyCol: Map<string, number>;
  totalCols: number;
}

// Card-width columns an empty SubEpic or Epic reserves: a single column is too narrow to
// read its name alongside its drag handle + icon buttons.
const EMPTY_PARENT_COLUMNS = 2;

/** Lays out the map's columns left to right as the drag under way would leave them: each Story one column, each
 *  SubEpic and Epic spanning the columns of its Stories. */
class ColumnLayoutBuilder {
  // every column is card-width
  private readonly layout: ColumnLayout = { epicCols: new Map(), subEpicCols: new Map(), storyCol: new Map(), totalCols: 1 };
  private col = 1;

  constructor(private readonly epics: EpicOnPage[], private readonly preview: DragPreview) {}

  laidOut(): ColumnLayout {
    const epicIds = computeDisplayIds(this.epics.map((e) => e.id), { listKey: EPIC_LIST_KEY, kind: 'epic' }, this.preview);
    for (const epicId of epicIds) this.layOutEpic(this.epics.find((e) => e.id === epicId)!);
    return { ...this.layout, totalCols: Math.max(1, this.col - 1) };
  }

  private layOutEpic(epic: EpicOnPage): void {
    const epicStart = this.col;
    const subEpicsById = new Map(this.epics.flatMap((e) => e.subEpics.map((s) => [s.id, s] as const)));
    const displaySubIds = computeDisplayIds(epic.subEpics.map((s) => s.id), { listKey: epic.id, kind: 'sub-epic' }, this.preview);
    for (const subId of displaySubIds) this.layOutSubEpic(subEpicsById.get(subId)!);
    if (displaySubIds.length === 0) this.col += EMPTY_PARENT_COLUMNS;
    this.layout.epicCols.set(epic.id, { start: epicStart, span: this.col - epicStart });
  }

  private layOutSubEpic(sub: EpicOnPage): void {
    const subStart = this.col;
    const displayStoryIds = computeDisplayIds(sub.stories.map((s) => s.id), { listKey: sub.id, kind: 'story' }, this.preview);
    if (displayStoryIds.length === 0) this.col += EMPTY_PARENT_COLUMNS;
    displayStoryIds.forEach((sid) => { this.layout.storyCol.set(sid, this.col); this.col += 1; });
    this.layout.subEpicCols.set(sub.id, { start: subStart, span: this.col - subStart });
  }
}

function computeColumnLayout(epics: EpicOnPage[], preview: DragPreview): ColumnLayout {
  return new ColumnLayoutBuilder(epics, preview).laidOut();
}

function colTemplate(totalCols: number): string {
  // Keep columns text-fit while allowing expansion states to grow the track when needed.
  return Array.from({ length: totalCols }, () => 'minmax(max-content, auto)').join(' ');
}

// ---------------------------------------------------------------------------
// StoryHierarchyView — Epic → SubEpic row → Spine + Increment rows
// ---------------------------------------------------------------------------

interface StoryHierarchyViewProps {
  // The map, whose increments the view draws and which adds and reorders epics and increments.
  map: StoryMapClient;
  // The epics the view draws: every epic, or the part a ticket's scope covers.
  epics: EpicOnPage[];
  expandedNodeIds: ReadonlySet<string>;
  showScenarios: boolean;
  /** false = Map View (no increment rows, no assign combobox); true = Increment View */
  showIncrements?: boolean;
  onNodeClick: (id: string) => void;
  onExpand: (id: string, descendantIds: string[]) => void;
  // Every edit goes here, each a call on the node a card shows.
  edit: Edit;
  // Opens an acceptance-test file in the chat bar's file viewer; none when no chat opened the page.
  onOpenFile?: (path: string) => void;
}

// The new name a person typed for a node, else the name a new node of its kind takes.
const named = (typed: string | undefined, otherwise: string): string => typed?.trim() || otherwise;

export function StoryHierarchyView({
  map,
  epics,
  expandedNodeIds,
  showScenarios,
  showIncrements = true,
  onNodeClick,
  onExpand,
  edit,
  onOpenFile,
}: StoryHierarchyViewProps) {
  const increments = map.incrementsOnPage;
  // The stories a drop names by id, among those the view draws.
  const storiesById = new Map(epics.flatMap((epic) => epic.storiesShown).map((story) => [story.id, story]));
  const dragRef = useRef<string | null>(null);
  const dragKindRef = useRef<DragKind | null>(null);
  /** True while the cursor is currently over a VALID drop target for the active drag —
   *  the signal the container onDragEnd uses to decide commit vs. cancel (see below). */
  const dragLandedValidRef = useRef(false);
  const incDragRef = useRef<string | null>(null);
  /** Tracks which story is being dragged for cross-row increment assignment. */
  const storyDragRef = useRef<string | null>(null);
  /** Which Increment (label + cards band together) is the current drop target —
   *  shared so the two grid rows highlight as one zone instead of flickering independently. */
  const [dragOverIncrementId, setDragOverIncrementId] = useState<string | null>(null);

  const dragVisuals = useDragVisuals();
  const { dragState, dropEdge } = dragVisuals;
  const { epicCols, subEpicCols, storyCol, totalCols } = computeColumnLayout(epics, dragVisuals);
  const gridCols = colTemplate(totalCols);

  // Grid row constants — keep in sync with test assertions
  const ROW_EPICS = 1;
  const ROW_SUB_EPICS = 2;
  const ROW_SPINE = 3;
  const ROW_UNASSIGNED_ZONE = 4;       // "Unassigned" drop zone (Increment View only)
  const incLabelRow = (i: number) => 5 + 2 * i;
  const incCardsRow = (i: number) => 5 + 2 * i + 1;
  const incAddRow   = (n: number) => 5 + 2 * n;

  /** Render a StoryCard with all callbacks wired — used in both spine and increment rows.
   *  Pass `isFirst=true` for the first story in a sub-epic group to show the prepend + button. */
  // The rows of every epic, and the epics, by the id a drop's list names them by.
  const rowsById = new Map(epics.flatMap((e) => e.subEpics.map((s) => [s.id, s] as const)));
  const epicsById = new Map(epics.map((e) => [e.id, e] as const));
  const getSubEpicStoryIds = (subEpicId: string) => rowsById.get(subEpicId)?.stories.map((st) => st.id) ?? [];
  const getEpicIds = () => epics.map((e) => e.id);
  const getEpicSubEpicIds = (epicId: string) => epicsById.get(epicId)?.subEpics.map((s) => s.id) ?? [];
  // A node dropped into a list goes before the node that follows it there; dropped last, it stays where it was.
  const moveInto = (siblings: StoryNodeOnPage[], dragged: StoryNodeOnPage | undefined, order: string[]) => {
    const next = siblings.find((each) => each.id === order[order.indexOf(dragged?.id ?? '') + 1]);
    if (dragged && next) edit(() => dragged.moveBefore(next));
  };
  const onMoveStory = (storyId: string, rowId: string, order: string[]) => moveInto(rowsById.get(rowId)?.stories ?? [], storiesById.get(storyId), order);
  const onMoveSubEpic = (subEpicId: string, epicId: string, order: string[]) => moveInto(epicsById.get(epicId)?.subEpics ?? [], rowsById.get(subEpicId), order);
  const onReorderEpics = (order: string[]) => edit(() => map.reorder(epics, order));

  // ── Authoritative container-level drop commit ──────────────────────────────
  // Native HTML5 drag only fires `drop` on an element whose `dragover` called
  // preventDefault(). During a drag the grid constantly reflows, so the element
  // under the cursor flickers between real drop targets and non-targets (card
  // child buttons, the drag-handle, the bare grid container). Any dragover that
  // lands on a non-target leaves the browser in "no drop allowed" state, so a
  // mouse-up there fires NO drop and the operation silently reverts. Making the
  // whole grid a drop surface guarantees preventDefault() runs wherever the
  // cursor is, so `drop` always fires; the live `dropEdge` (set by the specific
  // target's dragover) remains the authoritative landing position.
  const commitDropFromEdge = () => {
    const draggedId = dragRef.current;
    const kind = dragKindRef.current;
    const edge = dragVisuals.dropEdgeRef.current; // ref, not render-closure state — always current
    dragRef.current = null;
    dragKindRef.current = null;
    dragVisuals.end();
    if (!draggedId || !kind || !edge) return;
    if (kind === 'story') {
      onMoveStory(draggedId, edge.listKey, insertBeforeId(getSubEpicStoryIds(edge.listKey), draggedId, edge.beforeId));
    } else if (kind === 'sub-epic') {
      onMoveSubEpic(draggedId, edge.listKey, insertBeforeId(getEpicSubEpicIds(edge.listKey), draggedId, edge.beforeId));
    } else if (kind === 'epic') {
      onReorderEpics(insertBeforeId(getEpicIds(), draggedId, edge.beforeId));
    }
  };
  const containerDragHandlers = {
    onDragOver: (e: React.DragEvent<Element>) => {
      if (!dragKindRef.current) return; // not our drag
      e.preventDefault(); // keep the drop alive across the whole grid, even over non-target fragments
      // A valid target's own dragover sets a fresh edge (and, for the wrong kind, clears
      // it). So a non-null edge here == the cursor is over a valid landing spot right now.
      dragLandedValidRef.current = dragVisuals.dropEdgeRef.current !== null;
      if (e.dataTransfer) e.dataTransfer.dropEffect = dragVisuals.dropEdgeRef.current ? 'move' : 'none';
    },
    onDragLeave: (e: React.DragEvent<Element>) => {
      // Cursor left the whole grid — from here a release is a cancel, not a drop.
      if (e.currentTarget === e.target) dragLandedValidRef.current = false;
    },
    onDrop: (e: React.DragEvent<Element>) => {
      if (!dragKindRef.current) return;
      e.preventDefault();
      commitDropFromEdge();
    },
    // Fallback commit. onDragEnd ALWAYS fires (unlike `drop`, which the browser skips when
    // the release lands on the reflowed placeholder or a card child control). Commit only
    // when the last position was a VALID target (tracked in dragLandedValidRef via the
    // per-target dragover / clearEdge / grid dragleave); a cancel (Escape, released outside
    // the grid, or over a wrong-kind row) restores the original order. `drop` already
    // committed nulls dragKindRef, so this becomes a no-op after a real drop.
    onDragEnd: () => {
      if (!dragKindRef.current) return;
      if (dragLandedValidRef.current) commitDropFromEdge();
      else { dragRef.current = null; dragKindRef.current = null; dragVisuals.end(); }
      dragLandedValidRef.current = false;
    },
  };

  const renderStoryCard = (story: StoryOnPage, row: EpicOnPage, isFirst = false) => {
    const baseDrag = makeStoryDragHandlers(
      dragRef,
      dragKindRef,
      story.id,
      row.id,
      () => getSubEpicStoryIds(row.id),
      onMoveStory,
      dragVisuals,
    );

    // Intercept onDragStart to also track the dragged story ID for cross-row increment drop,
    // and onDragEnd to clear any lingering Increment drop-target highlight.
    const dragHandlers = {
      ...baseDrag,
      onDragStart: (e: React.DragEvent<Element>) => {
        storyDragRef.current = story.id;
        baseDrag.onDragStart(e);
      },
      onDragEnd: () => {
        setDragOverIncrementId(null);
        baseDrag.onDragEnd();
      },
    };

    return (
      <StoryCard
        story={story}
        row={row}
        isFirst={isFirst}
        isExpanded={expandedNodeIds.has(story.id)}
        onNodeClick={onNodeClick}
        onExpand={onExpand}
        edit={edit}
        onOpenFile={onOpenFile}
        dragHandlers={dragHandlers}
        dropIndicatorClass={
          dropIndicatorClass(dropEdge, row.id, story.id) +
          (isBeingDragged(dragState, 'story', story.id) ? ' being-dragged' : '')
        }
      />
    );
  };

  // The story a drop onto an increment names: the story dragged, else the one the drop's data names.
  const droppedStory = (drop: React.DragEvent<Element>): StoryOnPage | undefined => {
    const sid = storyDragRef.current ?? drop.dataTransfer?.getData('text/plain') ?? null;
    storyDragRef.current = null;
    // This is an increment (un)assignment, not a parent move — cancel the
    // cross-parent drag so the container's dragend fallback doesn't also fire.
    dragRef.current = null; dragKindRef.current = null; dragVisuals.end();
    return sid ? storiesById.get(sid) : undefined;
  };

  return (
    /*
     * Single shared CSS Grid — all rows (epics, sub-epics, spine, increments)
     * are direct children of ONE grid container so that expanding a story card
     * in the spine row causes its column to widen, which automatically pushes
     * the parent epic/sub-epic spans AND every column to the right.
     *
     * Rows are placed via explicit gridRow indices:
     *   1 → Epic lanes
     *   2 → SubEpic lanes
     *   3 → Spine (unassigned) story cards
     *   4 + 2*i   → Increment i label (spans all columns)
     *   4 + 2*i+1 → Increment i story cards
     */
    <div
      className="story-hierarchy-view"
      style={{
        display: 'grid',
        gridTemplateColumns: gridCols,
        rowGap: 'var(--row-gap)',
        columnGap: 'var(--row-gap)',
        alignItems: 'start',
      }}
      {...containerDragHandlers}
    >
      {/* ── Row 1: Epic lanes ─────────────────────────────────────────── */}
      {epics.length === 0
        ? <AddNodePopoverButton
            className="add-root-btn"
            title="Add Epic"
            buttonLabel="+ Epic"
            placeholder="Epic title (optional)"
            style={{ gridRow: ROW_EPICS, gridColumn: 1 }}
            onAdd={(name) => edit(() => map.addEpic(named(name, NEW_NAMES.epic)))}
          />
        : epics.map((epic, epicIdx) => {
            const at = epicCols.get(epic.id)!;
            const epicDragHandlers = makeEpicDragHandlers(
              dragRef,
              dragKindRef,
              epic.id,
              () => epics.map((e) => e.id),
              onReorderEpics,
              dragVisuals,
            );
            return (
              <div
                key={epic.id}
                className={`epic-lane${isBeingDragged(dragState, 'epic', epic.id) ? ' being-dragged' : ''}`}
                style={{ gridRow: ROW_EPICS, gridColumn: `${at.start} / span ${at.span}` }}
                onClick={() => onNodeClick(epic.id)}
                onDoubleClick={focusNameFieldOnDoubleClick}
                {...epicDragHandlers}
              >
                <div className="type-label-row">
                  <div className="type-label-left">
                    <span
                      className="drag-handle"
                      aria-hidden="true"
                      draggable={epicDragHandlers.draggable}
                      onDragStart={(e) => { e.stopPropagation(); epicDragHandlers.onDragStart(e); }}
                      onDragEnd={() => { epicDragHandlers.onDragEnd(); }}
                    >
                      ⠿
                    </span>
                  </div>
                  <div className="type-label-center">
                    <span className="type-label type-label-epic-subepic">EPIC</span>
                  </div>
                  <div className="type-label-right">
                    <span className="node-actions">
                      <button className="node-btn" title="Expand descendants" onClick={(e) => { e.stopPropagation(); onExpand(epic.id, epic.storiesShown.map((story) => story.id)); }}>↕</button>
                      <AddNodePopoverButton
                        className="node-btn plus-btn"
                        title="Add Epic"
                        buttonLabel="+"
                        placeholder="Epic title (optional)"
                        onAdd={(name) => edit(() => map.addEpic(named(name, NEW_NAMES.epic), epics[epicIdx + 1]))}
                      />
                      <button className="node-btn minus-btn" title="Delete Epic" onClick={(e) => { e.stopPropagation(); edit(() => epic.remove()); }}>−</button>
                    </span>
                  </div>
                </div>
                <NodeNameInput node={epic} edit={edit} className="node-label" />
                {expandedNodeIds.has(epic.id) && (
                  <DescriptionEditor key={epic.description} node={epic} edit={edit} />
                )}
              </div>
            );
          })
      }

      {/* ── Row 2: SubEpic lanes ──────────────────────────────────────── */}
      {epics.flatMap((epic) => {
        const epicAt = epicCols.get(epic.id)!;
        // A sub-epic added first goes before the first epic nested under this one, after the row of its own stories.
        const firstNested = epic.subEpics.find((sub) => sub.id !== epic.id);
        const displaySubEpicIds = computeDisplayIds(epic.subEpics.map((s) => s.id), { listKey: epic.id, kind: 'sub-epic' }, dragVisuals);
        if (displaySubEpicIds.length === 0) {
          return [
            // The "+" button stays small/visible, but the drop target spans the whole
            // reserved cell — otherwise half of a widened empty-Epic slot has nothing
            // listening for the drop and a dragged SubEpic silently fails to land.
            <div
              key={`sub-empty-${epic.id}`}
              className={`empty-parent-dropzone${isDropScopeActive(dropEdge, epic.id) ? ' drop-target-active' : ''}`}
              data-epic-id={epic.id}
              style={{ gridRow: ROW_SUB_EPICS, gridColumn: `${epicAt.start} / span ${epicAt.span}`, alignSelf: 'stretch' }}
              {...makeEmptyParentDropZone(dragRef, dragKindRef, 'sub-epic', epic.id, onMoveSubEpic, dragVisuals)}
            >
              <AddNodePopoverButton
                className="node-btn plus-btn row-lead-plus"
                title="Add SubEpic"
                buttonLabel="+"
                placeholder="SubEpic title (optional)"
                onAdd={(name) => edit(() => epic.newSubEpic(named(name, NEW_NAMES.subEpic), firstNested))}
              />
            </div>,
          ];
        }
        return epic.subEpics.map((sub, subIdx) => {
          const at = subEpicCols.get(sub.id)!;
          const isFirst = subIdx === 0;
          const subEpicDragHandlers = makeSubEpicDragHandlers(
            dragRef,
            dragKindRef,
            sub.id,
            epic.id,
            () => epic.subEpics.map((s) => s.id),
            onMoveSubEpic,
            dragVisuals,
          );
          return (
            <div
              key={sub.id}
              className={
                `sub-epic-lane${dropIndicatorClass(dropEdge, epic.id, sub.id)}` +
                (isBeingDragged(dragState, 'sub-epic', sub.id) ? ' being-dragged' : '')
              }
              style={{ gridRow: ROW_SUB_EPICS, gridColumn: `${at.start} / span ${at.span}` }}
              onClick={() => onNodeClick(sub.id)}
              onDoubleClick={focusNameFieldOnDoubleClick}
              {...subEpicDragHandlers}
            >
              <div className="type-label-row">
                <div className="type-label-left">
                  {isFirst && (
                    <AddNodePopoverButton
                      className="node-btn plus-btn row-lead-plus"
                      title="Add SubEpic at beginning"
                      buttonLabel="+"
                      placeholder="SubEpic title (optional)"
                      onAdd={(name) => edit(() => epic.newSubEpic(named(name, NEW_NAMES.subEpic), firstNested))}
                    />
                  )}
                  <span
                    className="drag-handle"
                    aria-hidden="true"
                    draggable={subEpicDragHandlers.draggable}
                    onDragStart={(e) => { e.stopPropagation(); subEpicDragHandlers.onDragStart(e); }}
                    onDragEnd={() => { subEpicDragHandlers.onDragEnd(); }}
                  >
                    ⠿
                  </span>
                </div>
                <div className="type-label-center">
                  <span className="type-label type-label-epic-subepic">SUB-EPIC</span>
                </div>
                <div className="type-label-right">
                  <span className="node-actions">
                    <button className="node-btn" onClick={(e) => { e.stopPropagation(); onExpand(sub.id, sub.stories.map((s) => s.id)); }}>↕</button>
                    <AddNodePopoverButton
                      className="node-btn plus-btn"
                      title="Add SubEpic"
                      buttonLabel="+"
                      placeholder="SubEpic title (optional)"
                      onAdd={(name) => edit(() => epic.newSubEpic(named(name, NEW_NAMES.subEpic), epic.subEpics[subIdx + 1]))}
                    />
                    <button className="node-btn minus-btn" title="Delete SubEpic" onClick={(e) => { e.stopPropagation(); edit(() => sub.remove()); }}>−</button>
                  </span>
                </div>
              </div>
              <NodeNameInput node={sub} edit={edit} className="node-label" />
              {/* An epic's own stories show as a row named for the epic, whose description the epic's lane edits. */}
              {sub.id !== epic.id && expandedNodeIds.has(sub.id) && (
                <DescriptionEditor key={sub.description} node={sub} edit={edit} />
              )}
            </div>
          );
        });
      })}

      {/* ── Row 3: Spine (unassigned) story cards ────────────────────── */}
      {epics.flatMap((epic) =>
        epic.subEpics.flatMap((sub) => {
          const subAt = subEpicCols.get(sub.id)!;
          const displayStoryIds = computeDisplayIds(sub.stories.map((s) => s.id), { listKey: sub.id, kind: 'story' }, dragVisuals);
          if (displayStoryIds.length === 0) {
            return [
              // Same reasoning as the empty-Epic dropzone above — the "+" button stays
              // small, but the drop target spans the whole reserved (now 2-column) cell.
              <div
                key={`story-empty-${sub.id}`}
                className={`empty-parent-dropzone${isDropScopeActive(dropEdge, sub.id) ? ' drop-target-active' : ''}`}
                data-sub-epic-id={sub.id}
                style={{ gridRow: ROW_SPINE, gridColumn: `${subAt.start} / span ${subAt.span}`, alignSelf: 'stretch' }}
                {...makeEmptyParentDropZone(dragRef, dragKindRef, 'story', sub.id, onMoveStory, dragVisuals)}
              >
                <AddNodePopoverButton
                  className="node-btn plus-btn row-lead-plus"
                  title="Add Story"
                  buttonLabel="+"
                  placeholder="Story title (optional)"
                  onAdd={(name) => edit(() => sub.newStory(named(name, NEW_NAMES.story)))}
                />
              </div>,
            ];
          }
          return sub.stories
            // Increment-assigned Stories only move down to an Increment row once
            // Increment View is actually rendering one for them — otherwise they'd
            // vanish entirely, leaving a phantom reserved column in this SubEpic.
            .filter((s) => !showIncrements || !s.increment)
            .map((story, storyIdx) => (
              <div key={story.id} data-row-type="spine" style={{ gridRow: ROW_SPINE, gridColumn: storyCol.get(story.id) }}>
                {renderStoryCard(story, sub, storyIdx === 0)}
              </div>
            ));
        }),
      )}

      {/* ── Row 4: Unassigned drop zone (Increment View only) ────────── */}
      {showIncrements && (
        <div
          className="unassigned-drop-zone"
          style={{ gridRow: ROW_UNASSIGNED_ZONE, gridColumn: `1 / span ${totalCols}` }}
          onDragEnter={(e) => e.currentTarget.classList.add('drag-over')}
          onDragLeave={(e) => e.currentTarget.classList.remove('drag-over')}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            e.currentTarget.classList.remove('drag-over');
            const story = droppedStory(e);
            const increment = story?.increment;
            if (story && increment) edit(() => increment.stopDelivering(story));
          }}
        >
          ↑ Unassigned — drop here to remove from increment
        </div>
      )}

      {/* ── Rows 5+: Increment rows (label + cards) ──────────────────── */}
      {showIncrements && increments.map((inc, incIdx) => {
        const labelRow = incLabelRow(incIdx);
        const cardsRow = incCardsRow(incIdx);
        return (
          <React.Fragment key={inc.id}>
            {/* Increment label — full-width drop target for story assignment. Highlight is
                driven by shared dragOverIncrementId (not local DOM classList) so it lights
                up together with the cards band below as ONE zone, not two flickering ones. */}
            <div
              className={`increment-row${dragOverIncrementId === inc.id ? ' drag-over' : ''}`}
              style={{ gridRow: labelRow, gridColumn: `1 / span ${totalCols}` }}
              onDragEnter={() => setDragOverIncrementId(inc.id)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                setDragOverIncrementId(null);
                const story = droppedStory(e);
                if (story) edit(() => inc.deliver(story));
              }}
            >
              <IncrementLabel
                increment={inc}
                edit={edit}
                dragHandlers={makeDragHandlers(incDragRef, inc.id, () => increments.map((i) => i.id), (order) => edit(() => map.reorder(increments, order)))}
              />
            </div>
            {/* Full-width drop band behind the cards row — lets a Story be dropped
                anywhere in the Increment, not just on its thin label bar above.
                alignSelf: 'stretch' overrides the grid's default 'start' so this
                fills the row's full height (matching its tallest story card)
                instead of collapsing to zero since the div itself has no content. */}
            <div
              className={`increment-cards-dropzone${dragOverIncrementId === inc.id ? ' drag-over' : ''}`}
              style={{ gridRow: cardsRow, gridColumn: `1 / span ${totalCols}`, alignSelf: 'stretch' }}
              onDragEnter={() => setDragOverIncrementId(inc.id)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                setDragOverIncrementId(null);
                const story = droppedStory(e);
                if (story) edit(() => inc.deliver(story));
              }}
            />
            {/* Increment story cards — placed at their story column positions */}
            {epics.flatMap((epic) =>
              epic.subEpics.flatMap((sub) => {
                const filtered = sub.stories.filter((s) => inc.delivers(s));
                return filtered.map((story, storyIdx) => (
                  <div key={story.id} data-row-type={`increment-${inc.id}`} style={{ gridRow: cardsRow, gridColumn: storyCol.get(story.id) }}>
                    {renderStoryCard(story, sub, storyIdx === 0)}
                  </div>
                ));
              }),
            )}
          </React.Fragment>
        );
      })}

      {/* Add Increment button */}
      {showIncrements && (
        <button
          className="add-root-btn"
          title="Add Increment"
          style={{ gridRow: incAddRow(increments.length), gridColumn: 1 }}
          onClick={() => edit(() => map.addIncrement(NEW_NAMES.increment))}
        >+ Increment</button>
      )}
    </div>
  );
}


// ---------------------------------------------------------------------------
// NodeNameInput — shared inline-rename control for Epic/SubEpic lane labels;
// saves through the node's own rename, as a story card's name does.
// ---------------------------------------------------------------------------

function NodeNameInput({
  node,
  edit,
  className,
}: {
  node: StoryNodeOnPage;
  edit: Edit;
  className: string;
}) {
  const [editName, setEditName] = useState(node.name);
  const save = () => { if (editName && editName !== node.name) edit(() => node.rename(editName)); };
  return (
    <>
      <input
        className={className}
        size={Math.max(1, editName.length)}
        value={editName}
        onClick={(e) => e.stopPropagation()}
        onDoubleClick={(e) => { e.stopPropagation(); e.currentTarget.select(); }}
        onChange={(e) => setEditName(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === 'Tab') { e.preventDefault(); e.stopPropagation(); save(); }
          if (e.key === 'Escape') { e.stopPropagation(); setEditName(node.name); }
        }}
        onBlur={save}
      />
    </>
  );
}

// ---------------------------------------------------------------------------
// IncrementLabel — inline-editable Increment name (rename through the increment's
// own rename, as Stories' names are) + delete
// ---------------------------------------------------------------------------

function IncrementLabel({
  increment,
  edit,
  dragHandlers,
}: {
  increment: IncrementOnPage;
  edit: Edit;
  dragHandlers: ReturnType<typeof makeDragHandlers>;
}) {
  const [editName, setEditName] = useState(increment.name);
  const save = () => { if (editName && editName !== increment.name) edit(() => increment.rename(editName)); };
  return (
    <div className="increment-label" onDoubleClick={focusNameFieldOnDoubleClick} {...dragHandlers}>
      <span className="drag-handle" aria-hidden="true">⠿</span>
      <input
        className="increment-name-input"
        aria-label={`Increment name for ${increment.name}`}
        value={editName}
        onClick={(e) => e.stopPropagation()}
        onDoubleClick={(e) => { e.stopPropagation(); e.currentTarget.select(); }}
        onChange={(e) => setEditName(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === 'Tab') { e.preventDefault(); save(); }
          if (e.key === 'Escape') setEditName(increment.name);
        }}
        onBlur={save}
      />
      <button className="node-btn minus-btn" title="Delete Increment" onClick={() => edit(() => increment.remove())}>−</button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// StoryCard — collapsed or inline-expanded
// ---------------------------------------------------------------------------

interface StoryCardProps {
  story: StoryOnPage;
  // The row the card sits in, whose epic adds a story beside it.
  row: EpicOnPage;
  // The first card of its row shows the button that adds a story at the row's start.
  isFirst: boolean;
  isExpanded: boolean;
  onNodeClick: (id: string) => void;
  onExpand: (id: string, descendantIds: string[]) => void;
  edit: Edit;
  dragHandlers: ReturnType<typeof makeStoryDragHandlers>;
  /** Extra className applied to the outer card — shows the "insert before" drop-position indicator. */
  dropIndicatorClass?: string;
  onOpenFile?: (path: string) => void;
}

function StoryCard(props: StoryCardProps) {
  const { isExpanded, dragHandlers, dropIndicatorClass = '' } = props;
  return (
    <div className={`story-card${isExpanded ? ' expanded' : ''}${dropIndicatorClass}`} {...dragHandlers}>
      <StoryCardHeader {...props} />
      {/* Expansion panel — always visible when expanded, regardless of Show Scenarios toggle */}
      {isExpanded && <StoryExpansionPanel {...props} />}
    </div>
  );
}

// The card's header: its drag handle, the buttons that add, expand and remove stories, and its name, edited in place.
// A story added after this one goes before the story that follows it in its row.
function StoryCardHeader({ story, row, isFirst, isExpanded, onNodeClick, onExpand, edit, dragHandlers }: StoryCardProps) {
  const { draggable: storyDraggable, onDragStart: storyOnDragStart, onDragEnd: storyOnDragEnd } = dragHandlers;
  const following = row.stories[row.stories.findIndex((each) => each.id === story.id) + 1];
  return (
    <div className="story-card-header" onClick={() => onNodeClick(story.id)} onDoubleClick={focusNameFieldOnDoubleClick}>
      <div className="type-label-row">
        <div className="type-label-left">
          {isFirst && (
            <AddNodePopoverButton className="node-btn plus-btn row-lead-plus" title="Add Story at beginning" buttonLabel="+" placeholder="Story title (optional)" onAdd={(name) => edit(() => row.newStory(named(name, NEW_NAMES.story), row.stories[0]))} />
          )}
          <span className="drag-handle" aria-hidden="true" draggable={storyDraggable} onDragStart={(e) => { e.stopPropagation(); storyOnDragStart(e); }} onDragEnd={() => { storyOnDragEnd(); }}>
            ⠿
          </span>
        </div>
        <div className="type-label-center">
          <span className="type-label">STORY</span>
        </div>
        <div className="type-label-right">
          <span className="node-actions">
            <button className="expand-btn" title="Expand story" onClick={(e) => { e.stopPropagation(); onExpand(story.id, []); }}>
              {isExpanded ? '▲' : '▼'}
            </button>
            <AddNodePopoverButton className="node-btn plus-btn" title="Add Story" buttonLabel="+" placeholder="Story title (optional)" onAdd={(name) => edit(() => row.newStory(named(name, NEW_NAMES.story), following))} />
            <button className="node-btn minus-btn" title="Delete Story" onClick={(e) => { e.stopPropagation(); edit(() => story.remove()); }}>−</button>
          </span>
        </div>
      </div>
      <StoryNameEditor story={story} edit={edit} />
    </div>
  );
}

// A story's name, edited in place and saved on Enter or when the person leaves it.
function StoryNameEditor({ story, edit }: Pick<StoryCardProps, 'story' | 'edit'>) {
  const [editName, setEditName] = useState(story.name);
  const saveName = () => { if (editName && editName !== story.name) edit(() => story.rename(editName)); };
  return (
    <div
      className="story-name-input"
      contentEditable={true}
      suppressContentEditableWarning={true}
      onInput={(e) => setEditName(e.currentTarget.textContent || '')}
      onDoubleClick={(e) => { e.stopPropagation(); e.currentTarget.focus(); selectWholeName(e.currentTarget); }}
      onKeyDown={(e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); e.stopPropagation(); saveName(); }
        if (e.key === 'Escape') { setEditName(story.name); e.currentTarget.blur(); }
      }}
      onBlur={saveName}
      onClick={(e) => e.stopPropagation()}
    >{editName}</div>
  );
}

// An expanded story: its description, its acceptance tests and its scenarios, each scenario dragged to reorder.
function StoryExpansionPanel({ story, edit, onOpenFile }: StoryCardProps) {
  const scenarioDragRef = useRef<string | null>(null);
  return (
    <div className="story-expansion-panel">
      <DescriptionEditor key={story.description} node={story} edit={edit} />
      <AcceptanceTestsView files={story.acceptanceTests} onOpen={onOpenFile} />
      <div className="section-heading">
        <span>Scenarios</span>
        <button className="node-btn plus-btn" title="Add Scenario" onClick={() => edit(() => story.newScenario(NEW_NAMES.scenario))}>+</button>
      </div>
      {story.scenarios.map((sc) => (
        <div key={sc.id} className="scenario-row-drag" {...makeDragHandlers(scenarioDragRef, sc.id, () => story.scenarios.map((s) => s.id), (ids) => edit(() => story.reorderScenarios(ids)))}>
          <ScenarioPanel scenario={sc} edit={edit} />
        </div>
      ))}
    </div>
  );
}

function AddNodePopoverButton({
  className,
  title,
  buttonLabel,
  placeholder,
  style,
  onAdd,
}: {
  className: string;
  title: string;
  buttonLabel: string;
  placeholder: string;
  style?: React.CSSProperties;
  onAdd: (name?: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');

  const submit = () => {
    const trimmed = name.trim();
    onAdd(trimmed.length > 0 ? trimmed : undefined);
    setName('');
    setOpen(false);
  };

  return (
    <span
      className="add-node-popover"
      style={style}
      onClick={(e) => e.stopPropagation()}
      onDoubleClick={(e) => e.stopPropagation()}
    >
      <button
        className={className}
        title={title}
        onClick={(e) => {
          e.stopPropagation();
          setOpen((v) => !v);
        }}
      >
        {buttonLabel}
      </button>
      {open && (
        <span className="add-node-popover-card" role="dialog" aria-label={`${title} dialog`}>
          <input
            className="add-node-popover-input"
            autoFocus
            placeholder={placeholder}
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                submit();
              }
              if (e.key === 'Escape') {
                e.preventDefault();
                setName('');
                setOpen(false);
              }
            }}
          />
          <button className="save-inline-btn" type="button" onClick={submit}>Add</button>
          <button className="cancel-inline-btn" type="button" onClick={() => { setName(''); setOpen(false); }}>Cancel</button>
        </span>
      )}
    </span>
  );
}

function ScenarioPanel({ scenario, edit }: { scenario: ScenarioOnPage; edit: Edit }) {
  const stepDragRef = useRef<string | null>(null);
  const [scenarioName, setScenarioName] = useState(scenario.name);
  const saveScenarioName = () => { if (scenarioName && scenarioName !== scenario.name) edit(() => scenario.rename(scenarioName)); };

  return (
    <div className="scenario-panel">
      <div className="scenario-header">
        <span className="drag-handle" aria-hidden="true">⠿</span>
        <input
          className="scenario-name-input"
          value={scenarioName}
          placeholder="Scenario name…"
          onClick={(e) => e.stopPropagation()}
          onDoubleClick={(e) => { e.stopPropagation(); e.currentTarget.select(); }}
          onChange={(e) => setScenarioName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === 'Tab') { e.preventDefault(); saveScenarioName(); }
            if (e.key === 'Escape') setScenarioName(scenario.name);
          }}
          onBlur={saveScenarioName}
        />
        <button className="node-btn minus-btn" title="Delete Scenario" onClick={() => edit(() => scenario.remove())}>−</button>
      </div>

      <div className="steps-section">
        <div className="section-heading indent">
          <span>Steps</span>
          <button className="node-btn plus-btn" title="Add Step" onClick={() => edit(() => scenario.newStep('given', NEW_NAMES.step))}>+</button>
        </div>
        <ol className="step-list">
          {scenario.steps.map((step) => (
            <li
              key={step.id}
              className="step-row"
              {...makeDragHandlers(stepDragRef, step.id, () => scenario.steps.map((s) => s.id), (ids) => edit(() => scenario.reorderSteps(ids)))}
            >
              <span className="drag-handle" aria-hidden="true">⠿</span>
              <StepEditor key={`${step.id}-${step.keyword}-${step.text}`} step={step} edit={edit} />
              <button className="node-btn minus-btn" title="Delete Step" onClick={() => edit(() => step.remove())}>−</button>
            </li>
          ))}
        </ol>
      </div>

      <ExampleTableView scenario={scenario} edit={edit} />
    </div>
  );
}

// ---------------------------------------------------------------------------
// StepEditor — inline-editable step (keyword selector + text); the text is saved through the step's edit_text
// ---------------------------------------------------------------------------
function StepEditor({ step, edit }: { step: StepOnPage; edit: Edit }) {
  const [text, setText] = useState(step.text);
  const [keyword, setKeyword] = useState<StepKeyword>(step.keyword);
  const save = () => { if (text !== step.text) edit(() => step.editText(text)); };
  return (
    <span className="step-editor">
      <select
        className="step-type-select"
        value={keyword}
        onChange={(e) => { setKeyword(e.target.value as StepKeyword); }}
        onBlur={save}
      >
        {STEP_KEYWORDS.map((each) => <option key={each} value={each}>{each}</option>)}
      </select>
      <input
        className="step-text-input"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === 'Tab') { e.preventDefault(); save(); } if (e.key === 'Escape') { setText(step.text); setKeyword(step.keyword); } }}
        onBlur={save}
      />
    </span>
  );
}

// A scenario's examples as the story model holds them: a row per example. Each cell its row has is edited through that
// example's edit_field when it changes; a column only other rows have stays empty and read only.
function ExampleTableView({ scenario, edit }: { scenario: ScenarioOnPage; edit: Edit }) {
  if (!scenario.examples.length) return null;
  const columns = scenario.exampleColumns;
  return (
    <div className="examples-section">
      <div className="section-heading indent"><span>Examples</span></div>
      <div className="example-block">
      <table>
        <thead>
          <tr>{columns.map((column) => <th key={column}>{column}</th>)}<th aria-label="Remove" /></tr>
        </thead>
        <tbody>
          {scenario.examples.map((example) => (
            <tr key={example.id}>
              {columns.map((column) => (
                <td key={column}>
                  {column in example.fields
                    ? <ExampleCellEditor key={`${example.id}-${example.fields[column]}`} label={`${column} of ${example.fields.example}`} value={example.fields[column]!} onSave={(value) => edit(() => example.editField(column, value))} />
                    : null}
                </td>
              ))}
              <td><button className="node-btn minus-btn" title="Delete Example" onClick={() => edit(() => example.remove())}>−</button></td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </div>
  );
}

// One cell of an example's row, saved when it changes and the person leaves it or presses Enter.
function ExampleCellEditor({ label, value, onSave }: { label: string; value: string; onSave: (value: string) => void }) {
  const [text, setText] = useState(value);
  const save = () => { if (text !== value) onSave(text); };
  return (
    <input
      className="example-cell-input"
      aria-label={label}
      value={text}
      onClick={(e) => e.stopPropagation()}
      onChange={(e) => setText(e.target.value)}
      onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); save(); } if (e.key === 'Escape') setText(value); }}
      onBlur={save}
    />
  );
}

// What the story map says about a node, under its heading; saved through the node's edit_description when it changes.
function DescriptionEditor({ node, edit }: { node: StoryNodeOnPage; edit: Edit }) {
  const [text, setText] = useState(node.description);
  const save = () => { if (text.trim() !== node.description) edit(() => node.describe(text)); };
  return (
    <div className="description-section">
      <div className="section-heading"><span>Description</span></div>
      <textarea
        className="description-input"
        aria-label={`Description of ${node.name}`}
        value={text}
        placeholder="What the story map says about it…"
        onChange={(e) => setText(e.target.value)}
        onClick={(e) => e.stopPropagation()}
        onBlur={save}
        onKeyDown={(e) => { if (e.key === 'Escape') setText(node.description); }}
      />
    </div>
  );
}

// A story's acceptance tests are not edited here: each is a link that opens the file in the chat bar's file viewer of the
// chat this page was opened beside. A page no chat opened names the files and says where to read them.
function AcceptanceTestsView({ files, onOpen }: { files: string[]; onOpen?: (path: string) => void }) {
  if (!files.length) return null;
  return (
    <div className="acceptance-tests-section">
      <div className="section-heading"><span>Acceptance tests</span></div>
      <ul className="acceptance-test-links">
        {files.map((file) => (
          <li key={file}>
            {onOpen
              ? <button type="button" className="acceptance-test-link" title="Open in the chat bar's file viewer" onClick={(e) => { e.stopPropagation(); onOpen(file); }}>{file}</button>
              : <span className="acceptance-test-path">{file}</span>}
          </li>
        ))}
      </ul>
      {!onOpen && <p className="acceptance-test-note" role="note">Open the Story UI from the chat bar, or from a ticket with a chat, to read these files in the chat's file viewer.</p>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// StoryMapWorkspaceView — the page: toolbar, format toggles, the map, and what failed
// ---------------------------------------------------------------------------

interface StoryMapWorkspaceViewProps {
  // The Stories file to open, from the page's ?file= link; none follows the session open in the project.
  file: string | null;
  // What failed on the page, shown here and sent to the chat the page was opened beside (its ?chat= link), whose file
  // viewer also shows a story's acceptance tests; that chat is empty for a page no chat opened.
  failures: StoryMapFailures;
}

// A view that throws would otherwise leave an empty page, so the person sees what broke, and the chat that opened the
// page is told, as every other failure is.
export class StoryMapFailureView extends Component<{ failures: StoryMapFailures; children: ReactNode }, { failure: string }> {
  state = { failure: '' };

  static getDerivedStateFromError(error: unknown) {
    return { failure: error instanceof Error ? error.message : String(error) };
  }

  componentDidCatch(error: unknown, failedComponents: ErrorInfo) {
    this.props.failures.failWith(error, `A Story UI view failed to draw:${failedComponents.componentStack ?? ''}`);
  }

  render() {
    if (!this.state.failure) return this.props.children;
    return (
      <div className="loading" role="alert">
        <span className="status-dot error" />The Story UI page failed: {this.state.failure}
        <button type="button" className="toolbar-btn" onClick={() => location.reload()}>Reload</button>
      </div>
    );
  }
}

type ColorMode = 'executive' | 'engineering';
const THEME_STORAGE_KEY = 'story-map-theme';
const NEW_NAMES = { epic: 'New Epic', subEpic: 'New SubEpic', story: 'New Story', scenario: 'New Scenario', step: 'New step', increment: 'New Increment' } as const;

// The formats chosen for the fidelity of the open file in the session: the chat bar's chips show the same choice, and
// the next edit renders to the formats on.
function FormatTogglesView({ map, onToggle }: { map: StoryMapClient; onToggle: (format: string, isChosen: boolean) => void }) {
  const { offered_formats: offered, chosen_formats: chosen } = map.formats;
  return (
    <div className="mode-switch" role="group" aria-label="Formats saved">
      {offered.map((format) => (
        <button key={format} type="button" className={chosen.includes(format) ? 'active' : ''} aria-pressed={chosen.includes(format)} onClick={() => onToggle(format, !chosen.includes(format))}>
          {format}
        </button>
      ))}
    </div>
  );
}

function themeOnOpen(): ColorMode {
  if (typeof window === 'undefined') return 'executive';
  return window.localStorage.getItem(THEME_STORAGE_KEY) === 'engineering' ? 'engineering' : 'executive';
}

const RIGHT_MOUSE_BUTTON = 2;
type PanStart = { x: number; y: number; left: number; top: number };

// While a pan is under way the canvas follows the pointer, even when the pointer leaves it, until the button is let go.
function usePanFollowingPointer(canvasRef: React.RefObject<HTMLDivElement>, panStart: PanStart | null, stopPanning: () => void) {
  useEffect(() => {
    if (!panStart) return undefined;
    const move = (pointer: MouseEvent) => {
      if (!canvasRef.current) return;
      canvasRef.current.scrollLeft = panStart.left - (pointer.clientX - panStart.x);
      canvasRef.current.scrollTop = panStart.top - (pointer.clientY - panStart.y);
    };
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', stopPanning);
    return () => {
      window.removeEventListener('mousemove', move);
      window.removeEventListener('mouseup', stopPanning);
    };
  }, [canvasRef, panStart, stopPanning]);
}

// Right-drag pans the canvas, even when the pointer leaves it.
function useCanvasPanning() {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [panStart, setPanStart] = useState<PanStart | null>(null);
  const stopPanning = useCallback(() => setPanStart(null), []);
  usePanFollowingPointer(canvasRef, panStart, stopPanning);

  const onMouseDown = (press: React.MouseEvent<HTMLDivElement>) => {
    if (press.button !== RIGHT_MOUSE_BUTTON) return;
    press.preventDefault();
    setPanStart({ x: press.clientX, y: press.clientY, left: canvasRef.current?.scrollLeft ?? 0, top: canvasRef.current?.scrollTop ?? 0 });
  };
  return { canvasRef, isPanning: panStart !== null, onMouseDown, onContextMenu: (press: React.MouseEvent) => press.preventDefault() };
}

export function StoryMapWorkspaceView({ file, failures }: StoryMapWorkspaceViewProps) {
  const { client, failure, status, edit, showInChat, dismissFailure } = useStoryMapPage(file, failures);
  const chat = failures.chat;
  const { viewMode, toggleViewMode, scoped, toggleScoped, showScenarios, expandedNodeIds, toggleShowScenarios, expandNode, collapseNode, expandDescendants, collapseAll } = useStoryMapViewState();
  const [theme, setTheme] = useState<ColorMode>(themeOnOpen);
  const panning = useCanvasPanning();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  if (!client) {
    return failure
      ? <div className="loading"><span className="status-dot error" />{failure}</div>
      : <div className="loading"><span className="status-dot pending" />Loading story map…</div>;
  }
  return <StoryMapCanvasView client={client} chat={chat} failure={failure} status={status} edit={edit} showInChat={showInChat} dismissFailure={dismissFailure} viewMode={viewMode} toggleViewMode={toggleViewMode} scoped={scoped} toggleScoped={toggleScoped} showScenarios={showScenarios} toggleShowScenarios={toggleShowScenarios} expandedNodeIds={expandedNodeIds} expandNode={expandNode} collapseNode={collapseNode} expandDescendants={expandDescendants} collapseAll={collapseAll} theme={theme} setTheme={setTheme} panning={panning} />;
}

type StoryMapCanvasProps = Omit<ReturnType<typeof useStoryMapPage>, 'client'> & Pick<ReturnType<typeof useStoryMapViewState>, 'viewMode' | 'toggleViewMode' | 'scoped' | 'toggleScoped' | 'showScenarios' | 'toggleShowScenarios' | 'expandedNodeIds' | 'expandNode' | 'collapseNode' | 'expandDescendants' | 'collapseAll'> & {
  client: StoryMapClient;
  chat: string;
  theme: ColorMode;
  setTheme: (theme: ColorMode) => void;
  panning: ReturnType<typeof useCanvasPanning>;
};

type StoryMapToolbarProps = Pick<StoryMapCanvasProps, 'edit' | 'viewMode' | 'toggleViewMode' | 'scoped' | 'toggleScoped' | 'showScenarios' | 'toggleShowScenarios' | 'expandDescendants' | 'collapseAll' | 'theme' | 'setTheme'> & {
  map: StoryMapClient;
  epics: EpicOnPage[];
};

function StoryMapToolbar({ map, epics, edit, viewMode, toggleViewMode, scoped, toggleScoped, showScenarios, toggleShowScenarios, expandDescendants, collapseAll, theme, setTheme }: StoryMapToolbarProps) {
  const everyNode = () => epics.flatMap((epic) => [epic.id, ...epic.subEpics.flatMap((sub) => [sub.id, ...sub.stories.map((story) => story.id)])]);
  return (
    <div className="workspace-toolbar">
      <img className="brand-logo" src={`${import.meta.env.BASE_URL}${theme === 'engineering' ? 'logo-wordmark-white.svg' : 'logo-wordmark-black.svg'}`} alt="abd.works" />
      <span className="toolbar-file" title={map.file}>{map.file}</span>
      <span className="toolbar-sep" />
      <button className={`toolbar-btn${showScenarios ? ' active' : ''}`} onClick={toggleShowScenarios}>Show Scenarios</button>
      <button className={`toolbar-btn${viewMode === 'increment' ? ' active' : ''}`} aria-pressed={viewMode === 'increment'} onClick={toggleViewMode}>Increments</button>
      {map.scope.length > 0 && (
        <button className={`toolbar-btn${scoped ? ' active' : ''}`} aria-pressed={scoped} onClick={toggleScoped} title="The stories the ticket's session names">Ticket scope</button>
      )}
      <span className="toolbar-sep" />
      <button className="toolbar-btn" onClick={() => expandDescendants('all-epics', everyNode())}>Expand All</button>
      <button className="toolbar-btn" onClick={collapseAll}>Collapse All</button>
      <span className="toolbar-sep" />
      <FormatTogglesView map={map} onToggle={(format, isChosen) => void edit(() => map.chooseFormat(format, isChosen))} />
      <div className="mode-switch" role="group" aria-label="Color mode">
        <button type="button" className={theme === 'executive' ? 'active' : ''} aria-pressed={theme === 'executive'} onClick={() => setTheme('executive')}>Executive</button>
        <button type="button" className={theme === 'engineering' ? 'active' : ''} aria-pressed={theme === 'engineering'} onClick={() => setTheme('engineering')}>Engineering</button>
      </div>
    </div>
  );
}

function SaveStatusView({ status, map }: { status: EditStatus; map: StoryMapClient }) {
  return (
    <div className="status-rail">
      {status === 'synced' && <span><span className="status-dot" />saved in {map.formats.chosen_formats.join(' and ')}</span>}
      {status === 'saving' && <span><span className="status-dot pending" />saving…</span>}
      {status === 'error' && <span><span className="status-dot error" />not saved</span>}
    </div>
  );
}

function StoryMapCanvasView(props: StoryMapCanvasProps) {
  const { client, chat, failure, status, edit, showInChat, dismissFailure, viewMode, showScenarios, expandedNodeIds, expandNode, collapseNode, expandDescendants, panning } = props;
  const map = useStoryMap(client);
  // The epics are made once from each answer the map holds; reading them again draws the same nodes.
  const epics = map.epicsShown(props.scoped);
  const handleExpand = (id: string, descendants: string[]) => (expandedNodeIds.has(id) ? collapseNode(id) : expandDescendants(id, descendants));

  return (
    <main className="story-map-workspace">
      <StoryMapToolbar {...props} map={map} epics={epics} />
      {failure && (
        <div className="edit-failure" role="alert">
          <span className="status-dot error" />{failure}
          <button type="button" className="toolbar-btn" onClick={dismissFailure}>Dismiss</button>
        </div>
      )}
      {map.refusal && <div className="edit-refusal" role="note">Read only: {map.refusal}</div>}
      <div ref={panning.canvasRef} className="story-map-canvas" style={{ cursor: panning.isPanning ? 'grabbing' : 'grab' }} onMouseDown={panning.onMouseDown} onContextMenu={panning.onContextMenu}>
        <StoryHierarchyView map={map} epics={epics} expandedNodeIds={expandedNodeIds} showScenarios={showScenarios} showIncrements={viewMode === 'increment'} onNodeClick={expandNode} onExpand={handleExpand} edit={(change) => void edit(change)} onOpenFile={chat ? showInChat : undefined} />
      </div>
      <SaveStatusView status={status} map={map} />
    </main>
  );
}
