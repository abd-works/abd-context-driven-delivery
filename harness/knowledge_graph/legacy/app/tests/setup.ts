import { createElement } from 'react';
import { vi } from 'vitest';
import '@testing-library/jest-dom/vitest';

vi.mock('@monaco-editor/react', () => ({
  default: ({ value }: { value?: string }) =>
    createElement('pre', { 'data-monaco': 'stub' }, value ?? ''),
}));
