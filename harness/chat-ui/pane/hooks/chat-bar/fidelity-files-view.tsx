import type { EngineInterface } from 'claude-code'

import type { FidelityFilesJson } from '../../types'
import { BRAND } from '../brand'
import { closeFiles, showFile } from './fidelity-files-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// A file's text in the files view shows this many lines, so the box keeps above the prompt.
const FILE_LINES = 24

// One tab per file the fidelity declares, and the shown tab's first lines.
export function FidelityFilesView($: EngineInterface, { Box, Button, Text }: ElementTable, files: FidelityFilesJson) {
  if (!files) return null
  const shown = files.tabs.find(tab => tab.path === files.shown)
  const lines = (shown?.text ?? '').split('\n').slice(0, FILE_LINES)
  return (
    <Box key="files" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.surface}>
      <Box flexDirection="row" gap={1} flexWrap="wrap">
        {files.tabs.map(tab => (
          <Button key={`file-${tab.path}`} label={tab.path.split('/').at(-1) ?? tab.path} variant={tab.path === files.shown ? 'primary' : undefined} onPress={() => showFile($, tab.path)} />
        ))}
        <Button key="files-close" label="✕" onPress={() => closeFiles($)} />
      </Box>
      {files.tabs.length ? lines.map((line, index) => <Text key={`line-${index}`} color={BRAND.text}>{line}</Text>) : <Text color={BRAND.muted}>{`${files.fidelity} declares no files.`}</Text>}
    </Box>
  )
}
