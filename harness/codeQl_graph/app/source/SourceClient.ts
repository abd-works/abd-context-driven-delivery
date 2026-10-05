import { PythonCall } from '../python-call';
import type { FoldMember } from './call-expansion';

export type SourceText = {
  node_id: string;
  name: string;
  type: string;
  file: string;
  text: string;
  start_line: number;
  end_line: number;
  members?: FoldMember[];
};

export class SourceClient {
  constructor(private readonly python = new PythonCall()) {}

  open(nodeId: string): Promise<SourceText> {
    return this.python.run('source', { node_id: nodeId });
  }
}
