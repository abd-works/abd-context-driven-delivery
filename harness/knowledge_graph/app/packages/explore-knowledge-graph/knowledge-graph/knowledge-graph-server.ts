import { KnowledgeGraph } from "./knowledge-graph";

export class KnowledgeGraphServer extends KnowledgeGraph {
  createDatabase(): void {
    super.createDatabase();
    this.copyMasterToWorkingCopy();
  }

  refreshMaster(): void {
    this.copyWorkingCopyToMaster();
  }

  reloadWorkingCopy(): void {
    this.workingCopy = `${this.folder}/.codeql/javascript-working-copy`;
    this.loadedLatestFiles = true;
  }

  updateWorkingCopy(paths: any): void {
    this.saveKnowledgeGraph();
    this.loadKnowledgeGraph(this.folder);
  }
}
