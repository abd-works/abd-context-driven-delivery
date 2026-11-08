import type { EngineInterface } from 'claude-code'

import type { FidelityFilesJson } from '../../types'
import { BRAND } from '../brand'
import { openInDrawio } from './drawio-viewer-client'
import { closeFiles, isDiagram, showFile, validateAgain } from './fidelity-files-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// A file's text in the files view shows this many lines, so the box keeps above the prompt.
const FILE_LINES = 40

// The shown tab's first lines: markdown drawn as the board and the chat draw it, with headings, tables and links, and any
// other file as its plain lines. A note says how many lines are left out.
function FileTextView({ Box, Markdown, Text }: ElementTable, path: string, text: string) {
  const lines = text.split('\n')
  const shown = lines.slice(0, FILE_LINES)
  const more = lines.length - shown.length
  return (
    <Box key="file-text" flexDirection="column">
      {path.endsWith('.md') ? <Markdown key="file-markdown" text={shown.join('\n')} /> : shown.map((line, index) => <Text key={`line-${index}`} color={BRAND.text}>{line}</Text>)}
      {more > 0 ? <Text color={BRAND.muted}>{`… ${more} more lines`}</Text> : null}
    </Box>
  )
}

function ShownFileView(elements: ElementTable, shown: { path: string; text: string | null }) {
  const { Text } = elements
  if (isDiagram(shown.path)) return <Text color={BRAND.muted}>{`${shown.path} is a diagram: open it in draw.io.`}</Text>
  return FileTextView(elements, shown.path, shown.text ?? '')
}

// A report whose saved graph predates the graph's shape says so, and offers to validate its fidelity again, as the board does.
function OutOfDateView($: EngineInterface, { Box, Button, Text }: ElementTable, slug: string) {
  return (
    <Box key="out-of-date" flexDirection="row" gap={1} alignItems="center">
      <Text color={BRAND.error}>This report's saved graph is out of date, so its graph's rules are not shown. Validate again to read them.</Text>
      <Button key="validate-again" label="Validate again" onPress={() => validateAgain($, slug)} />
    </Box>
  )
}

// The files pane: one tab per file the fidelity declares, or its validation report alone, and the shown tab's first lines.
export function FidelityFilesView($: EngineInterface, elements: ElementTable, files: FidelityFilesJson) {
  const { Box, Button, Text } = elements
  if (!files) return <Text color={BRAND.muted}>No files open.</Text>
  const shown = files.tabs.find(tab => tab.path === files.shown)
  return (
    <Box key="files" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.surface}>
      <Box flexDirection="row" gap={1} flexWrap="wrap">
        {files.tabs.map(tab => (
          <Button key={`file-${tab.path}`} label={tab.path.split('/').at(-1) ?? tab.path} variant={tab.path === files.shown ? 'primary' : undefined} onPress={() => showFile($, tab.path)} />
        ))}
        {shown && isDiagram(shown.path) ? <Button key="file-drawio" label="Open in draw.io" variant="primary" onPress={() => openInDrawio($, shown.path)} /> : null}
        <Button key="files-close" label="✕" onPress={() => closeFiles($)} />
      </Box>
      {files.isOutOfDate ? OutOfDateView($, elements, files.fidelity) : null}
      {shown ? ShownFileView(elements, shown) : <Text color={BRAND.muted}>{`${files.fidelity} declares no files.`}</Text>}
    </Box>
  )
}
