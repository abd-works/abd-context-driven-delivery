import { FORMAT_GROUPS } from '../board/board-brand'
import type { ColumnClient } from '../board/column-client'
import type { FilesByFidelity } from './ticket-client'

export type FormatChip = { label: string; formats: string[] }

// Each group the tile offers, and any format the canvas groups do not name under its own name.
export function chipsOf(stage: ColumnClient, slugs: string[]): FormatChip[] {
  const offered = [...new Set(slugs.flatMap(slug => stage.formats[slug] ?? []))]
  const grouped = FORMAT_GROUPS.map(group => ({ ...group, formats: group.formats.filter(format => offered.includes(format)) })).filter(group => group.formats.length)
  const named = FORMAT_GROUPS.flatMap(group => group.formats)
  const others = offered.filter(format => !named.includes(format)).map(format => ({ label: format, formats: [format] }))
  return [...grouped, ...others]
}

// A chip stands for a group, and each fidelity uses one format from it: its default when the group holds that.
function chipFormat(stage: ColumnClient, slug: string, chip: FormatChip): string | undefined {
  const offered = chip.formats.filter(format => stage.formats[slug]?.includes(format))
  const preferred = stage.defaultFormats[slug] ?? ''
  return offered.includes(preferred) ? preferred : offered[0]
}

export function chosenFormats(stage: ColumnClient, slugs: string[], picked: string[]): string[] {
  const chips = chipsOf(stage, slugs).filter(chip => picked.includes(chip.label))
  return [...new Set(slugs.flatMap(slug => chips.flatMap(chip => chipFormat(stage, slug, chip) ?? [])))]
}

const hasMade = (files: FilesByFidelity, slug: string, chip: FormatChip): boolean =>
  chip.formats.some(format => (files[slug]?.[format] ?? []).some(entry => entry.exists))

export const chipDoneCount = (files: FilesByFidelity, slugs: string[], chip: FormatChip): number => slugs.filter(slug => hasMade(files, slug, chip)).length

export const chipOfferedCount = (stage: ColumnClient, slugs: string[], chip: FormatChip): number => slugs.filter(slug => chipFormat(stage, slug, chip)).length

// A tile opens ready to run: the fidelities' default formats, unless that output already exists.
export function defaultPicks(stage: ColumnClient, slugs: string[], files: FilesByFidelity): string[] {
  const defaults = slugs.map(slug => stage.defaultFormats[slug] ?? '')
  return chipsOf(stage, slugs)
    .filter(chip => chip.formats.some(format => defaults.includes(format)) && !chipDoneCount(files, slugs, chip))
    .map(chip => chip.label)
}
