import { useState } from 'react';
import wordmarkBlack from './brand/abd.works.wordmark.black.svg?url';
import wordmarkWhite from './brand/abd.works.wordmark.white.svg?url';

type SiteNavProps = {
  canReload: boolean;
  onReload: () => void;
};

// The page's header: the brand, the theme a person reads it in, and the button that reloads the graph from its files.
export function SiteNav({ canReload, onReload }: SiteNavProps) {
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme ?? '');
  const engineering = theme === 'engineering';
  const choose = (next: '' | 'engineering') => setTheme(applyTheme(next));
  return (
    <header className="site-nav">
      <div className="nav-brand">
        <a className="nav-logo" href="/" aria-label="abd.works">
          <img src={engineering ? wordmarkWhite : wordmarkBlack} alt="abd.works" />
        </a>
        <p className="page-hero-label">Knowledge graph</p>
      </div>
      <div className="nav-actions">
        <div className="mode-toggle" role="group" aria-label="Theme">
          <button type="button" className={engineering ? '' : 'is-active'} onClick={() => choose('')}>
            <span className="mode-label">Executive</span>
            <span className="mode-icon" aria-hidden="true">☀</span>
          </button>
          <button type="button" className={engineering ? 'is-active' : ''} onClick={() => choose('engineering')}>
            <span className="mode-label">Engineering</span>
            <span className="mode-icon" aria-hidden="true">☾</span>
          </button>
        </div>
        <button type="button" className="btn-refresh" data-testid="force-reload" title="Force reload" disabled={!canReload} onClick={onReload}>
          Force reload
        </button>
      </div>
    </header>
  );
}

// Show the page in theme next, and keep it for the next visit.
function applyTheme(next: '' | 'engineering'): string {
  if (next) {
    document.documentElement.dataset.theme = next;
  } else {
    delete document.documentElement.dataset.theme;
  }
  window.localStorage.setItem('kg-theme', next);
  return next;
}
