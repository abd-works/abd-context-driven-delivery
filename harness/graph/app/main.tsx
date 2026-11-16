import { createRoot } from 'react-dom/client';
import { GraphPage } from './GraphPage';
import './explorer.css';

// main.tsx imports only components, so Vite swaps a changed module in below them and never runs this file twice: a
// second createRoot on the same element leaves two roots removing each other's nodes.
const stored = window.localStorage.getItem('kg-theme');
if (stored === 'engineering') {
  document.documentElement.dataset.theme = 'engineering';
}

createRoot(document.getElementById('root')!).render(<GraphPage />);
