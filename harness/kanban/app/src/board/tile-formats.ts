import type { Column, TicketFiles } from './board'
import { FORMAT_GROUPS } from './board-brand'

export type FormatChip = { label: string; formats: string[] }

// Each group the tile offers, and any format the canvas groups do not name under its own name.
export function chipsOf(stage: Column, slugs: string[]): FormatChip[] {
  const offered = [...new Set(slugs.flatMap(slug => stage.formats?.[slug] ?? []))]
  const grouped = FORMAT_GROUPS.map(group => ({ ...group, formats: group.formats.filter(format => offered.includes(format)) })).filter(group => group.formats.length)
  const named = FORMAT_GROUPS.flatMap(group => group.formats)
  const others = offered.filter(format => !named.includes(format)).map(format => ({ label: format, formats: [format] }))
  return [...grouped, ...others]
}

// A chip stands for a group, and each fidelity uses one format from it: its default when the group holds that.
function chipFormat(stage: Column, slug: string, chip: FormatChip): string | undefined {
  const offered = chip.formats.filter(format => stage.formats?.[slug]?.includes(format))
  const preferred = stage.default_formats?.[slug] ?? ''
  return offered.includes(preferred) ? preferred : offered[0]
}

export function chosenFormats(stage: Column, slugs: string[], picked: string[]): string[] {
  const chips = chipsOf(stage, slugs).filter(chip => picked.includes(chip.label))
  return [...new Set(slugs.flatMap(slug => chips.flatMap(chip => chipFormat(stage, slug, chip) ?? [])))]
}

const hasMade = (files: TicketFiles, slug: string, chip: FormatChip): boolean =>
  chip.formats.some(format => (files[slug]?.[format] ?? []).some(entry => entry.exists))

export const chipDoneCount = (files: TicketFiles, slugs: string[], chip: FormatChip): number => slugs.filter(slug => hasMade(files, slug, chip)).length

export const chipOfferedCount = (stage: Column, slugs: string[], chip: FormatChip): number => slugs.filter(slug => chipFormat(stage, slug, chip)).length

// A tile opens ready to run: the fidelities' default formats, unless that output already exists.
export function defaultPicks(stage: Column, slugs: string[], files: TicketFiles): string[] {
  const defaults = slugs.map(slug => stage.default_formats?.[slug] ?? '')
  return chipsOf(stage, slugs)
    .filter(chip => chip.formats.some(format => defaults.includes(format)) && !chipDoneCount(files, slugs, chip))
    .map(chip => chip.label)
}
