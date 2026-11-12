const SHOWN_PARAGRAPHS = 2

// A card shows only the opening of what its ticket is about: its first paragraphs, then a link to the whole file.
export const openingOf = (text: string): { opening: string; isCut: boolean } => {
  const paragraphs = text.split(/\n\s*\n/).filter(paragraph => paragraph.trim())
  return { opening: paragraphs.slice(0, SHOWN_PARAGRAPHS).join('\n\n'), isCut: paragraphs.length > SHOWN_PARAGRAPHS }
}
