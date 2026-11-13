// The Story UI editor's views: the story map as epics, sub-epics, stories and scenarios, edited in place. The views
// draw what the Python story model sends (StoryMapClient over the generated StoryModel client) and hand every edit to
// that client, which saves it through the node's own tool; nothing here holds a story map of its own.

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useStoryModel } from '@cdd/practices/stories/model/story-model-views';

import { StoryMapApi } from './story-map-api';
import { StoryMapClient, type NodeKind } from './story-map-client';
import {
  StoryMapViewModel,
  type EpicViewModel,
  type ExampleTable,
  type IncrementViewModel,
  type ScenarioViewModel,
  type SemanticType,
  type StepRowDto,
  type StoryViewModel,
  type SubEpicViewModel,
} from './story-map-view-models';

// The page reads its map again this often, so an edit the agent made through the tools shows without a reload, and a
// page following the open session shows the ticket activated last.
const READ_EVERY_MILLISECONDS = 2_000;

type EditStatus = 'synced' | 'saving' | 'error';

// The story map a page shows: the file its link names, else the story map of the session open in the project.
export function useStoryMapPage(file: string | null) {
  const [failure, setFailure] = useState<string | null>(null);
  const api = useMemo(() => new StoryMapApi(setFailure), []);
  const [client, setClient] = useState<StoryMapClient | null>(null);
  const [status, setStatus] = useState<EditStatus>('synced');
  const editing = useRef(false);

  useEffect(() => {
    let stopped = false;
    let held: StoryMapClient | null = null;
    const read = async () => {
      if (editing.current) return;
      const next = file ? await (held ?? new StoryMapClient(api, null, file)).show() : await StoryMapClient.inOpenSession(api);
      if (stopped || !next) return;
      if (held && held.file === next.file) {
        if (next !== held) held.takeOn(next);
        return;
      }
      held = next;
      setClient(next);
    };
    void read();
    const timer = setInterval(() => void read(), READ_EVERY_MILLISECONDS);
    return () => {
      stopped = true;
      clearInterval(timer);
    };
  }, [api, file]);

  // An edit answers the map as its file now holds it; one that fails leaves the map as it was and says why.
  const edit = useCallback(async (change: (held: StoryMapClient) => Promise<StoryMapClient | null>) => {
    if (!client) return;
    editing.current = true;
    setStatus('saving');
    const answered = await change(client);
    editing.current = false;
    setStatus(answered ? 'synced' : 'error');
  }, [client]);

  return { client, failure, status, edit, dismissFailure: () => setFailure(null) };
}

// ---------------------------------------------------------------------------
// useStoryMapViewState — toggles and expansion state
// ---------------------------------------------------------------------------

