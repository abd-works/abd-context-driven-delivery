import type { ElementTable, EngineInterface } from 'claude-code'

import type { FilesPanelJson, HelpPanelJson, ReportPanelJson, ReportRuleJson, SidePanelJson } from '../../types'
import { ActionButtonView } from './action-button'
import { BRAND } from './brand'
import { closeFileTab, chooseFilesMode, closePanel, openFileTab, togglePanelExpanded } from './side-panel-client'
import { fixRule, fixViolation } from './ticket-client'
import { isLocked } from './view-context'
import type { ViewContext } from './view-context'

const FILE_MODES = ['list', 'folder', 'files']
const PANEL_TITLES: Record<string, string> = { report: 'Report', files: 'Files', help: 'Help' }

const fileName = (path: string): string => path.split('/').at(-1) ?? path

const filesOf = (panel: FilesPanelJson) =>
  panel.slugs.flatMap(slug => Object.values(panel.files[slug] ?? {}).flat()).filter(entry => entry.exists)

function FileRowView($: EngineInterface, view: ViewContext, path: string, label: string) {
  return view.elements.Button({ key: `file-${path}`, plain: true, label, onPress: () => openFileTab($, path) })
}

function FolderGroupsView($: EngineInterface, view: ViewContext, panel: FilesPanelJson) {
  const { Box, Text } = view.elements
  const paths = filesOf(panel).map(entry => entry.path)
  const roots = [...new Set(paths.map(path => path.split('/')[0] ?? ''))]
  return (
    <Box key="folders" flexDirection="column">
      {roots.map(root => (
        <Box key={`folder-${root}`} flexDirection="column">
          <Text color={BRAND.muted}>{root}/</Text>
          {paths.filter(path => path.startsWith(`${root}/`)).map(path => FileRowView($, view, path, `  ${path.slice(root.length + 1)}`))}
        </Box>
      ))}
    </Box>
  )
}

function FileTabsView($: EngineInterface, view: ViewContext, panel: FilesPanelJson) {
  const { Box, Button, Code, Markdown, Text } = view.elements
  const text = panel.texts[panel.activeTab] ?? ''
  return (
    <Box key="tabs" flexDirection="column">
      <Box key="tab-names" flexDirection="row" flexWrap="wrap" columnGap={1}>
        {panel.tabs.map(path => (
          <Box key={`tab-${path}`} flexDirection="row">
            <Button key={`tab-open-${path}`} plain label={fileName(path)} dimColor={path !== panel.activeTab} onPress={() => openFileTab($, path)} />
            <Button key={`tab-close-${path}`} plain label="×" onPress={() => closeFileTab($, path)} />
          </Box>
        ))}
      </Box>
      {!text ? <Text color={BRAND.muted}>Not generated yet</Text> : null}
      {text && panel.activeTab.endsWith('.md') ? <Markdown text={text} /> : null}
      {text && !panel.activeTab.endsWith('.md') ? <Code source={text} path={panel.activeTab} /> : null}
    </Box>
  )
}

function FilesBodyView($: EngineInterface, view: ViewContext, panel: FilesPanelJson) {
  const { Box, Button, Text } = view.elements
  const paths = filesOf(panel)
  return (
    <Box key="files-body" flexDirection="column" gap={1}>
      <Box key="modes" flexDirection="row" columnGap={1}>
        {FILE_MODES.map(mode => (
          <Button key={`mode-${mode}`} label={mode} variant={panel.mode === mode ? 'primary' : 'secondary'} onPress={() => chooseFilesMode($, mode)} />
        ))}
      </Box>
      {panel.mode !== 'files' && !paths.length ? <Text color={BRAND.muted}>No files generated yet</Text> : null}
      {panel.mode === 'list' ? paths.map(entry => FileRowView($, view, entry.path, entry.path)) : null}
      {panel.mode === 'folder' ? FolderGroupsView($, view, panel) : null}
      {panel.mode === 'files' ? FileTabsView($, view, panel) : null}
    </Box>
  )
}

