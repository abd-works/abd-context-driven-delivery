/** How the explorer names a pattern overlay: by its folder's name, read as words. */

export function overlayCatalogLabel(patternId: string): string {
  const words = patternId.replace(/_/g, ' ');
  return words.charAt(0).toUpperCase() + words.slice(1);
}

export function overlayPathLabel(path: string): string {
  const trimmed = path.replace(/[/\\]+$/, '');
  const base = trimmed.split(/[/\\]/).pop() || path;
  return overlayCatalogLabel(base);
}
