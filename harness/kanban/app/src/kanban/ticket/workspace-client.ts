import type { WorkspaceData } from '@cdd/harness/kanban/ticket'

// What exists for a ticket on disk. WorkspaceData has no generated class, because Python returns it as a plain result.
export class WorkspaceClient {
  constructor(private readonly data: WorkspaceData) {}

  get hasBranch(): boolean {
    return this.data.has_branch
  }

  get hasWorktree(): boolean {
    return this.data.has_worktree
  }

  get leavingHasBranch(): boolean {
    return this.data.leaving_has_branch
  }
}
