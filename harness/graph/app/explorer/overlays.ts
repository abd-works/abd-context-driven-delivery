import { useState, type Dispatch, type SetStateAction } from 'react';
import { graphs } from '../graph/graph-page';
import type { LoadStatus } from './load-status';
import type { PageFolder } from './page-folder';
import { normalizeInventoryBundle } from './inventory-bundle';
import { overlayPathLabel } from '../labels/overlay-labels';
import type { ExplorerFilter } from './explorer-filter';
import { chosen } from '../filter/filter-selection';
import type { FilterSelection } from '../filter/filter-selection';

const LAST_OVERLAYS = 'cdd-graph-overlays';

type Held<T> = [T, Dispatch<SetStateAction<T>>];

interface OverlaysState {
  available: Held<string[]>;
  applying: Held<boolean>;
  folder: PageFolder;
  status: LoadStatus;
}

// The pattern overlays a person applies to the graph loaded from a folder, and those the graph offers.
export class Overlays {
  constructor(
    private readonly state: OverlaysState,
    private readonly filter: ExplorerFilter,
  ) {}

  get available(): string[] {
    return this.state.available[0];
  }

  get applying(): boolean {
    return this.state.applying[0];
  }

  // The overlays the graph offers, as a load or a change of overlays answers them.
  offer(available: string[]): void {
    this.state.available[1](available);
  }

  // The overlays the graph applies, kept for the next visit.
  keep(applied: string[]): void {
    window.localStorage.setItem(LAST_OVERLAYS, JSON.stringify(applied));
  }

  async apply(overlays: string[]): Promise<void> {
    const next = { ...this.filter.selection, overlays };
    if (!this.state.folder.chosen) {
      this.filter.select(next);
      return;
    }
    this.state.applying[1](true);
    this.state.status.begin('Applying pattern overlays…');
    try {
      await this.showApplied(overlays, next);
    } catch (cause) {
      this.state.status.failed(cause, 'Applying pattern overlays in the Graph app');
    } finally {
      this.state.applying[1](false);
      this.state.status.end();
    }
  }

  async addFolder(): Promise<void> {
    try {
      const picked = await graphs.chooseOverlayFolder();
      if (picked.trim() && !this.filter.selection.overlays.includes(picked)) {
        await this.apply([...this.filter.selection.overlays, picked]);
      }
    } catch (cause) {
      this.state.status.failed(cause, 'Adding a pattern overlay folder in the Graph app');
    }
  }

  remove(overlay: string): void {
    void this.apply(this.filter.selection.overlays.filter((item) => item !== overlay));
  }

  addNamed(name: string): void {
    const overlays = this.filter.selection.overlays;
    if (!overlays.some((item) => overlayPathLabel(item) === name || item === name)) {
      void this.apply([...overlays, name]);
    }
  }

  private async showApplied(overlays: string[], next: FilterSelection): Promise<void> {
    const bundle = normalizeInventoryBundle(await graphs.setOverlays(overlays));
    this.offer(bundle.available_overlays ?? []);
    // The overlays change the node types the practices hold, so the node choice starts again from every one offered.
    const applied = { ...next, overlays: bundle.overlays?.length ? bundle.overlays : overlays, node_types: [] };
    await this.filter.show(chosen(applied, await this.filter.offerChoices(applied)));
    this.keep(bundle.overlays);
  }
}

export function useOverlays(filter: ExplorerFilter, folder: PageFolder, status: LoadStatus): Overlays {
  return new Overlays({ available: useState<string[]>([]), applying: useState(false), folder, status }, filter);
}

// The overlays a person last applied. Saved text that is not a list of overlays fails the load that reads it, which
// says so, instead of loading with none.
export function readSavedOverlays(): string[] {
  const raw = window.localStorage.getItem(LAST_OVERLAYS);
  if (!raw) {
    return [];
  }
  const parsed = JSON.parse(raw) as unknown;
  if (!Array.isArray(parsed)) {
    throw new Error(`The overlays saved in this browser (${LAST_OVERLAYS}) are not a list: ${raw}`);
  }
  return parsed.map(String);
}
