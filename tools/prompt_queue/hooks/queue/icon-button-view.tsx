import type { ElementTable } from 'claude-code'

/** The desktop's own greys, sampled from its prompt box: the card, its placeholder text, and a key cap's grey behind buttons. */
export const LOOK = { muted: '#9B9BA8', accent: '#E5531A', card: '#303030', placeholder: '#8C8C8C', keyCap: '#3F3F3F', popover: '#1C1C1E' }

/** About one line of text tall, in the desktop's pixels. */
const ICON_PIXELS = 16

export type Icon = { key: string; svg: (colour: string) => string; glyph: string; tip: string; isOn?: boolean }

/**
 * An image the person clicks; its words are the image's alt text. A Button holds only text, so a see-through
 * Button lies over the image; a surface with no Svg draws the glyph instead.
 */
export function IconButtonView(elements: ElementTable, icon: Icon, onPress: () => unknown) {
  const { Box, Button, Text } = elements
  const colour = icon.isOn ? LOOK.accent : LOOK.muted
  const image = 'Svg' in elements
    ? <elements.Svg source={icon.svg(colour)} alt={icon.tip} width={ICON_PIXELS} height={ICON_PIXELS} />
    : <Text color={colour}>{icon.glyph}</Text>

  return (
    <Box key={`${icon.key}-box`}>
      {image}
      <Box position="absolute" top={0} left={0}>
        <Button key={icon.key} plain label=" " onPress={onPress} />
      </Box>
    </Box>
  )
}

const svgOf = (colour: string, body: string) =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none" stroke="${colour}" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`

/**
 * Two cards behind a front card that carries the count, so the stack says how many are queued. The count is drawn
 * as line segments, not `<text>`: drawn with `<text>`, the stack never showed in the desktop chat bar.
 */
export const stackSvgOf = (count: number) => (colour: string) =>
  svgOf(colour, '<path d="M4.5 2h7M3 4.5h10"/><rect x="1.5" y="6.5" width="13" height="8" rx="1.5"/>'
    + `<path stroke-width="1.1" d="${countPath(Math.min(count, 99))}"/>`)

/** The segments each digit lights, as on a seven-segment display: a top, b-c right, d bottom, e-f left, g middle. */
const DIGIT_SEGMENTS = ['abcdef', 'bc', 'abged', 'abgcd', 'fgbc', 'afgcd', 'afgedc', 'abc', 'abcdefg', 'abcdfg']

const DIGIT_WIDTH = 2.4
const DIGIT_GAP = 1.4
const DIGIT_TOP = 8.5
const DIGIT_HEIGHT = 4.4

function countPath(count: number): string {
  const digits = String(count)
  const span = digits.length * DIGIT_WIDTH + (digits.length - 1) * DIGIT_GAP
  const left = 8 - span / 2

  return [...digits].map((digit, index) => digitPath(Number(digit), left + index * (DIGIT_WIDTH + DIGIT_GAP))).join('')
}

function digitPath(digit: number, x: number): string {
  const right = x + DIGIT_WIDTH
  const middle = DIGIT_TOP + DIGIT_HEIGHT / 2
  const bottom = DIGIT_TOP + DIGIT_HEIGHT
  const segments: Record<string, string> = {
    a: `M${x} ${DIGIT_TOP}H${right}`,
    b: `M${right} ${DIGIT_TOP}V${middle}`,
    c: `M${right} ${middle}V${bottom}`,
    d: `M${x} ${bottom}H${right}`,
    e: `M${x} ${middle}V${bottom}`,
    f: `M${x} ${DIGIT_TOP}V${middle}`,
    g: `M${x} ${middle}H${right}`,
  }

  return [...(DIGIT_SEGMENTS[digit] ?? '')].map(segment => segments[segment]).join('')
}

export const ADD_SVG = (colour: string) => svgOf(colour, '<circle cx="8" cy="8" r="6"/><path d="M8 5v6M5 8h6"/>')

export const PLAY_SVG = (colour: string) => svgOf(colour, '<path d="M5 3.5v9l7.5-4.5z"/>')

export const PAUSE_SVG = (colour: string) => svgOf(colour, '<path d="M5.5 3.5v9M10.5 3.5v9"/>')

export const SUB_AGENTS_SVG = (colour: string) =>
  svgOf(colour, '<circle cx="8" cy="3" r="1.6"/><circle cx="3" cy="13" r="1.6"/><circle cx="8" cy="13" r="1.6"/>'
    + '<circle cx="13" cy="13" r="1.6"/><path d="M8 4.6v6.8M8 7.5 3 11.4M8 7.5l5 3.9"/>')

export const CLEAR_SVG = (colour: string) =>
  svgOf(colour, '<path d="M3 4.5h10M6.5 4.5V3h3v1.5M4.5 4.5l.7 9h5.6l.7-9M7 7v4M9 7v4"/>')

/** Claude-orange shades, one for each sub-agent's robot in turn. */
const ROBOT_ORANGES = ['#D97757', '#E5531A', '#F0883E', '#C2410C', '#FB923C', '#EA580C']
/** Robot eyes, one look for each sub-agent in turn: round, square, a visor, winking. */
const ROBOT_EYES = [
  '<circle cx="6" cy="8" r="1" fill="#1F1F1F"/><circle cx="10" cy="8" r="1" fill="#1F1F1F"/>',
  '<rect x="5" y="7" width="2" height="2" fill="#1F1F1F"/><rect x="9" y="7" width="2" height="2" fill="#1F1F1F"/>',
  '<rect x="4.5" y="7.2" width="7" height="1.6" rx="0.8" fill="#1F1F1F"/>',
  '<circle cx="6" cy="8" r="1" fill="#1F1F1F"/><path d="M9 8h2" stroke="#1F1F1F" stroke-width="1"/>',
]
/** Robot antennas, one for each sub-agent in turn: a ball, two prongs, a bolt. */
const ROBOT_ANTENNAS = [
  '<path d="M8 4V2" stroke="ORANGE"/><circle cx="8" cy="1.6" r="1" fill="ORANGE"/>',
  '<path d="M6 4L5 1.5M10 4l1-2.5" stroke="ORANGE"/>',
  '<path d="M8.5 1L7 3h2l-1.5 2" stroke="ORANGE"/>',
]

/** The robot on top of a sub-agent's column: Claude orange, with its own shade, eyes and antenna for its place. */
export function robotSvgOf(place: number): string {
  const orange = ROBOT_ORANGES[place % ROBOT_ORANGES.length]!
  const eyes = ROBOT_EYES[place % ROBOT_EYES.length]!
  const antenna = ROBOT_ANTENNAS[place % ROBOT_ANTENNAS.length]!.replaceAll('ORANGE', orange)
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" stroke-width="1.2" stroke-linecap="round">'
    + `${antenna}<rect x="3" y="4" width="10" height="8" rx="2" fill="${orange}"/>${eyes}`
    + `<path d="M6.5 10.5h3" stroke="#1F1F1F" stroke-width="0.9"/><rect x="5" y="12.5" width="6" height="2.5" rx="0.8" fill="${orange}"/></svg>`
}
