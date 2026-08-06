import React from 'react';
import { createRoot } from 'react-dom/client';
import { {{EpicName}}View } from './{{EpicName}}View';

/**
 * main.tsx — browser process entry for the {{epicSlug}} feature package.
 *
 * Lives on the feature package — there is no separate app-client package.
 */
createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <{{EpicName}}View />
  </React.StrictMode>,
);
