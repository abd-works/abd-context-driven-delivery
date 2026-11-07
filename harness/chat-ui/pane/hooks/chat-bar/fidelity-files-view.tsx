import type { EngineInterface } from 'claude-code'

import type { FidelityFilesJson } from '../../types'
import { BRAND } from '../brand'
import { closeFiles, openInDrawio, showFile } from './fidelity-files-client'

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

// One tab per file the fidelity declares, or its validation report alone, and the shown tab's first lines.
export function FidelityFilesView($: EngineInterface, elements: ElementTable, files: FidelityFilesJson) {
  const { Box, Button, Text } = elements
  if (!files) return null
  const shown = files.tabs.find(tab => tab.path === files.shown)
  return (
    <Box key="files" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.surface}>
      <Box flexDirection="row" gap={1} flexWrap="wrap">
        {files.tabs.map(tab => (
          <Button key={`file-${tab.path}`} label={tab.path.split('/').at(-1) ?? tab.path} variant={tab.path === files.shown ? 'primary' : undefined} onPress={() => showFile($, tab.path)} />
        ))}
        {shown?.path.endsWith('.drawio') ? <Button key="file-drawio" label="Open in draw.io" variant="primary" onPress={() => openInDrawio($, shown.path)} /> : null}
        <Button key="files-close" label="✕" onPress={() => closeFiles($)} />
      </Box>
      {shown ? FileTextView(elements, shown.path, shown.text ?? '') : <Text color={BRAND.muted}>{`${files.fidelity} declares no files.`}</Text>}
    </Box>
  )
}
