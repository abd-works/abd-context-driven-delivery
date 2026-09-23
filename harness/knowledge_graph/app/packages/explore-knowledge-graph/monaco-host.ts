import { loader } from '@monaco-editor/react';
import * as monaco from 'monaco-editor';
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';
import tsWorker from 'monaco-editor/esm/vs/language/typescript/ts.worker?worker';

window.MonacoEnvironment = {
  getWorker(_workerId: string, label: string) {
    if (label === 'typescript' || label === 'javascript') {
      return new tsWorker();
    }
    return new editorWorker();
  },
};

loader.config({ monaco });

monaco.editor.defineTheme('kg-light', {
  base: 'vs',
  inherit: true,
  rules: [],
  colors: {
    'editor.background': '#F0ECE4',
    'editor.foreground': '#111113',
    'editorLineNumber.foreground': '#595A61',
    'editor.lineHighlightBackground': '#2563EB24',
  },
});

monaco.editor.defineTheme('kg-dark', {
  base: 'vs-dark',
  inherit: true,
  rules: [],
  colors: {
    'editor.background': '#1B1B20',
    'editor.foreground': '#E8E8ED',
    'editorLineNumber.foreground': '#9B9BA8',
    'editor.lineHighlightBackground': '#60A5FA38',
  },
});
