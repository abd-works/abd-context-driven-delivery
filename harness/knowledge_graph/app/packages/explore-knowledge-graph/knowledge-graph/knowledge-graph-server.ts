import { KnowledgeGraph } from "./knowledge-graph";

export class KnowledgeGraphServer extends KnowledgeGraph {
  createDatabase(): void {
    super.createDatabase();
    this.copyMasterToWorkingCopy();
  }

  refreshMaster(): void {
    this.copyWorkingCopyToMaster();
    this.saveKnowledgeGraph();
    this.loadKnowledgeGraph(this.folder);
  }

  reloadWorkingCopy(): void {
    this.saveKnowledgeGraph();
    this.copyWorkingCopyToMaster();
    this.loadKnowledgeGraph(this.folder);
  }

  updateWorkingCopy(paths: any): void {
    this.saveKnowledgeGraph();
    this.loadKnowledgeGraph(this.folder);
  }
}
