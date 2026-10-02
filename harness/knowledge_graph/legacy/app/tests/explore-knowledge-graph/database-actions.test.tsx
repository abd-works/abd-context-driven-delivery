import { render, screen } from '@testing-library/react';
import { ExploreKnowledgeGraphView } from '../../packages/explore-knowledge-graph/ExploreKnowledgeGraphView';

describe('Explore Knowledge Graph database actions', () => {
  it('should show create database, refresh master, and reload working copy', () => {
    render(<ExploreKnowledgeGraphView />);
    expect(screen.getByTestId('create-database')).toBeTruthy();
    expect(screen.getByTestId('refresh-master')).toBeTruthy();
    expect(screen.getByTestId('reload-working-copy')).toBeTruthy();
    expect(screen.queryByTestId('repo-path')).toBeNull();
  });
});