function RuleView($: EngineInterface, view: ViewContext, panel: ReportPanelJson, rule: ReportRuleJson) {
  const { Box, Text } = view.elements
  const isOff = isLocked(view, panel.ticket)
  return (
    <Box key={`rule-${rule.name}`} flexDirection="column">
      <Box key="rule-head" flexDirection="row" justifyContent="space-between">
        <Text bold color={BRAND.text}>
          {rule.name} <Text color={BRAND.error}>{rule.count} violations</Text>
        </Text>
        {ActionButtonView(view, `fix-all-${rule.name}`, 'Fix all', isOff ? null : () => fixRule($, panel.fidelity, rule.name))}
      </Box>
      {rule.violations.map(violation => (
        <Box key={`violation-${rule.name}-${violation.location}-${violation.message}`} flexDirection="row" justifyContent="space-between">
          <Text color={BRAND.muted}>
            {violation.location}: {violation.message}
          </Text>
          {ActionButtonView(view, `fix-${violation.location}-${violation.message}`, 'Fix', isOff ? null : () => fixViolation($, panel.fidelity, rule.name, violation.location))}
        </Box>
      ))}
    </Box>
  )
}

function ReportBodyView($: EngineInterface, view: ViewContext, panel: ReportPanelJson) {
  const { Box, Text } = view.elements
  const { report } = panel
  return (
    <Box key="report-body" flexDirection="column" gap={1}>
      <Text color={BRAND.muted}>{report.path}</Text>
      {report.has_saved_graph ? null : <Text color={BRAND.warning}>This report has no saved graph, so its rules are only in the report file</Text>}
      {report.has_saved_graph && !report.rules.length ? <Text color={BRAND.success}>No violations in this report</Text> : null}
      {report.rules.map(rule => RuleView($, view, panel, rule))}
    </Box>
  )
}

function HelpBodyView(view: ViewContext, panel: HelpPanelJson) {
  const { Box, Link, Markdown, Text } = view.elements
  const { help } = panel
  return (
    <Box key="help-body" flexDirection="column" gap={1}>
      <Link href={help.href} label="Open on the Forge" />
      <Markdown text={help.overview} />
      {help.guidance ? <Markdown text={help.guidance} /> : null}
      <Text bold color={BRAND.muted}>
        RULES
      </Text>
      {help.rules.map(rule => (
        <Box key={`help-rule-${rule.slug}`} flexDirection="column">
          <Text color={BRAND.text}>{rule.slug}</Text>
          <Text color={BRAND.muted}>{rule.text}</Text>
        </Box>
      ))}
    </Box>
  )
}

function bodyOf($: EngineInterface, view: ViewContext, panel: SidePanelJson) {
  if (panel.kind === 'files') return FilesBodyView($, view, panel)
  if (panel.kind === 'report') return ReportBodyView($, view, panel)
  return HelpBodyView(view, panel)
}

function SidePanelView($: EngineInterface, view: ViewContext, panel: SidePanelJson, width: number) {
  const { elements, hasSurfaceModules } = view
  const { Box, Text } = elements
  const Client = hasSurfaceModules ? (elements as ElementTable<'desktop'>).Client : null
  return (
    <Box key={`panel-${panel.kind}`} flexDirection="row" width={width} flexShrink={0} backgroundColor={BRAND.surface}>
      {Client ? (
        <Client
          key={`panel-grip-${panel.kind}`}
          module="./panel-grip.tsx"
          props={{ panel: panel.kind, width: panel.width, color: BRAND.idle, hoverColor: BRAND.accent }}
          width={1}
          height="100%"
        />
      ) : null}
      <Box key="panel-body" flexDirection="column" flexGrow={1} gap={1} paddingX={1} overflow="hidden">
        <Box key="panel-head" flexDirection="row" justifyContent="space-between">
          <Text bold color={BRAND.text}>
            {PANEL_TITLES[panel.kind]}
          </Text>
          <Box key="panel-controls" flexDirection="row" columnGap={1}>
            {ActionButtonView(view, `panel-expand-${panel.kind}`, panel.isExpanded ? 'Collapse' : 'Expand', () => togglePanelExpanded($, panel.kind))}
            {ActionButtonView(view, `panel-close-${panel.kind}`, '×', () => closePanel($, panel.kind))}
          </Box>
        </Box>
        {bodyOf($, view, panel)}
      </Box>
    </Box>
  )
}

const othersWidth = (panels: SidePanelJson[], kept: SidePanelJson): number =>
  panels.filter(panel => panel !== kept).reduce((total, panel) => total + panel.width, 0)

export const expandedPanel = ({ panels }: ViewContext): SidePanelJson | undefined => panels.find(panel => panel.isExpanded)

// An expanded panel takes the board's width less the other open panels.
export function SidePanelsView($: EngineInterface, view: ViewContext) {
  const { bodyColumns, panels } = view
  return panels.map(panel => SidePanelView($, view, panel, panel.isExpanded ? Math.max(bodyColumns - othersWidth(panels, panel), panel.width) : panel.width))
}
