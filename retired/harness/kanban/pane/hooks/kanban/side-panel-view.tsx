import type { ElementTable, EngineInterface } from 'claude-code'

import type { FilesPanelJson, HelpPanelJson, ReportPanelJson, ReportRuleJson, SidePanelJson, SourceLineJson, ViolationJson } from '../../types'
import { ActionButtonView, ColorBarView, ExpandToggleView, LinkButtonView, SectionTitleView } from './action-button'
import { BRAND, practiceOf, PRACTICES } from './brand'
import { closeFileTab, chooseFilesMode, closePanel, openFileAtLine, openFileTab, togglePanelExpanded, toggleRule } from './side-panel-client'
import { fixRule, fixViolation } from './ticket-client'
import { countOf, guidanceSlug } from './ticket-summary'
import { isLocked, panelWidthsOf } from './view-context'
import type { ViewContext } from './view-context'

const FILE_MODES = ['list', 'folder', 'files']
const PANEL_TITLES: Record<string, string> = { report: 'VALIDATION REPORT', files: 'FILES', help: 'HELP' }

const fileName = (path: string): string => path.split('/').at(-1) ?? path

const filesOf = (panel: FilesPanelJson) =>
  panel.slugs.flatMap(slug => Object.values(panel.files[slug] ?? {}).flat()).filter(entry => entry.exists)

function FileRowView($: EngineInterface, view: ViewContext, path: string, label: string) {
  return LinkButtonView(view, `file-${path}`, label, BRAND.text, () => openFileTab($, path))
}

function FolderGroupsView($: EngineInterface, view: ViewContext, panel: FilesPanelJson) {
  const { Box, Text } = view.elements
  const paths = filesOf(panel).map(entry => entry.path)
  const roots = [...new Set(paths.map(path => path.split('/')[0] ?? ''))]
  return (
    <Box key="folders" flexDirection="column" rowGap={1} paddingX={2}>
      {roots.map(root => (
        <Box key={`folder-${root}`} flexDirection="column">
          <Text mono size="footnote" weight="semibold" color={BRAND.text}>
            {root}/
          </Text>
          <Box key={`folder-entries-${root}`} flexDirection="column" paddingLeft={2}>
            {paths.filter(path => path.startsWith(`${root}/`)).map(path => FileRowView($, view, path, path.slice(root.length + 1)))}
          </Box>
        </Box>
      ))}
    </Box>
  )
}

function FileTabsView($: EngineInterface, view: ViewContext, panel: FilesPanelJson) {
  const { Box, Button, Code, Markdown, Text } = view.elements
  const text = panel.texts[panel.activeTab] ?? ''
  const line = panel.lines[panel.activeTab] ?? 0
  return (
    <Box key="tabs" flexDirection="column" rowGap={1}>
      <Box key="tab-names" flexDirection="row" flexWrap="wrap" columnGap={2} paddingX={1} backgroundColor={BRAND.surface}>
        {panel.tabs.map(path => (
          <Box key={`tab-${path}`} flexDirection="row" columnGap={1}>
            <Button key={`tab-open-${path}`} plain onPress={() => openFileTab($, path)}>
              <Text mono size="footnote" underline={path === panel.activeTab} color={path === panel.activeTab ? BRAND.text : BRAND.muted}>
                {fileName(path)}
              </Text>
            </Button>
            <Button key={`tab-close-${path}`} plain dimColor label="×" onPress={() => closeFileTab($, path)} />
          </Box>
        ))}
      </Box>
      <Box key="active-file" paddingX={1}>
        <Text mono size="caption" color={BRAND.muted}>
          {panel.activeTab}
        </Text>
      </Box>
      {!text ? <Text color={BRAND.muted}>Not generated yet</Text> : null}
      {text && line ? <Code source={text.split('\n').slice(line - 1).join('\n')} path={panel.activeTab} startLine={line} /> : null}
      {text && !line && panel.activeTab.endsWith('.md') ? <Markdown text={text} /> : null}
      {text && !line && !panel.activeTab.endsWith('.md') ? <Code source={text} path={panel.activeTab} /> : null}
    </Box>
  )
}

