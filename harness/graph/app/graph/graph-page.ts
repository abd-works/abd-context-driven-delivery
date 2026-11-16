import { GraphClient } from './GraphClient';
import { GraphApi } from './graph-api';
import { chatOfPage, GraphFailures } from './graph-failures';

// The page's one way to its server, and the one place its failures go: to a toast and to the chat that opened it.
export const api = new GraphApi();
export const failures = new GraphFailures(api, chatOfPage());
// The explorer's graph, the one the cdd server holds for the page's project or folder.
export const graphs = new GraphClient(api);
