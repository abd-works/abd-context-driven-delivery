import { useEffect, useRef, useState, type MutableRefObject } from 'react';
import type { Held } from './held';
import type { FilterSelection } from '../filter/filter-selection';
import type { ExplorerFilter } from './explorer-filter';
import { readSavedOverlays, type Overlays } from './overlays';
import { normalizeInventoryBundle } from './inventory-bundle';
import { reasonOf } from '@cdd/cdd-page-failures';
import { api, failures, graphs } from '../graph/graph-page';
import type { LoadStatus } from './load-status';
import { openedFolder, type PageFolder } from './page-folder';

interface GraphLoadState {
  folder: PageFolder;
  status: LoadStatus;
  loadedFolder: Held<string>;
  practices: Held<string[]>;
  // The newest load, so a load overtaken by a later one shows nothing.
  generation: MutableRefObject<number>;
}

// Each load of the page's graph: from the folder the page names, or, for a page opened on a project, the graph of the
// session open there, loaded on its practice roots.
export class GraphLoad {
  constructor(
    private readonly state: GraphLoadState,
    private readonly filter: ExplorerFilter,
    private readonly overlays: Overlays,
  ) {}

  get loadedFolder(): string {
    return this.state.loadedFolder[0];
  }

  get practices(): string[] {
    return this.state.practices[0];
  }

  async load(root: string, force: boolean = false): Promise<void> {
    const trimmed = root.trim();
    if (!trimmed) {
      return;
    }
    const status = this.state.status;
    const generation = ++this.state.generation.current;
    status.begin();
    status.clearLog();
    try {
      await this.read(trimmed, force);
      if (generation === this.state.generation.current) await this.showLoaded(trimmed, generation);
    } catch (cause) {
      this.failed(cause, generation, trimmed);
    } finally {
      if (generation === this.state.generation.current) status.end();
    }
  }

  async browse(): Promise<void> {
    try {
      const chosen = await graphs.chooseFolder();
      if (chosen) {
        this.state.folder.choose(chosen);
        await this.load(chosen);
      }
    } catch (cause) {
      this.state.status.failed(cause, 'Choosing the session path in the Graph app');
    }
  }

  private failed(cause: unknown, generation: number, root: string): void {
    if (generation !== this.state.generation.current) {
      failures.fail(reasonOf(cause), `Loading the graph of ${root}, a load the page has since started again`);
      return;
    }
    this.state.status.failed(cause, `Loading the graph of ${root}`);
  }

  // The project's open session loads on the roots its practices name, and holds only the practices it works on; a chosen
  // folder loads every practice from that folder.
  private async read(root: string, force: boolean): Promise<void> {
    const names = (await graphs.practiceNames()) ?? [];
    this.state.practices[1](names);
    if (api.project) {
      await graphs.loadPracticeRoots();
      return;
    }
    await graphs.loadWorkingCopy(root, Object.fromEntries(names.map((name) => [name, root])), root, readSavedOverlays(), force);
  }

  // Show the graph a load read from root, with the overlays it applied, unless a later load started since.
  private async showLoaded(root: string, generation: number): Promise<void> {
    const bundle = normalizeInventoryBundle(await graphs.inventory());
    if (generation !== this.state.generation.current) {
      return;
    }
    const next: FilterSelection = this.filter.selection;
    const synced = { ...next, overlays: bundle.overlays?.length ? bundle.overlays : next.overlays };
    this.overlays.offer(bundle.available_overlays ?? []);
    await this.filter.offerChoices(synced);
    await this.filter.show(synced);
    this.state.loadedFolder[1](root);
    this.state.folder.remember(root);
    this.overlays.keep(bundle.overlays);
    this.state.status.clearLog();
  }
}

export function useGraphLoad(filter: ExplorerFilter, overlays: Overlays, status: LoadStatus): GraphLoad {
  const loader = new GraphLoad(
    { folder: filter.folder, status, loadedFolder: useState(''), practices: useState<string[]>([]), generation: useRef(0) },
    filter,
    overlays,
  );
  useEffect(() => {
    const saved = openedFolder().trim();
    if (saved) void loader.load(saved);
  }, []);
  useProjectReread(loader, status);
  return loader;
}

// The session open in the project can change while the page is open, as when the board makes another ticket active, so
// a page opened on a project reads it again whenever the person comes back to it; nothing is pushed to it.
function useProjectReread(loader: GraphLoad, status: LoadStatus): void {
  useEffect(() => {
    if (!api.project) {
      return;
    }
    const reread = () => {
      if (!status.loadingNow) void loader.load(api.project);
    };
    window.addEventListener('focus', reread);
    return () => window.removeEventListener('focus', reread);
  }, []);
}
