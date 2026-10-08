import { PythonCall } from '../python-call';
import type { Staleness } from './DataManagementView';

export class DataManagementClient {
  constructor(private readonly python = new PythonCall()) {}

  createDatabase(folder: string, practices: Record<string, string>): Promise<string> {
    return this.python.run('create_database', { folder, practices, database: folder });
  }

  mergeWorkingToMaster(): Promise<string> {
    return this.python.run('reload_working_copy');
  }

  reloadWorkingCopy(folder: string, practices: Record<string, string>): Promise<string> {
    return this.python.run('load_working_copy', { folder, practices, database: folder });
  }

  staleness(folder: string, practices: Record<string, string>): Promise<Staleness> {
    return this.python.run('staleness', { folder, practices, database: folder });
  }

  serializeGraphCache(folder: string, practices: Record<string, string>): Promise<string> {
    return this.python.run('serialize_graph_cache', { folder, practices, database: folder });
  }
}
