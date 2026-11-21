import { useRef, useState, type MutableRefObject } from 'react';
import type { Held } from './held';
import type { ExplorerEntryData, FilterData } from '@cdd/harness/graph/graph';
import { NO_CHOICES, NO_FILTER, chosen, nodeFilter, type FilterSelection } from '../filter/filter-selection';
import { reasonOf } from '@cdd/cdd-page-failures';
import { failures, graphs } from '../graph/graph-page';
import { withBranch } from '../graph/graph-selection';
import type { LoadStatus } from './load-status';
import type { PageFolder } from './page-folder';


interface ExplorerFilterState {
  selection: Held<FilterSelection>;
  trees: Held<ExplorerEntryData[]>;
  choices: Held<FilterData>;
  // The filter the trees on the page were read with, which a branch opened later is read with too.
  shown: MutableRefObject<FilterSelection>;
  folder: PageFolder;
  status: LoadStatus;
}

// What the explorer's filter chooses and the trees it keeps. Python's Filter works out what the filter offers and which
// nodes it keeps; the page shows what it answers.
export class ExplorerFilter {
  constructor(private readonly state: ExplorerFilterState) {}

  get selection(): FilterSelection {
    return this.state.selection[0];
  }

  // The folder the graph the filter narrows is read from.
  get folder(): PageFolder {
    return this.state.folder;
  }

  get trees(): ExplorerEntryData[] {
    return this.state.trees[0];
  }

  // The node types, relationships, and rules the filter offers for the selection.
  get offered(): FilterData {
    return this.state.choices[0];
  }

  select(next: FilterSelection): void {
    this.state.selection[1](next);
  }

  // The node types the practices hold, and the relationships and rules of the node types chosen. practicesBefore names
  // the practices chosen before a change of practice.
  async offerChoices(next: FilterSelection, practicesBefore?: string[]): Promise<FilterData> {
    const choices = (await graphs.filterChoices(next.practices, next.node_types, practicesBefore)) ?? NO_CHOICES;
    this.state.choices[1](choices);
    return choices;
  }

  // The nodes the selection matches, with the way to each, in every practice it names.
  async show(resolved: FilterSelection): Promise<void> {
    this.state.selection[1](resolved);
    this.state.shown.current = resolved;
    this.state.trees[1]((await graphs.explorerTrees(nodeFilter(resolved))) ?? []);
  }

  // The entries a closed entry left out, read with the filter the trees were read with, put in its place.
  async openBranch(nodeId: string): Promise<void> {
    try {
      const branch = await graphs.explorerBranch(nodeId, nodeFilter(this.state.shown.current));
      if (branch) this.state.trees[1]((current) => withBranch(current, branch));
    } catch (cause) {
      failures.fail(reasonOf(cause), `Opening ${nodeId} in the Graph app's tree`);
    }
  }

  // A person's change of the filter: with a folder chosen, a change of practice or node type asks Python's Filter what
  // the new choice offers first.
  async apply(next: FilterSelection): Promise<void> {
    if (!this.state.folder.chosen) {
      this.select(next);
      return;
    }
    try {
      await this.show(await this.resolved(next));
    } catch (cause) {
      this.state.status.failed(cause, 'Changing the filter in the Graph app');
    }
  }

  private async resolved(next: FilterSelection): Promise<FilterSelection> {
    const current = this.selection;
    if (joined(next.practices) !== joined(current.practices)) return chosen(next, await this.offerChoices(next, current.practices));
    if (joined(next.node_types) !== joined(current.node_types)) return chosen(next, await this.offerChoices(next));
    return next;
  }
}

export function useExplorerFilter(folder: PageFolder, status: LoadStatus): ExplorerFilter {
  return new ExplorerFilter({
    selection: useState<FilterSelection>(NO_FILTER),
    trees: useState<ExplorerEntryData[]>([]),
    choices: useState<FilterData>(NO_CHOICES),
    shown: useRef<FilterSelection>(NO_FILTER),
    folder,
    status,
  });
}

function joined(values: string[]): string {
  return values.join('\n');
}