function FilesBodyView($: EngineInterface, view: ViewContext, panel: FilesPanelJson) {
  const { Box, Text } = view.elements
  const paths = filesOf(panel)
  return (
    <Box key="files-body" flexDirection="column" gap={1}>
      {panel.mode !== 'files' && !paths.length ? <Text mono size="footnote" color={BRAND.muted}>No files generated yet</Text> : null}
      {panel.mode === 'list' ? (
        <Box key="file-list" flexDirection="column" rowGap={1} paddingX={2}>
          {paths.map(entry => FileRowView($, view, entry.path, entry.path))}
        </Box>
      ) : null}
      {panel.mode === 'folder' ? FolderGroupsView($, view, panel) : null}
      {panel.mode === 'files' ? FileTabsView($, view, panel) : null}
    </Box>
  )
}

function FileModesView($: EngineInterface, view: ViewContext, panel: FilesPanelJson) {
  const { Box, Button, Text } = view.elements
  return (
    <Box key="modes" flexDirection="row" columnGap={2}>
      {FILE_MODES.map(mode => (
        <Button key={`mode-${mode}`} plain onPress={() => chooseFilesMode($, mode)}>
          <Text mono size="footnote" weight={panel.mode === mode ? 'semibold' : 'regular'} color={panel.mode === mode ? BRAND.accentText : BRAND.muted}>
            {mode}
          </Text>
        </Button>
      ))}
    </Box>
  )
}

const locationOf = (violation: ViolationJson): string => (violation.line ? `${violation.location}:${violation.line}` : violation.location)

// A location with no source has no file to open, so only one with source lines is a link.
function ViolationLocationView($: EngineInterface, view: ViewContext, panel: ReportPanelJson, rule: ReportRuleJson, violation: ViolationJson) {
  const { Text } = view.elements
  const location = locationOf(violation)
  if (!violation.source.length) {
    return (
      <Text mono size="footnote" weight="medium" color={BRAND.text}>
        {location}
      </Text>
    )
  }
  return LinkButtonView(view, `open-${location}-${violation.message}`, location, BRAND.text, () => openFileAtLine($, panel.ticket, rule.fidelity, violation.location, violation.line ?? 1))
}

function SourceLineView(view: ViewContext, violation: ViolationJson, entry: SourceLineJson, numberWidth: number) {
  const { Box, Text } = view.elements
  const isFailing = entry.number === violation.line
  return (
    <Box key={isFailing ? `failing-line-${entry.number}` : `line-${entry.number}`} flexDirection="row" columnGap={1} backgroundColor={isFailing ? BRAND.errorWash : BRAND.canvas}>
      {ColorBarView(view, isFailing ? BRAND.error : BRAND.canvas)}
      <Text mono size="footnote" tabular color={BRAND.muted}>
        {String(entry.number).padStart(numberWidth)}
      </Text>
      <Text mono size="footnote" wrap="truncate-end" color={BRAND.text}>
        {entry.text || ' '}
      </Text>
    </Box>
  )
}

function ViolationSourceView(view: ViewContext, violation: ViolationJson) {
  const { Box } = view.elements
  const numberWidth = String(violation.source.at(-1)?.number ?? 0).length
  return (
    <Box key="violation-source" flexDirection="column" backgroundColor={BRAND.canvas}>
      {violation.source.map(entry => SourceLineView(view, violation, entry, numberWidth))}
    </Box>
  )
}

function ViolationView($: EngineInterface, view: ViewContext, panel: ReportPanelJson, rule: ReportRuleJson, violation: ViolationJson) {
  const { Box, Text } = view.elements
  const isOff = isLocked(view, panel.ticket)
  return (
    <Box key={`violation-${rule.name}-${violation.location}-${violation.line}-${violation.message}`} flexDirection="column" borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.surface}>
      <Box key="violation-head" flexDirection="row" columnGap={2} paddingX={1}>
        <Box key="violation-words" flexDirection="column" flexGrow={1} flexShrink={1}>
          {ViolationLocationView($, view, panel, rule, violation)}
          <Text color={BRAND.error}>{violation.message}</Text>
        </Box>
        {ActionButtonView(view, `fix-${rule.fidelity}-${rule.name}-${locationOf(violation)}-${violation.message}`, 'Fix', isOff ? null : () => fixViolation($, rule.fidelity, rule.name, locationOf(violation)), true)}
      </Box>
      {violation.source.length ? ViolationSourceView(view, violation) : null}
    </Box>
  )
}

