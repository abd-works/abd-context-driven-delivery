import {
  ExplorePracticeGraphsBaseHelper,
  KEEP_OPERATIONS_SMALL_FOCUSED,
  passingLoadOperation,
  SEEDED_GRAPH_ID,
} from './explore-practice-graphs.base';

export class ExplorePracticeGraphsE2eHelper extends ExplorePracticeGraphsBaseHelper {
  async seed(): Promise<void> {
    return;
  }

  async cleanup(): Promise<void> {
    this.listed = null;
  }

  graphQuery(): string {
    return `/?id=${SEEDED_GRAPH_ID}`;
  }

  ruleSlug(): string {
    return KEEP_OPERATIONS_SMALL_FOCUSED;
  }

  passingName(): string {
    return passingLoadOperation.name;
  }
}
