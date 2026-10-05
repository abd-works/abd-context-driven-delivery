import { useCallback, useEffect, useRef, useState } from 'react';
import { KnowledgeGraphClient } from './knowledge-graph/knowledge-graph-client';
import { KnowledgeGraphNode } from './knowledge-graph/knowledge-graph';

const SCAN_ROOT_KEY = 'kg-scan-root-v2';

export function useKnowledgeGraph(id: string) {
  const [graph, setGraph] = useState<KnowledgeGraphClient | null>(null);
  const [loading, setLoading] = useState(false);
  const [scanError, setScanError] = useState('');
  const [workStatus, setWorkStatus] = useState<{
    action: string;
    phase: 'working' | 'done' | 'failed';
    seconds: number;
    detail: string;
  } | null>(null);
  const request = useRef(0);

  useEffect(() => {
    if (workStatus?.phase !== 'working') {
      return;
    }
    const timer = window.setInterval(() => {
      setWorkStatus((current) =>
        current && current.phase === 'working'
          ? { ...current, seconds: current.seconds + 1 }
          : current,
      );
    }, 1000);
    return () => window.clearInterval(timer);
  }, [workStatus?.phase, workStatus?.action]);

  const take = useCallback((work: Promise<void>, target: KnowledgeGraphClient, action?: string) => {
    const token = ++request.current;
    const started = Date.now();
    setLoading(true);
    setScanError('');
    if (action) {
      setWorkStatus({ action, phase: 'working', seconds: 0, detail: '' });
    }
    work
      .then(() => {
        if (token === request.current) {
          setGraph(target);
          if (action) {
            setWorkStatus({
              action,
              phase: 'done',
              seconds: Math.floor((Date.now() - started) / 1000),
              detail: '',
            });
          }
        }
      })
      .catch((error: unknown) => {
        if (token === request.current) {
          const detail =
            error instanceof Error ? error.message : 'Could not load KnowledgeGraph';
          setScanError(detail);
          if (action) {
            setWorkStatus({
              action,
              phase: 'failed',
              seconds: Math.floor((Date.now() - started) / 1000),
              detail,
            });
          }
        }
      })
      .finally(() => {
        if (token === request.current) {
          setLoading(false);
        }
      });
  }, []);

  useEffect(() => {
    const next = new KnowledgeGraphClient(null, null, null, null);
    next.graphId = id;
    next.folder = lastScanFolder();
    take(next.loadKnowledgeGraph(next.folder || id), next, 'Load Knowledge Graph');
  }, [id, take]);

  const selectNode = useCallback((nodeId: string) => {
    setGraph((prev) => {
      if (!prev) {
        return prev;
      }
      const node = prev.nodes.find((item) => item.nodeId === nodeId);
      if (node) {
        prev.choose(node);
      }
      return Object.assign(Object.create(Object.getPrototypeOf(prev)), prev);
    });
  }, []);

  const selectFolder = useCallback(
    (input: { folder?: string; paths?: string[] } = {}) => {
      const next = graph ?? new KnowledgeGraphClient(null, null, null, null);
      const chosen = input.folder ?? lastScanFolder();
      next.graphId = '';
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem('kg-scan-graph-id-v2');
      }
      next.folder = chosen;
      take(next.loadKnowledgeGraph(next.folder, input.paths), next, 'Load Knowledge Graph');
    },
    [graph, take],
  );

  const runDatabase = useCallback(
    (action: string, folder: string | undefined, operation: (item: KnowledgeGraphClient) => Promise<void>) => {
      const next = graph ?? new KnowledgeGraphClient(null, null, null, null);
      next.folder = folder || next.folder || lastScanFolder();
      take(operation(next), next, action);
    },
    [graph, take],
  );

  return {
    graph,
    loading,
    workStatus,
    scanError,
    folder: graph?.folder ?? lastScanFolder(),
    listedTree: graph?.matching.length ? graph.matching : graph?.nodes ?? [],
    filterOptions: graph?.options ?? {
      practices: [],
      stages: [],
      node_types: [],
      relationship_types: [],
      rules: [],
      ruleCatalog: [],
    },
    members: graph?.members ?? [],
    selectedNode: graph?.selected ?? null,
    html: graph?.render() ?? '',
    selectNode,
    selectFolder,
    createDatabase: (folder?: string) =>
      runDatabase('Create database', folder, (item) => item.createDatabase()),
    refreshMaster: (folder?: string) =>
      runDatabase('Merge working to master', folder, (item) => item.refreshMaster()),
    reloadWorkingCopy: (folder?: string) =>
      runDatabase('Reload working copy', folder, (item) => item.reloadWorkingCopy()),
    choose: (node: KnowledgeGraphNode) => graph?.choose(node),
  };
}

function lastScanFolder(): string {
  if (typeof window === 'undefined') {
    return '';
  }
  const fromQuery = new URLSearchParams(window.location.search).get('folder');
  if (fromQuery) {
    window.localStorage.setItem(SCAN_ROOT_KEY, fromQuery);
    window.localStorage.removeItem('kg-scan-graph-id-v2');
    return fromQuery;
  }
  return window.localStorage.getItem(SCAN_ROOT_KEY) ?? '';
}
