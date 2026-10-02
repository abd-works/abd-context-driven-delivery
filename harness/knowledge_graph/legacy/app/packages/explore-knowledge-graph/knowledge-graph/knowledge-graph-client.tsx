import { useCallback, useEffect, useRef, useState } from 'react';
import {
  KnowledgeGraphClient,
} from '../../../../app/packages/explore-knowledge-graph/knowledge-graph/knowledge-graph-client';
import {
  KnowledgeGraphNode,
} from '../../../../app/packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';

const SCAN_ROOT_KEY = 'kg-scan-root-v2';

export { KnowledgeGraphClient };

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

  const followRelationship = useCallback((toId: string) => {
    setGraph((prev) => {
      if (!prev || !prev.selected) {
        return prev;
      }
      const edge = prev.selected.edges.find((item) => item.to?.nodeId === toId);
      if (edge) {
        const other = prev.selected.navigateTo(edge);
        if (other) {
          prev.choose(other);
        }
      }
      return Object.assign(Object.create(Object.getPrototypeOf(prev)), prev);
    });
  }, []);

  const selectFolder = useCallback((input: { folder?: string } = {}) => {
    const next = graph ?? new KnowledgeGraphClient(null, null, null, null);
    next.folder = input.folder ?? lastScanFolder();
    take(next.loadKnowledgeGraph(next.folder), next, 'Load Knowledge Graph');
  }, [graph, take]);

  const runDatabase = useCallback((action: string, operation: (item: KnowledgeGraphClient) => Promise<void>) => {
    const next = graph ?? new KnowledgeGraphClient(null, null, null, null);
    next.folder = next.folder || lastScanFolder();
    take(operation(next), next, action);
  }, [graph, take]);

  return {
    graph,
    loading,
    workStatus,
    scanError,
    folder: graph?.folder ?? '',
    listedTree: graph?.matching.length ? graph.matching : graph?.nodes ?? [],
    selectedNode: graph?.selected ?? null,
    html: graph?.render() ?? '',
    selectNode,
    followRelationship,
    selectFolder,
    refreshGraph: () => selectFolder({ folder: graph?.folder }),
    createDatabase: (folder?: string) =>
      runDatabase('Create database', (item) => {
        item.folder = folder || item.folder || lastScanFolder();
        return item.createDatabase();
      }),
    refreshMaster: (folder?: string) =>
      runDatabase('Refresh master', (item) => {
        item.folder = folder || item.folder || lastScanFolder();
        return item.refreshMaster();
      }),
    reloadWorkingCopy: (folder?: string) =>
      runDatabase('Reload working copy', (item) => {
        item.folder = folder || item.folder || lastScanFolder();
        return item.reloadWorkingCopy();
      }),
    choose: (node: KnowledgeGraphNode) => graph?.choose(node),
  };
}

function lastScanFolder(): string {
  if (typeof window === 'undefined') {
    return '';
  }
  return window.localStorage.getItem(SCAN_ROOT_KEY) ?? '';
}
