import type { EngineInterface } from 'claude-code'

import type { FidelityFilesJson } from '../../types'
import { BRAND } from '../brand'
import { closeFiles, showFile } from './fidelity-files-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The canvas's files panel is 280px tall: a header, one line of tabs, the shown path, and this many lines of text,
// so the panel never pushes the bar's own line off screen.
const FILE_LINES = 12

// The header names the fidelity, one tab per file it declares sits on a single line that clips rather than wraps, and
// the shown tab's path and first lines follow. A desktop draws a Button's label in place of its children, so each tab
// is a plain Button holding its name.
export function FidelityFilesView($: EngineInterface, { Box, Button, Text }: ElementTable, files: FidelityFilesJson) {
  if (!files) return null
  const shown = files.tabs.find(tab => tab.path === files.shown)
  const lines = (shown?.text ?? '').split('\n').slice(0, FILE_LINES)
  return (
    <Box key="files" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.surface}>
      <Box flexDirection="row" gap={1}>
        <Text size="caption" color={BRAND.muted}>FILES</Text>
        <Text color={BRAND.accent}>{files.fidelity}</Text>
        <Box flexGrow={1} />
        <Button key="files-close" plain onPress={() => closeFiles($)}>
          <Text color={BRAND.muted}>✕</Text>
        </Button>
      </Box>
      <Box flexDirection="row" gap={1} flexWrap="nowrap" overflow="hidden">
        {files.tabs.map(tab => (
          <Button key={`file-${tab.path}`} plain onPress={() => showFile($, tab.path)}>
            <Text size="footnote" color={tab.path === files.shown ? BRAND.text : BRAND.muted} backgroundColor={tab.path === files.shown ? BRAND.raised : undefined}>
              {tab.path.split('/').at(-1) ?? tab.path}
            </Text>
          </Button>
        ))}
      </Box>
      {shown ? <Text size="caption" color={BRAND.muted}>{shown.path}</Text> : null}
      {files.tabs.length ? lines.map((line, index) => <Text key={`line-${index}`} size="footnote" wrap="truncate-end" color={BRAND.text}>{line}</Text>) : <Text color={BRAND.muted}>{`${files.fidelity} declares no files.`}</Text>}
    </Box>
  )
}