function RuleView($: EngineInterface, view: ViewContext, panel: ReportPanelJson, rule: ReportRuleJson) {
  const { Box, Button, Text } = view.elements
  const isOff = isLocked(view, panel.ticket)
  const place = `${rule.fidelity}/${rule.name}`
  const isOpen = !panel.closedRules.includes(place)
  return (
    <Box key={`rule-${place}`} flexDirection="column" rowGap={1}>
      <Box key="rule-head" flexDirection="row" justifyContent="space-between" columnGap={2}>
        <Box key="rule-words" flexDirection="column" flexShrink={1}>
          <Button key={`rule-toggle-${place}`} plain onPress={() => toggleRule($, place)}>
            <Text mono weight="semibold" color={BRAND.text} hover={{ color: BRAND.accentText }}>
              {isOpen ? '▾' : '▸'} {rule.name}{' '}
            </Text>
            <Text mono size="footnote" weight="medium" color={BRAND.error}>
              {countOf(rule.count, 'violation')}
            </Text>
          </Button>
          {rule.description ? <Text color={BRAND.muted}>{rule.description}</Text> : null}
        </Box>
        {ActionButtonView(view, `fix-all-${place}`, 'Fix all', isOff ? null : () => fixRule($, rule.fidelity, rule.name))}
      </Box>
      {isOpen ? rule.violations.map(violation => ViolationView($, view, panel, rule, violation)) : null}
    </Box>
  )
}

function ReportBodyView($: EngineInterface, view: ViewContext, panel: ReportPanelJson) {
  const { Box, Text } = view.elements
  const { report } = panel
  return (
    <Box key="report-body" flexDirection="column" gap={1} paddingX={2}>
      {report.has_saved_graph ? null : <Text color={BRAND.warning}>This report has no saved graph, so its rules are only in the report file</Text>}
      {report.has_saved_graph && !report.rules.length ? (
        <Text mono weight="semibold" color={BRAND.success}>
          No violations in this report
        </Text>
      ) : null}
      {report.rules.map(rule => RuleView($, view, panel, rule))}
    </Box>
  )
}

function HelpBodyView(view: ViewContext, panel: HelpPanelJson) {
  const { Box, Markdown, Text } = view.elements
  const { help } = panel
  return (
    <Box key="help-body" flexDirection="column" gap={2} paddingX={2}>
      <Markdown text={help.overview} />
      {help.guidance ? (
        <Box key="help-guidance" flexDirection="column" gap={1}>
          {SectionTitleView(view, 'GUIDANCE')}
          <Markdown text={help.guidance} />
        </Box>
      ) : null}
      {help.rules.length ? (
        <Box key="help-rules" flexDirection="column" gap={1}>
          {SectionTitleView(view, help.fidelity ? 'RULES' : 'SHARED RULES')}
          {help.rules.map(rule => (
            <Box key={`help-rule-${rule.slug}`} flexDirection="column">
              <Text mono size="footnote" weight="semibold" color={BRAND.text}>
                {rule.slug}
              </Text>
              <Text color={BRAND.muted}>{rule.text}</Text>
            </Box>
          ))}
        </Box>
      ) : null}
    </Box>
  )
}

function bodyOf($: EngineInterface, view: ViewContext, panel: SidePanelJson) {
  if (panel.kind === 'files') return FilesBodyView($, view, panel)
  if (panel.kind === 'report') return ReportBodyView($, view, panel)
  return HelpBodyView(view, panel)
}

function ReportStatView({ elements: { Box, Text } }: ViewContext, key: string, count: number, label: string, color: string) {
  return (
    <Box key={key} flexDirection="column" alignItems="flex-end">
      <Text size="title" weight="bold" tabular color={color}>
        {count}
      </Text>
      <Text mono size="caption" color={BRAND.muted}>
        {label}
      </Text>
    </Box>
  )
}

