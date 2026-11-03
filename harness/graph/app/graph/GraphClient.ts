import { GraphClientGenerated } from '@cdd/harness/graph/graph';

import { GraphApi } from './graph-api';

// The explorer's graph: the one the cdd server holds, with the folder dialogs only this page opens.
export class GraphClient extends GraphClientGenerated {
  constructor(api = new GraphApi()) {
    super(api);
  }

  async chooseFolder(title = 'Select a repo folder'): Promise<string> {
    return (await this.api.post<{ folder: string }>('/explorer/choose-folder', { title }))?.folder ?? '';
  }

  async chooseOverlayFolder(): Promise<string> {
    const folder = await this.chooseFolder('Select a pattern overlay folder (contains practices/)');
    if (!folder) {
      return '';
    }
    return (await this.overlayOf(folder))?.overlay ?? '';
  }
}
