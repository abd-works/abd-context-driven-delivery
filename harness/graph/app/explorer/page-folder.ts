import { useState, type Dispatch, type SetStateAction } from 'react';
import { api } from '../graph/graph-page';

const LAST_FOLDER = 'cdd-graph-folder';
const FOLDER_QUERY = 'folder';

// The folder the page reads its graph from, as a person typed or chose it. A page opened with ?folder= (the chat bar
// names the session's workpath) starts on that folder; one opened on a project (?project=, from a ticket's graph widget)
// on the project; a page opened with neither on the folder a person last chose.
export class PageFolder {
  constructor(private readonly held: [string, Dispatch<SetStateAction<string>>]) {}

  get value(): string {
    return this.held[0];
  }

  // Whether a folder is chosen, so a change of filter or overlays has a graph to read.
  get chosen(): boolean {
    return Boolean(this.held[0].trim());
  }

  choose(folder: string): void {
    this.held[1](folder);
  }

  // root is the folder last loaded: a page opened on a project keeps no folder of its own.
  remember(root: string): void {
    if (!api.project) window.localStorage.setItem(LAST_FOLDER, root);
  }
}

export function usePageFolder(): PageFolder {
  return new PageFolder(useState(openedFolder));
}

export function openedFolder(): string {
  const named = new URLSearchParams(window.location.search).get(FOLDER_QUERY)?.trim() ?? '';
  return named || api.project || (window.localStorage.getItem(LAST_FOLDER) ?? '');
}
