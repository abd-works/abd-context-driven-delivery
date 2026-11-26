/** How the explorer names a pattern overlay: by its folder's name, read as words. */

export function overlayCatalogLabel(patternId: string): string {
  const words = patternId.replace(/_/g, ' ');
  return words.charAt(0).toUpperCase() + words.slice(1);
}

// The id of the overlay kept at path, its folder's name, which is how the graph's catalogue names it.
export function overlayId(path: string): string {
  const trimmed = path.replace(/[/\\]+$/, '');
  return trimmed.split(/[/\\]/).pop() || path;
}

export function overlayPathLabel(path: string): string {
  return overlayCatalogLabel(overlayId(path));
}