export function useStoryMapViewState() {
  const [viewMode, setViewMode] = useState<'map' | 'increment'>('map');
  const [showScenarios, setShowScenarios] = useState(false);
  // A map opened on a ticket shows the part its session covers until the person asks for the whole map.
  const [scoped, setScoped] = useState(true);
  const [expandedNodeIds, setExpandedNodeIds] = useState<ReadonlySet<string>>(new Set());

  const toggleViewMode = useCallback(() => setViewMode((m) => (m === 'map' ? 'increment' : 'map')), []);

  const expandNode = useCallback((id: string) => {
    setExpandedNodeIds((prev) => new Set([...prev, id]));
  }, []);

  const collapseNode = useCallback((id: string) => {
    setExpandedNodeIds((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  }, []);

  const expandDescendants = useCallback((nodeId: string, descendantIds: string[]) => {
    setExpandedNodeIds((prev) => new Set([...prev, nodeId, ...descendantIds]));
  }, []);

  const collapseAll = useCallback(() => setExpandedNodeIds(new Set()), []);

  return {
    viewMode,
    showScenarios,
    scoped,
    expandedNodeIds,
    toggleViewMode,
    toggleShowScenarios: () => setShowScenarios((v) => !v),
    toggleScoped: () => setScoped((v) => !v),
    expandNode,
    collapseNode,
    expandDescendants,
    collapseAll,
  };
}

// ---------------------------------------------------------------------------
// Drag-to-reorder — shared, dependency-free HTML5 DnD wiring.
// A single ref per rendering scope tracks the dragged node id; makeDragHandlers
// is a plain function (not a hook) so it is safe to call from inside .map().
// ---------------------------------------------------------------------------

let titleMeasureCtx: CanvasRenderingContext2D | null = null;
function measureStoryTitleWidthPx(text: string): number {
  if (typeof document === 'undefined') return Math.max(8, text.length * 7);
  if (typeof navigator !== 'undefined' && /jsdom/i.test(navigator.userAgent)) {
    return Math.max(8, Math.ceil((text || ' ').length * 7));
  }
  if (!titleMeasureCtx) {
    const canvas = document.createElement('canvas');
    titleMeasureCtx = canvas.getContext('2d');
  }
  if (!titleMeasureCtx) return Math.max(8, text.length * 7);
  titleMeasureCtx.font = '500 13px Inter, system-ui, sans-serif';
  return Math.max(8, Math.ceil(titleMeasureCtx.measureText(text || ' ').width));
}

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
function suppressNativeDragImage(e: React.DragEvent<Element>) {
  try {
    if (!emptyDragImage) {
      emptyDragImage = new Image();
      emptyDragImage.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBTAA7';
    }
    e.dataTransfer?.setDragImage(emptyDragImage, 0, 0);
  } catch { /* jsdom / unsupported browsers just keep the native ghost */ }
}

function useDragVisuals(): DragVisualControls {
  const [dragState, setDragState] = useState<DragState | null>(null);
  const [dropEdge, setDropEdge] = useState<DropEdge | null>(null);
  const dropEdgeRef = useRef<DropEdge | null>(null);
  const writeEdge = (next: DropEdge | null) => { dropEdgeRef.current = next; setDropEdge(next); };
  return {
    start: (kind, id, originListKey) => {
      // Deferred to the next task on purpose: restyling the drag SOURCE from inside its
      // own dragstart handler (here `.being-dragged`, which also sets pointer-events:none)
      // makes Chrome abort the native drag outright — no dragover, no drop, nothing moves.
      // Synthetic dispatchEvent-driven tests never hit this, only a real mouse does.
      setTimeout(() => {
        setDragState({ kind, id, originListKey });
        // Only seeds the "in place" edge — a dragover that already landed keeps its edge.
        if (dropEdgeRef.current === null) writeEdge({ listKey: originListKey, beforeId: id });
      }, 0);
    },
    end: () => { setDragState(null); writeEdge(null); },
    setEdge: (listKey, beforeId) => {
      const prev = dropEdgeRef.current;
      if (prev?.listKey === listKey && prev?.beforeId === beforeId) return;
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
function computeBeforeId(rect: { left: number; width: number }, clientX: number, ids: string[], targetId: string): string | null {
  const before = rect.width === 0 || clientX < rect.left + rect.width / 2;
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
function computeDisplayIds(
  realIds: string[],
  listKey: string,
  dragState: DragState | null,
  dropEdge: DropEdge | null,
  kind: DragKind,
): string[] {
  if (!dragState || dragState.kind !== kind) return realIds;
  const isTarget = dropEdge?.listKey === listKey;
  if (isTarget) {
    return insertBeforeId(realIds.filter((id) => id !== dragState.id), dragState.id, dropEdge!.beforeId);
  }
  if (dragState.originListKey === listKey && dropEdge) {
    return realIds.filter((id) => id !== dragState.id);
  }
  return realIds;
}

/** True while `id` is the node currently being dragged — the dashed/grayed "landing
 *  here" styling hook (see .being-dragged in workspace.css). */
function isBeingDragged(dragState: DragState | null, kind: DragKind, id: string): boolean {
  return dragState?.kind === kind && dragState.id === id;
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
function focusNameFieldOnDoubleClick(e: React.MouseEvent<Element>) {
  const field = e.currentTarget.querySelector<HTMLInputElement>('.node-label, .story-name-input, .increment-name-input');
  if (!field) return;
  field.focus();
  field.select();
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
      const rect = (e.currentTarget as Element).getBoundingClientRect();
      visuals.setEdge(subEpicId, computeBeforeId(rect, e.clientX, getTargetIds(), storyId));
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
      const rect = (e.currentTarget as Element).getBoundingClientRect();
      visuals.setEdge(epicId, computeBeforeId(rect, e.clientX, getTargetIds(), subEpicId));
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
      const rect = (e.currentTarget as Element).getBoundingClientRect();
      visuals.setEdge(EPIC_LIST_KEY, computeBeforeId(rect, e.clientX, getIds(), epicId));
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
function dropIndicatorClass(dropEdge: DropEdge | null, listKey: string, id: string): string {
  return dropEdge?.listKey === listKey && dropEdge.beforeId === id ? ' drop-indicator' : '';
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
  /** Column indices (1-based) that are narrow leading-plus slots, not card slots. */
  leadCols: Set<number>;
}

function computeColumnLayout(
  storyMap: StoryMapViewModel,
  dragState: DragState | null,
  dropEdge: DropEdge | null,
): ColumnLayout {
  const epicCols = new Map<string, { start: number; span: number }>();
  const subEpicCols = new Map<string, { start: number; span: number }>();
  const storyCol = new Map<string, number>();
  const leadCols = new Set<number>(); // no dedicated lead columns — all columns are card-width
  const subEpicsById = new Map(storyMap.epics.flatMap((e) => e.sub_epics.map((s) => [s.id, s] as const)));
  let col = 1;
  const displayEpicIds = computeDisplayIds(storyMap.epics.map((e) => e.id), EPIC_LIST_KEY, dragState, dropEdge, 'epic');
  for (const epicId of displayEpicIds) {
    const epic = storyMap.epics.find((e) => e.id === epicId)!;
    const epicStart = col;
    const displaySubIds = computeDisplayIds(epic.sub_epics.map((s) => s.id), epic.id, dragState, dropEdge, 'sub-epic');
    for (const subId of displaySubIds) {
      const sub = subEpicsById.get(subId)!;
      const subStart = col;
      const displayStoryIds = computeDisplayIds(sub.stories.map((s) => s.id), sub.id, dragState, dropEdge, 'story');
      if (displayStoryIds.length === 0) {
        // Reserve 2 card-width columns (not 1) — a single column is too narrow to
        // read the SubEpic's name alongside its drag handle + icon buttons.
        col += 2;
      } else {
        displayStoryIds.forEach((sid) => { storyCol.set(sid, col); col += 1; });
      }
      subEpicCols.set(sub.id, { start: subStart, span: col - subStart });
    }
    if (displaySubIds.length === 0) {
      col += 2; // same reasoning as above, one level up — empty Epics need room too
    }
    epicCols.set(epic.id, { start: epicStart, span: col - epicStart });
  }
  return { epicCols, subEpicCols, storyCol, totalCols: Math.max(1, col - 1), leadCols };
}

function colTemplate(totalCols: number, _leadCols: Set<number>): string {
  // Keep columns text-fit while allowing expansion states to grow the track when needed.
  return Array.from({ length: totalCols }, () => 'minmax(max-content, auto)').join(' ');
}

// ---------------------------------------------------------------------------
// StoryHierarchyView — Epic → SubEpic row → Spine + Increment rows
// ---------------------------------------------------------------------------

interface StoryHierarchyViewProps {
  storyMap: StoryMapViewModel;
  expandedNodeIds: ReadonlySet<string>;
  showScenarios: boolean;
  /** false = Map View (no increment rows, no assign combobox); true = Increment View */
  showIncrements?: boolean;
  onNodeClick: (id: string, semantic_type: SemanticType) => void;
  onExpand: (id: string, semantic_type: SemanticType, descendantIds: string[]) => void;
  onSaveInline: (nodeId: string, patch: { name?: string }) => void;
  onReorderEpics?: (epicOrders: string[]) => void;
  onReorderSubEpics?: (epicId: string, subEpicOrders: string[]) => void;
  onReorderStories?: (subEpicId: string, storyOrders: string[]) => void;
  /** Move a Story to a SubEpic — same-parent reorder or across to a different Epic's SubEpic. */
  onMoveStory?: (storyId: string, targetSubEpicId: string, storyOrders: string[]) => void;
  /** Move a SubEpic (and its Stories) to an Epic — same-parent reorder or across to a different Epic. */
  onMoveSubEpic?: (subEpicId: string, targetEpicId: string, subEpicOrders: string[]) => void;
  onReorderScenarios?: (storyId: string, scenarioOrders: string[]) => void;
  onReorderSteps?: (storyId: string, scenarioId: string, stepOrders: string[]) => void;
  onAssignToIncrement?: (storyId: string, incrementId: string) => void;
  onUnassignFromIncrement?: (storyId: string) => void;
  onAppendEpic?: (name?: string) => void;
  onRemoveEpic?: (epicId: string) => void;
  onAppendSubEpic?: (epicId: string, name?: string) => void;
  onRemoveSubEpic?: (epicId: string, subEpicId: string) => void;
  onAppendStory?: (subEpicId: string, name?: string) => void;
  onRemoveStory?: (subEpicId: string, storyId: string) => void;
  // Positional insert — leading-+ per group and card-level + buttons
  onInsertEpicAfter?: (afterEpicId: string, name?: string) => void;
  onPrependSubEpic?: (epicId: string, name?: string) => void;
  onInsertSubEpicAfter?: (epicId: string, afterSubEpicId: string, name?: string) => void;
  onPrependStory?: (subEpicId: string, name?: string) => void;
  onInsertStoryAfter?: (subEpicId: string, afterStoryId: string, name?: string) => void;
  onAppendIncrement?: () => void;
  onRemoveIncrement?: (incrementId: string) => void;
  onReorderIncrements?: (incrementOrders: string[]) => void;
  // Scenario / step / example CRUD
  onAppendScenario?: (storyId: string) => void;
  onRemoveScenario?: (storyId: string, scenarioId: string) => void;
  onAddStep?: (storyId: string, scenarioId: string) => void;
  onUpdateStep?: (storyId: string, scenarioId: string, stepId: string, values: Partial<Pick<StepRowDto, 'text' | 'step_type'>>) => void;
  onRemoveStep?: (storyId: string, scenarioId: string, stepId: string) => void;
  onEditExample?: (exampleId: string, field: string, value: string) => void;
  onRemoveExample?: (exampleId: string) => void;
  onEditDescription?: (nodeId: string, description: string) => void;
  // Opens an acceptance-test file in the chat bar's file viewer; none when no chat opened the page.
  onOpenFile?: (path: string) => void;
}

export function StoryHierarchyView({
  storyMap,
  expandedNodeIds,
  showScenarios,
  showIncrements = true,
  onNodeClick,
  onExpand,
  onSaveInline,
  onReorderEpics = () => {},
  onReorderSubEpics = () => {},
  onReorderStories = () => {},
  onMoveStory = () => {},
  onMoveSubEpic = () => {},
  onReorderScenarios = () => {},
  onReorderSteps = () => {},
  onAssignToIncrement = () => {},
  onUnassignFromIncrement = () => {},
  onAppendEpic = () => {},
  onRemoveEpic = () => {},
  onAppendSubEpic = () => {},
  onRemoveSubEpic = () => {},
  onAppendStory = () => {},
  onRemoveStory = () => {},
  onInsertEpicAfter = () => {},
  onPrependSubEpic = () => {},
  onInsertSubEpicAfter = () => {},
  onPrependStory = () => {},
  onInsertStoryAfter = () => {},
  onAppendIncrement = () => {},
  onRemoveIncrement = () => {},
  onReorderIncrements = () => {},
  onAppendScenario = () => {},
  onRemoveScenario = () => {},
  onAddStep = () => {},
  onUpdateStep = () => {},
  onRemoveStep = () => {},
  onEditExample = () => {},
  onRemoveExample = () => {},
  onEditDescription = () => {},
  onOpenFile,
}: StoryHierarchyViewProps) {
  const assignedStoryIds = new Set(storyMap.increments.flatMap((i) => i.stories));
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
  const { epicCols, subEpicCols, storyCol, totalCols, leadCols } = computeColumnLayout(storyMap, dragState, dropEdge);
  const gridCols = colTemplate(totalCols, leadCols);

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
  const getSubEpicStoryIds = (subEpicId: string) => {
    for (const e of storyMap.epics)
      for (const s of e.sub_epics)
        if (s.id === subEpicId) return s.stories.map((st) => st.id);
    return [];
  };
  const getEpicIds = () => storyMap.epics.map((e) => e.id);
  const getEpicSubEpicIds = (epicId: string) => storyMap.epics.find((e) => e.id === epicId)?.sub_epics.map((s) => s.id) ?? [];

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

  const renderStoryCard = (story: StoryViewModel, subEpicId: string, isFirst = false) => {
    const baseDrag = makeStoryDragHandlers(
      dragRef,
      dragKindRef,
      story.id,
      subEpicId,
      () => getSubEpicStoryIds(subEpicId),
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
        increments={storyMap.increments}
        isExpanded={expandedNodeIds.has(story.id)}
        showScenarios={showScenarios}
        showIncrements={showIncrements}
        onNodeClick={onNodeClick}
        onExpand={onExpand}
        onSaveInline={onSaveInline}
        onAssignToIncrement={onAssignToIncrement}
        onUnassignFromIncrement={onUnassignFromIncrement}
        onReorderScenarios={onReorderScenarios}
        onReorderSteps={onReorderSteps}
        onRemoveStory={(storyId) => onRemoveStory(subEpicId, storyId)}
        onAppendStory={(name) => onInsertStoryAfter(subEpicId, story.id, name)}
        onPrepend={isFirst ? (name) => onPrependStory(subEpicId, name) : undefined}
        onAppendScenario={onAppendScenario}
        onRemoveScenario={onRemoveScenario}
        onAddStep={onAddStep}
        onUpdateStep={onUpdateStep}
        onRemoveStep={onRemoveStep}
        onEditExample={onEditExample}
        onRemoveExample={onRemoveExample}
        onEditDescription={onEditDescription}
        onOpenFile={onOpenFile}
        dragHandlers={dragHandlers}
        dropIndicatorClass={
          dropIndicatorClass(dropEdge, subEpicId, story.id) +
          (isBeingDragged(dragState, 'story', story.id) ? ' being-dragged' : '')
        }
      />
    );
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
      {storyMap.epics.length === 0
        ? <AddNodePopoverButton
            className="add-root-btn"
            title="Add Epic"
            buttonLabel="+ Epic"
            placeholder="Epic title (optional)"
            style={{ gridRow: ROW_EPICS, gridColumn: 1 }}
            onAdd={onAppendEpic}
          />
        : storyMap.epics.map((epic) => {
            const at = epicCols.get(epic.id)!;
            const epicDragHandlers = makeEpicDragHandlers(
              dragRef,
              dragKindRef,
              epic.id,
              () => storyMap.epics.map((e) => e.id),
              onReorderEpics,
              dragVisuals,
            );
            return (
              <div
                key={epic.id}
                className={`epic-lane${isBeingDragged(dragState, 'epic', epic.id) ? ' being-dragged' : ''}`}
                style={{ gridRow: ROW_EPICS, gridColumn: `${at.start} / span ${at.span}` }}
                onClick={() => onNodeClick(epic.id, 'epic')}
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
                      <button className="node-btn" title="Expand descendants" onClick={(e) => { e.stopPropagation(); onExpand(epic.id, 'epic', getAllDescendantStoryIds(epic)); }}>↕</button>
                      <AddNodePopoverButton
                        className="node-btn plus-btn"
                        title="Add Epic"
                        buttonLabel="+"
                        placeholder="Epic title (optional)"
                        onAdd={(name) => onInsertEpicAfter(epic.id, name)}
                      />
                      <button className="node-btn minus-btn" title="Delete Epic" onClick={(e) => { e.stopPropagation(); onRemoveEpic(epic.id); }}>−</button>
                    </span>
                  </div>
                </div>
                <NodeNameInput nodeId={epic.id} name={epic.name} onSaveInline={onSaveInline} className="node-label" />
                {expandedNodeIds.has(epic.id) && (
                  <DescriptionEditor key={epic.description} node={epic} onSave={(description) => onEditDescription(epic.id, description)} />
                )}
              </div>
            );
          })
      }

      {/* ── Row 2: SubEpic lanes ──────────────────────────────────────── */}
      {storyMap.epics.flatMap((epic) => {
        const epicAt = epicCols.get(epic.id)!;
        const displaySubEpicIds = computeDisplayIds(epic.sub_epics.map((s) => s.id), epic.id, dragState, dropEdge, 'sub-epic');
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
                onAdd={(name) => onPrependSubEpic(epic.id, name)}
              />
            </div>,
          ];
        }
        return epic.sub_epics.map((sub, subIdx) => {
          const at = subEpicCols.get(sub.id)!;
          const isFirst = subIdx === 0;
          const subEpicDragHandlers = makeSubEpicDragHandlers(
            dragRef,
            dragKindRef,
            sub.id,
            epic.id,
            () => epic.sub_epics.map((s) => s.id),
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
              onClick={() => onNodeClick(sub.id, 'sub-epic')}
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
                      onAdd={(name) => onPrependSubEpic(epic.id, name)}
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
                    <button className="node-btn" onClick={(e) => { e.stopPropagation(); onExpand(sub.id, 'sub-epic', sub.stories.map((s) => s.id)); }}>↕</button>
                    <AddNodePopoverButton
                      className="node-btn plus-btn"
                      title="Add SubEpic"
                      buttonLabel="+"
                      placeholder="SubEpic title (optional)"
                      onAdd={(name) => onInsertSubEpicAfter(epic.id, sub.id, name)}
                    />
                    <button className="node-btn minus-btn" title="Delete SubEpic" onClick={(e) => { e.stopPropagation(); onRemoveSubEpic(epic.id, sub.id); }}>−</button>
                  </span>
                </div>
              </div>
              <NodeNameInput nodeId={sub.id} name={sub.name} onSaveInline={onSaveInline} className="node-label" />
              {/* An epic's own stories show as a row named for the epic, whose description the epic's lane edits. */}
              {sub.id !== epic.id && expandedNodeIds.has(sub.id) && (
                <DescriptionEditor key={sub.description} node={sub} onSave={(description) => onEditDescription(sub.id, description)} />
              )}
            </div>
          );
        });
      })}

      {/* ── Row 3: Spine (unassigned) story cards ────────────────────── */}
      {storyMap.epics.flatMap((epic) =>
        epic.sub_epics.flatMap((sub) => {
          const subAt = subEpicCols.get(sub.id)!;
          const displayStoryIds = computeDisplayIds(sub.stories.map((s) => s.id), sub.id, dragState, dropEdge, 'story');
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
                  onAdd={(name) => onPrependStory(sub.id, name)}
                />
              </div>,
            ];
          }
          return sub.stories
            // Increment-assigned Stories only move down to an Increment row once
            // Increment View is actually rendering one for them — otherwise they'd
            // vanish entirely, leaving a phantom reserved column in this SubEpic.
            .filter((s) => !showIncrements || !assignedStoryIds.has(s.id))
            .map((story, storyIdx) => (
              <div key={story.id} data-row-type="spine" style={{ gridRow: ROW_SPINE, gridColumn: storyCol.get(story.id) }}>
                {renderStoryCard(story, sub.id, storyIdx === 0)}
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
            const sid = storyDragRef.current ?? e.dataTransfer?.getData('text/plain') ?? null;
            storyDragRef.current = null;
            // This is an increment (un)assignment, not a parent move — cancel the
            // cross-parent drag so the container's dragend fallback doesn't also fire.
            dragRef.current = null; dragKindRef.current = null; dragVisuals.end();
            if (sid) onUnassignFromIncrement(sid);
          }}
        >
          ↑ Unassigned — drop here to remove from increment
        </div>
      )}

      {/* ── Rows 5+: Increment rows (label + cards) ──────────────────── */}
      {showIncrements && storyMap.increments.map((inc, incIdx) => {
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
                const sid = storyDragRef.current ?? e.dataTransfer?.getData('text/plain') ?? null;
                storyDragRef.current = null;
                dragRef.current = null; dragKindRef.current = null; dragVisuals.end();
                if (sid) onAssignToIncrement(sid, inc.id);
              }}
            >
              <IncrementLabel
                increment={inc}
                onSaveInline={onSaveInline}
                onRemoveIncrement={onRemoveIncrement}
                dragHandlers={makeDragHandlers(incDragRef, inc.id, () => storyMap.increments.map((i) => i.id), onReorderIncrements)}
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
                const sid = storyDragRef.current ?? e.dataTransfer?.getData('text/plain') ?? null;
                storyDragRef.current = null;
                dragRef.current = null; dragKindRef.current = null; dragVisuals.end();
                if (sid) onAssignToIncrement(sid, inc.id);
              }}
            />
            {/* Increment story cards — placed at their story column positions */}
            {storyMap.epics.flatMap((epic) =>
              epic.sub_epics.flatMap((sub) => {
                const filtered = sub.stories.filter((s) => inc.stories.includes(s.id));
                return filtered.map((story, storyIdx) => (
                  <div key={story.id} data-row-type={`increment-${inc.id}`} style={{ gridRow: cardsRow, gridColumn: storyCol.get(story.id) }}>
                    {renderStoryCard(story, sub.id, storyIdx === 0)}
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
          style={{ gridRow: incAddRow(storyMap.increments.length), gridColumn: 1 }}
          onClick={onAppendIncrement}
        >+ Increment</button>
      )}
    </div>
  );
}

function getAllDescendantStoryIds(epic: EpicViewModel): string[] {
  return epic.sub_epics.flatMap((sub) => sub.stories.map((s) => s.id));
}

// ---------------------------------------------------------------------------
// NodeNameInput — shared inline-rename control for Epic/SubEpic lane labels;
// commits via the same StoryNodeBase.translateFrom PATCH /nodes/:nodeId path
// Story cards already use (on-double-click-name -> inline rename -> Save Inline).
// ---------------------------------------------------------------------------

function NodeNameInput({
  nodeId,
  name,
  onSaveInline,
  className,
}: {
  nodeId: string;
  name: string;
  onSaveInline: (nodeId: string, patch: { name?: string }) => void;
  className: string;
}) {
  const [editName, setEditName] = useState(name);
  const save = () => { if (editName !== name) onSaveInline(nodeId, { name: editName }); };
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
          if (e.key === 'Escape') { e.stopPropagation(); setEditName(name); }
        }}
        onBlur={save}
      />
    </>
  );
}

// ---------------------------------------------------------------------------
// IncrementLabel — inline-editable Increment name (rename via the same
// StoryNodeBase.translateFrom PATCH /nodes/:nodeId path Stories use) + delete
// ---------------------------------------------------------------------------

function IncrementLabel({
  increment,
  onSaveInline,
  onRemoveIncrement,
  dragHandlers,
}: {
  increment: IncrementViewModel;
  onSaveInline: (nodeId: string, patch: { name?: string }) => void;
  onRemoveIncrement: (incrementId: string) => void;
  dragHandlers: ReturnType<typeof makeDragHandlers>;
}) {
  const [editName, setEditName] = useState(increment.name);
  const save = () => { if (editName !== increment.name) onSaveInline(increment.id, { name: editName }); };
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
      <button className="node-btn minus-btn" title="Delete Increment" onClick={() => onRemoveIncrement(increment.id)}>−</button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// StoryCard — collapsed or inline-expanded
// ---------------------------------------------------------------------------

interface StoryCardProps {
  story: StoryViewModel;
  increments: IncrementViewModel[];
  isExpanded: boolean;
  showScenarios: boolean;
  /** When false (Map View) the increment assign combobox is hidden */
  showIncrements: boolean;
  onNodeClick: (id: string, semantic_type: SemanticType) => void;
  onExpand: (id: string, semantic_type: SemanticType, descendantIds: string[]) => void;
  onSaveInline: (nodeId: string, patch: { name?: string }) => void;
  onAssignToIncrement: (storyId: string, incrementId: string) => void;
  onUnassignFromIncrement: (storyId: string) => void;
  onReorderScenarios: (storyId: string, scenarioOrders: string[]) => void;
  onReorderSteps: (storyId: string, scenarioId: string, stepOrders: string[]) => void;
  onRemoveStory: (storyId: string) => void;
  onAppendStory: (name?: string) => void;
  /** When provided, renders a prepend-sibling + button as the very first element
   * in the card header (only supplied for the first story in each sub-epic group). */
  onPrepend?: (name?: string) => void;
  dragHandlers: ReturnType<typeof makeStoryDragHandlers>;
  /** Extra className applied to the outer card — shows the "insert before" drop-position indicator. */
  dropIndicatorClass?: string;
  // Scenario / step / example CRUD
  onAppendScenario: (storyId: string) => void;
  onRemoveScenario: (storyId: string, scenarioId: string) => void;
  onAddStep: (storyId: string, scenarioId: string) => void;
  onUpdateStep: (storyId: string, scenarioId: string, stepId: string, values: Partial<Pick<StepRowDto, 'text' | 'step_type'>>) => void;
  onRemoveStep: (storyId: string, scenarioId: string, stepId: string) => void;
  onEditExample: (exampleId: string, field: string, value: string) => void;
  onRemoveExample: (exampleId: string) => void;
  onEditDescription: (nodeId: string, description: string) => void;
  onOpenFile?: (path: string) => void;
}

function StoryCard({
  story,
  increments,
  isExpanded,
  showScenarios: _showScenarios,
  showIncrements,
  onNodeClick,
  onExpand,
  onSaveInline,
  onAssignToIncrement,
  onUnassignFromIncrement,
  onReorderScenarios,
  onReorderSteps,
  onRemoveStory,
  onAppendStory,
  onPrepend,
  dragHandlers,
  dropIndicatorClass = '',
  onAppendScenario,
  onRemoveScenario,
  onAddStep,
  onUpdateStep,
  onRemoveStep,
  onEditExample,
  onRemoveExample,
  onEditDescription,
  onOpenFile,
}: StoryCardProps) {
  const [editName, setEditName] = useState(story.name);
  const scenarioDragRef = useRef<string | null>(null);
  const {
    draggable: storyDraggable,
    onDragStart: storyOnDragStart,
    onDragEnd: storyOnDragEnd,
  } = dragHandlers;

  const saveName = () => { if (editName !== story.name) onSaveInline(story.id, { name: editName }); };

  return (
    <div className={`story-card${isExpanded ? ' expanded' : ''}${dropIndicatorClass}`} {...dragHandlers}>
      <div className="story-card-header" onClick={() => onNodeClick(story.id, 'story')} onDoubleClick={focusNameFieldOnDoubleClick}>
        <div className="type-label-row">
          <div className="type-label-left">
            {onPrepend && (
              <AddNodePopoverButton
                className="node-btn plus-btn row-lead-plus"
                title="Add Story at beginning"
                buttonLabel="+"
                placeholder="Story title (optional)"
                onAdd={onPrepend}
              />
            )}
            <span
              className="drag-handle"
              aria-hidden="true"
              draggable={storyDraggable}
              onDragStart={(e) => { e.stopPropagation(); storyOnDragStart(e); }}
              onDragEnd={() => { storyOnDragEnd(); }}
            >
              ⠿
            </span>
          </div>
          <div className="type-label-center">
            <span className="type-label">STORY</span>
          </div>
          <div className="type-label-right">
            <span className="node-actions">
              <button className="expand-btn" title="Expand story" onClick={(e) => { e.stopPropagation(); onExpand(story.id, 'story', []); }}>
                {isExpanded ? '▲' : '▼'}
              </button>
              <AddNodePopoverButton
                className="node-btn plus-btn"
                title="Add Story"
                buttonLabel="+"
                placeholder="Story title (optional)"
                onAdd={onAppendStory}
              />
              <button className="node-btn minus-btn" title="Delete Story" onClick={(e) => { e.stopPropagation(); onRemoveStory(story.id); }}>−</button>
            </span>
          </div>
        </div>
        <div
          className="story-name-input"
          contentEditable={true}
          suppressContentEditableWarning={true}
          onInput={(e) => setEditName(e.currentTarget.textContent || '')}
          onDoubleClick={(e) => { e.stopPropagation(); e.currentTarget.focus(); document.execCommand('selectAll', false, undefined); }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); e.stopPropagation(); saveName(); }
            if (e.key === 'Escape') { setEditName(story.name); e.currentTarget.blur(); }
          }}
          onBlur={saveName}
          onClick={(e) => e.stopPropagation()}
        >{editName}</div>
      </div>

      {/* Expansion panel — always visible when expanded, regardless of Show Scenarios toggle */}
      {isExpanded && (
        <div className="story-expansion-panel">
          <DescriptionEditor key={story.description} node={story} onSave={(description) => onEditDescription(story.id, description)} />
          <AcceptanceTestsView files={story.acceptance_tests} onOpen={onOpenFile} />
          <div className="section-heading">
            <span>Scenarios</span>
            <button className="node-btn plus-btn" title="Add Scenario" onClick={() => onAppendScenario(story.id)}>+</button>
          </div>
          {story.scenarios.map((sc) => (
            <div
              key={sc.id}
              className="scenario-row-drag"
              {...makeDragHandlers(scenarioDragRef, sc.id, () => story.scenarios.map((s) => s.id), (ids) => onReorderScenarios(story.id, ids))}
            >
              <ScenarioPanel
                scenario={sc}
                storyId={story.id}
                onSaveInline={onSaveInline}
                onReorderSteps={onReorderSteps}
                onRemoveScenario={() => onRemoveScenario(story.id, sc.id)}
                onAddStep={() => onAddStep(story.id, sc.id)}
                onUpdateStep={(stepId, values) => onUpdateStep(story.id, sc.id, stepId, values)}
                onRemoveStep={(stepId) => onRemoveStep(story.id, sc.id, stepId)}
                onEditExample={onEditExample}
                onRemoveExample={onRemoveExample}
              />
            </div>
          ))}
        </div>
      )}
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

function ScenarioPanel({
  scenario,
  storyId,
  onSaveInline,
  onReorderSteps,
  onRemoveScenario,
  onAddStep,
  onUpdateStep,
  onRemoveStep,
  onEditExample,
  onRemoveExample,
}: {
  scenario: ScenarioViewModel;
  storyId: string;
  onSaveInline: (nodeId: string, patch: { name?: string }) => void;
  onReorderSteps: (storyId: string, scenarioId: string, stepOrders: string[]) => void;
  onRemoveScenario: () => void;
  onAddStep: () => void;
  onUpdateStep: (stepId: string, values: Partial<Pick<StepRowDto, 'text' | 'step_type'>>) => void;
  onRemoveStep: (stepId: string) => void;
  onEditExample: (exampleId: string, field: string, value: string) => void;
  onRemoveExample: (exampleId: string) => void;
}) {
  const stepDragRef = useRef<string | null>(null);
  const [scenarioName, setScenarioName] = useState(scenario.name);
  const saveScenarioName = () => { if (scenarioName !== scenario.name) onSaveInline(scenario.id, { name: scenarioName }); };

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
        <button className="node-btn minus-btn" title="Delete Scenario" onClick={onRemoveScenario}>−</button>
      </div>

      <div className="steps-section">
        <div className="section-heading indent">
          <span>Steps</span>
          <button className="node-btn plus-btn" title="Add Step" onClick={onAddStep}>+</button>
        </div>
        <ol className="step-list">
          {scenario.steps.map((step) => (
            <li
              key={step.id}
              className="step-row"
              {...makeDragHandlers(stepDragRef, step.id, () => scenario.steps.map((s) => s.id), (ids) => onReorderSteps(storyId, scenario.id, ids))}
            >
              <span className="drag-handle" aria-hidden="true">⠿</span>
              <StepEditor key={`${step.id}-${step.step_type}-${step.text}`} step={step} onUpdate={(values) => onUpdateStep(step.id, values)} />
              <button className="node-btn minus-btn" title="Delete Step" onClick={() => onRemoveStep(step.id)}>−</button>
            </li>
          ))}
        </ol>
      </div>

      <ExampleTableView examples={scenario.examples} onEdit={onEditExample} onRemove={onRemoveExample} />
    </div>
  );
}

// ---------------------------------------------------------------------------
// StepEditor — inline-editable step (type selector + text)
// ---------------------------------------------------------------------------
const STEP_TYPES: StepRowDto['step_type'][] = ['given', 'when', 'then', 'and', 'but'];

function StepEditor({
  step,
  onUpdate,
}: {
  step: { step_type: StepRowDto['step_type']; text: string };
  onUpdate: (values: Partial<Pick<StepRowDto, 'text' | 'step_type'>>) => void;
}) {
  const [text, setText] = useState(step.text);
  const [type, setType] = useState<StepRowDto['step_type']>(step.step_type);
  const save = () => {
    const changed: Partial<Pick<StepRowDto, 'text' | 'step_type'>> = {};
    if (text !== step.text) changed.text = text;
    if (type !== step.step_type) changed.step_type = type;
    if (Object.keys(changed).length > 0) onUpdate(changed);
  };
  return (
    <span className="step-editor">
      <select
        className="step-type-select"
        value={type}
        onChange={(e) => { setType(e.target.value as StepRowDto['step_type']); }}
        onBlur={save}
      >
        {STEP_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
      </select>
      <input
        className="step-text-input"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === 'Tab') { e.preventDefault(); save(); } if (e.key === 'Escape') { setText(step.text); setType(step.step_type); } }}
        onBlur={save}
      />
    </span>
  );
}

// A scenario's examples as the story model holds them: a row per example. Each cell its row has is edited through that
// example's edit_field when it changes; a column only other rows have stays empty and read only.
function ExampleTableView({ examples, onEdit, onRemove }: { examples: ExampleTable; onEdit: (exampleId: string, field: string, value: string) => void; onRemove: (exampleId: string) => void }) {
  if (!examples.rows.length) return null;
  return (
    <div className="examples-section">
      <div className="section-heading indent"><span>Examples</span></div>
      <div className="example-block">
      <table>
        <thead>
          <tr>{examples.columns.map((column) => <th key={column}>{column}</th>)}<th aria-label="Remove" /></tr>
        </thead>
        <tbody>
          {examples.rows.map((row) => (
            <tr key={row.id}>
              {examples.columns.map((column) => (
                <td key={column}>
                  {column in row.fields
                    ? <ExampleCellEditor key={`${row.id}-${row.fields[column]}`} label={`${column} of ${row.fields.example}`} value={row.fields[column]!} onSave={(value) => onEdit(row.id, column, value)} />
                    : null}
                </td>
              ))}
              <td><button className="node-btn minus-btn" title="Delete Example" onClick={() => onRemove(row.id)}>−</button></td>
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
function DescriptionEditor({ node, onSave }: { node: { name: string; description: string }; onSave: (description: string) => void }) {
  const [text, setText] = useState(node.description);
  const save = () => { if (text.trim() !== node.description) onSave(text); };
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
  // The chat the page was opened beside, from its ?chat= link, whose file viewer shows a story's acceptance tests;
  // empty for a page no chat opened.
  chat?: string;
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

// Right-drag pans the canvas, even when the pointer leaves it.
function useCanvasPanning() {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [panStart, setPanStart] = useState<{ x: number; y: number; left: number; top: number } | null>(null);

  useEffect(() => {
    if (!panStart) return undefined;
    const move = (e: MouseEvent) => {
      if (!canvasRef.current) return;
      canvasRef.current.scrollLeft = panStart.left - (e.clientX - panStart.x);
      canvasRef.current.scrollTop = panStart.top - (e.clientY - panStart.y);
    };
    const up = () => setPanStart(null);
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
    return () => {
      window.removeEventListener('mousemove', move);
      window.removeEventListener('mouseup', up);
    };
  }, [panStart]);

  const onMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.button !== 2) return;
    e.preventDefault();
    setPanStart({ x: e.clientX, y: e.clientY, left: canvasRef.current?.scrollLeft ?? 0, top: canvasRef.current?.scrollTop ?? 0 });
  };
  return { canvasRef, isPanning: panStart !== null, onMouseDown, onContextMenu: (e: React.MouseEvent) => e.preventDefault() };
}

export function StoryMapWorkspaceView({ file, chat = '' }: StoryMapWorkspaceViewProps) {
  const { client, failure, status, edit, dismissFailure } = useStoryMapPage(file);
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
  return <StoryMapCanvasView client={client} chat={chat} failure={failure} status={status} edit={edit} dismissFailure={dismissFailure} viewMode={viewMode} toggleViewMode={toggleViewMode} scoped={scoped} toggleScoped={toggleScoped} showScenarios={showScenarios} toggleShowScenarios={toggleShowScenarios} expandedNodeIds={expandedNodeIds} expandNode={expandNode} collapseNode={collapseNode} expandDescendants={expandDescendants} collapseAll={collapseAll} theme={theme} setTheme={setTheme} panning={panning} />;
}

type StoryMapCanvasProps = Omit<ReturnType<typeof useStoryMapPage>, 'client'> & Pick<ReturnType<typeof useStoryMapViewState>, 'viewMode' | 'toggleViewMode' | 'scoped' | 'toggleScoped' | 'showScenarios' | 'toggleShowScenarios' | 'expandedNodeIds' | 'expandNode' | 'collapseNode' | 'expandDescendants' | 'collapseAll'> & {
  client: StoryMapClient;
  chat: string;
  theme: ColorMode;
  setTheme: (theme: ColorMode) => void;
  panning: ReturnType<typeof useCanvasPanning>;
};

function StoryMapCanvasView({ client, chat, failure, status, edit, dismissFailure, viewMode, toggleViewMode, scoped, toggleScoped, showScenarios, toggleShowScenarios, expandedNodeIds, expandNode, collapseNode, expandDescendants, collapseAll, theme, setTheme, panning }: StoryMapCanvasProps) {
  const map = useStoryModel(client);
  const storyMap = useMemo(() => StoryMapViewModel.of(map.toJSON(), scoped), [map, map.toJSON(), scoped]);
  const kindOf = (node: string): NodeKind => (storyMap.kinds.get(node) ?? 'epic') as NodeKind;
  const lastOf = <T extends { id: string }>(nodes: T[]): string | undefined => nodes[nodes.length - 1]?.id;
  const subEpicsOf = (epic: string) => storyMap.epics.find((each) => each.id === epic)?.sub_epics ?? [];
  const storiesOf = (sub: string) => storyMap.epics.flatMap((each) => each.sub_epics).find((each) => each.id === sub)?.stories ?? [];

  // A node added after another is added last, then moved before the one that followed the other.
  const addThenPlace = (add: (held: StoryMapClient) => Promise<StoryMapClient | null>, siblings: (read: StoryMapViewModel) => { id: string }[], after: string | null) => edit(async (held) => {
    const added = await add(held);
    if (!added) return null;
    const placed = siblings(StoryMapViewModel.of(added.toJSON()));
    const created = lastOf(placed);
    const next = after === null ? placed[0]?.id : placed[placed.findIndex((each) => each.id === after) + 1]?.id;
    return created && next && next !== created ? held.moveBeforeNode(created, kindOf(next) === 'story' ? 'story' : 'epic', next) : added;
  });

  const handleExpand = (id: string, _type: SemanticType, descendants: string[]) => {
    if (expandedNodeIds.has(id)) collapseNode(id);
    else expandDescendants(id, descendants);
  };

  return (
    <main className="story-map-workspace">
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
        <button className="toolbar-btn" onClick={() => expandDescendants('all-epics', storyMap.epics.flatMap((e) => [e.id, ...e.sub_epics.flatMap((s) => [s.id, ...s.stories.map((st) => st.id)])]))}>Expand All</button>
        <button className="toolbar-btn" onClick={collapseAll}>Collapse All</button>
        <span className="toolbar-sep" />
        <FormatTogglesView map={map} onToggle={(format, isChosen) => void edit((held) => held.chooseFormat(format, isChosen))} />
        <div className="mode-switch" role="group" aria-label="Color mode">
          <button type="button" className={theme === 'executive' ? 'active' : ''} aria-pressed={theme === 'executive'} onClick={() => setTheme('executive')}>Executive</button>
          <button type="button" className={theme === 'engineering' ? 'active' : ''} aria-pressed={theme === 'engineering'} onClick={() => setTheme('engineering')}>Engineering</button>
        </div>
      </div>

      {failure && (
        <div className="edit-failure" role="alert">
          <span className="status-dot error" />{failure}
          <button type="button" className="toolbar-btn" onClick={dismissFailure}>Dismiss</button>
        </div>
      )}
      {map.refusal && <div className="edit-refusal" role="note">Read only: {map.refusal}</div>}

      <div ref={panning.canvasRef} className="story-map-canvas" style={{ cursor: panning.isPanning ? 'grabbing' : 'grab' }} onMouseDown={panning.onMouseDown} onContextMenu={panning.onContextMenu}>
        <StoryHierarchyView
          storyMap={storyMap}
          expandedNodeIds={expandedNodeIds}
          showScenarios={showScenarios}
          showIncrements={viewMode === 'increment'}
          onNodeClick={expandNode}
          onExpand={handleExpand}
          onSaveInline={(nodeId, patch) => { if (patch.name) void edit((held) => held.renameNode(nodeId, kindOf(nodeId), patch.name!)); }}
          onReorderEpics={(order) => void edit((held) => held.reorder(storyMap.epics.map((e) => e.id), order, 'epic'))}
          onReorderSubEpics={(epic, order) => void edit((held) => held.reorder(subEpicsOf(epic).map((s) => s.id), order, 'sub-epic'))}
          onReorderStories={(sub, order) => void edit((held) => held.reorder(storiesOf(sub).map((s) => s.id), order, 'story'))}
          onMoveStory={(story, _sub, order) => { const next = order[order.indexOf(story) + 1]; if (next) void edit((held) => held.moveBeforeNode(story, 'story', next)); }}
          onMoveSubEpic={(sub, _epic, order) => { const next = order[order.indexOf(sub) + 1]; if (next) void edit((held) => held.moveBeforeNode(sub, 'sub-epic', next)); }}
          onReorderScenarios={(story, order) => void edit((held) => held.reorder(storyMap.epics.flatMap((e) => e.sub_epics.flatMap((s) => s.stories)).find((s) => s.id === story)?.scenarios.map((sc) => sc.id) ?? [], order, 'scenario'))}
          onAppendEpic={(name) => void edit((held) => held.newEpic(name?.trim() || NEW_NAMES.epic))}
          onRemoveEpic={(epic) => void edit((held) => held.removeNode(epic, 'epic'))}
          onAppendSubEpic={(epic, name) => void edit((held) => held.newSubEpic(epic, name?.trim() || NEW_NAMES.subEpic))}
          onRemoveSubEpic={(_epic, sub) => void edit((held) => held.removeNode(sub, 'sub-epic'))}
          onAppendStory={(sub, name) => void edit((held) => held.newStory(sub, name?.trim() || NEW_NAMES.story))}
          onRemoveStory={(_sub, story) => void edit((held) => held.removeNode(story, 'story'))}
          onInsertEpicAfter={(after, name) => void addThenPlace((held) => held.newEpic(name?.trim() || NEW_NAMES.epic), (read) => read.epics, after)}
          onPrependSubEpic={(epic, name) => void addThenPlace((held) => held.newSubEpic(epic, name?.trim() || NEW_NAMES.subEpic), (read) => read.epics.find((e) => e.id === epic)?.sub_epics ?? [], null)}
          onInsertSubEpicAfter={(epic, after, name) => void addThenPlace((held) => held.newSubEpic(epic, name?.trim() || NEW_NAMES.subEpic), (read) => read.epics.find((e) => e.id === epic)?.sub_epics ?? [], after)}
          onPrependStory={(sub, name) => void addThenPlace((held) => held.newStory(sub, name?.trim() || NEW_NAMES.story), (read) => read.epics.flatMap((e) => e.sub_epics).find((s) => s.id === sub)?.stories ?? [], null)}
          onInsertStoryAfter={(sub, after, name) => void addThenPlace((held) => held.newStory(sub, name?.trim() || NEW_NAMES.story), (read) => read.epics.flatMap((e) => e.sub_epics).find((s) => s.id === sub)?.stories ?? [], after)}
          onAppendScenario={(story) => void edit((held) => held.newScenario(story, NEW_NAMES.scenario))}
          onRemoveScenario={(_story, scenario) => void edit((held) => held.removeNode(scenario, 'scenario'))}
          onAddStep={(_story, scenario) => void edit((held) => held.newStep(scenario, 'given', NEW_NAMES.step))}
          onUpdateStep={(_story, _scenario, step, values) => { if (values.text !== undefined) void edit((held) => held.editStep(step, values.text!)); }}
          onRemoveStep={(_story, _scenario, step) => void edit((held) => held.removeNode(step, 'step'))}
          onEditExample={(example, field, value) => void edit((held) => held.editExample(example, field, value))}
          onRemoveExample={(example) => void edit((held) => held.removeExample(example))}
          onEditDescription={(node, description) => void edit((held) => held.describeNode(node, kindOf(node), description))}
          onOpenFile={chat ? (path) => void client.showInChat(chat, path) : undefined}
          onAppendIncrement={() => void edit((held) => held.newIncrement(NEW_NAMES.increment))}
          onRemoveIncrement={(increment) => void edit((held) => held.removeNode(increment, 'increment'))}
          onReorderIncrements={(order) => void edit((held) => held.reorder(storyMap.increments.map((each) => each.id), order, 'increment'))}
          onAssignToIncrement={(story, increment) => void edit((held) => held.deliverIn(increment, story))}
          onUnassignFromIncrement={(story) => { const increment = storyMap.incrementOf(story); if (increment) void edit((held) => held.stopDelivering(increment.id, story)); }}
        />
      </div>

      <div className="status-rail">
        {status === 'synced' && <span><span className="status-dot" />saved in {map.formats.chosen_formats.join(' and ')}</span>}
        {status === 'saving' && <span><span className="status-dot pending" />saving…</span>}
        {status === 'error' && <span><span className="status-dot error" />not saved</span>}
      </div>
    </main>
  );
}