function HelpHeadView({ elements: { Box, Text } }: ViewContext, { help }: HelpPanelJson) {
  const practice = PRACTICES.find(entry => entry.key === help.practice)
  return [
    <Text size="title" weight="bold" color={BRAND.text}>
      {help.fidelity ? help.fidelity.replaceAll('_', '-') : practice?.name}
    </Text>,
    <Box key="help-place" flexDirection="row" columnGap={1}>
      <Text mono size="footnote" weight="semibold" color={practice?.color ?? BRAND.text}>
        {practice?.name}
      </Text>
      <Text mono size="footnote" color={BRAND.muted}>
        {help.stage || 'Practice overview'}
      </Text>
    </Box>,
  ]
}

function HeadWordsView($: EngineInterface, view: ViewContext, panel: SidePanelJson) {
  const { Text } = view.elements
  if (panel.kind === 'files') {
    return [
      <Text mono size="footnote" color={BRAND.text}>
        {panel.slugs.map(guidanceSlug).join(', ')}
      </Text>,
      FileModesView($, view, panel),
    ]
  }
  if (panel.kind === 'help') return HelpHeadView(view, panel)
  return [
    <Text size="title" weight="bold" color={BRAND.text}>
      {panel.fidelity ? practiceOf(panel.fidelity)?.name ?? panel.fidelity : panel.ticket}
    </Text>,
    <Text mono size="footnote" color={BRAND.muted}>
      {panel.report.path}
    </Text>,
  ]
}

function HeadControlsView($: EngineInterface, view: ViewContext, panel: SidePanelJson) {
  const { Box, Link } = view.elements
  const violations = panel.kind === 'report' ? panel.report.rules.reduce((total, rule) => total + rule.count, 0) : 0
  return (
    <Box key="panel-controls" flexDirection="row" columnGap={1} alignItems="flex-start" flexShrink={0}>
      {panel.kind === 'report' ? ReportStatView(view, 'report-violations', violations, 'violations', BRAND.error) : null}
      {panel.kind === 'report' ? ReportStatView(view, 'report-rules', panel.report.rules.length, 'rules hit', BRAND.text) : null}
      {panel.kind === 'help' ? <Link href={panel.help.href} label="Forge" /> : null}
      {ExpandToggleView(view, `panel-expand-${panel.kind}`, panel.isExpanded, () => togglePanelExpanded($, panel.kind))}
      {ActionButtonView(view, `panel-close-${panel.kind}`, '×', () => closePanel($, panel.kind))}
    </Box>
  )
}

function PanelHeadView($: EngineInterface, view: ViewContext, panel: SidePanelJson) {
  const { Box } = view.elements
  return (
    <Box key="panel-head" flexDirection="row" justifyContent="space-between" columnGap={2} paddingX={2} paddingY={1} flexShrink={0} backgroundColor={BRAND.surface}>
      <Box key="panel-words" flexDirection="column" flexShrink={1}>
        {SectionTitleView(view, PANEL_TITLES[panel.kind] ?? '')}
        {HeadWordsView($, view, panel)}
      </Box>
      {HeadControlsView($, view, panel)}
    </Box>
  )
}

function SidePanelView($: EngineInterface, view: ViewContext, panel: SidePanelJson, width: number) {
  const { elements, hasSurfaceModules } = view
  const { Box } = elements
  const Client = hasSurfaceModules ? (elements as ElementTable<'desktop'>).Client : null
  return (
    <Box key={`panel-${panel.kind}`} flexDirection="row" width={width} flexShrink={0} backgroundColor={BRAND.canvas}>
      {Client ? (
        <Client
          key={`panel-grip-${panel.kind}`}
          module="./panel-grip.tsx"
          props={{ panel: panel.kind, width, color: BRAND.idle, hoverColor: BRAND.accent }}
          width={1}
          height="100%"
        />
      ) : null}
      <Box key="panel-body" flexDirection="column" flexGrow={1} gap={1} overflow="hidden">
        {PanelHeadView($, view, panel)}
        {bodyOf($, view, panel)}
      </Box>
    </Box>
  )
}

export const expandedPanel = ({ panels }: ViewContext): SidePanelJson | undefined => panels.find(panel => panel.isExpanded)

export function SidePanelsView($: EngineInterface, view: ViewContext) {
  const widths = panelWidthsOf(view)
  return view.panels.map((panel, index) => SidePanelView($, view, panel, widths[index] ?? panel.width))
}
