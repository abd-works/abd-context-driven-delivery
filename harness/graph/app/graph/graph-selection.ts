import type { ViolationFocus } from '../source/violation-prompt';

export type GraphSelection = {
  nodeId: string;
  violation?: ViolationFocus;
};
