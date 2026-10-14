import { PythonCall } from '../python-call';

export type FilterSelection = {
  practices: string[];
  overlays: string[];
  node_types: string[];
  relationships: string[];
  rules: string[];
  violations: boolean;
};

export type InventoryBundle = {
  practices: Record<string, PracticeInventory>;
  overlays: string[];
  available_overlays: string[];
};

export type PracticeInventory = {
  node_counts: Record<string, number>;
  edge_count: number;
  node_types: string[];
  edge_types: string[];
  rules: string[];
  tree: GraphTree;
};

export type RuleHit = {
  message: string;
  file?: string;
  start?: number;
  end?: number;
};

export type GraphTree = {
  type: string;
  name: string;
  node_id: string;
  status?: string;
  violation?: string;
  violations?: RuleHit[];
  children: GraphTree[];
};

export class FilterClient {
  constructor(private readonly python = new PythonCall()) {}

  nodes(selection: FilterSelection): Promise<FilteredNode[]> {
    return this.python.run('return_nodes', { filter: selection });
  }

  choices(selection: FilterSelection): Promise<FilterChoices> {
    return this.python.run('filter_choices', { filter: selection });
  }

  applyOverlays(overlays: string[]): Promise<InventoryBundle> {
    return this.python.run('apply_overlays', { overlays });
  }
}

export type FilterChoices = {
  node_types: string[];
  relationships: string[];
  rules: string[];
};

export type FilteredNode = {
  practice: string;
  type: string;
  name: string;
  node_id: string;
  ancestors: string[];
  children: string[];
};
