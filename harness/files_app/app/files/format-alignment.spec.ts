// Diagnose And Align Session Formats, as the page shows it: what the session answers for a diagnosis and an alignment
// is proved by cdd_guidance/align/format_alignment_heavy_spec.py; here, what the Diagnose and Align buttons ask of it, what
// the page shows while it waits, and what Fix hands the band of failures.
import { describe, expect, it } from 'vitest'

import type { AlignmentDiagnosisData, AlignmentGapData, AlignmentResultData } from '@cdd/align/format-alignment'

import { FormatAlignment, type AlignmentSession, type FailureBand } from './format-alignment'

const DRAWING = '.context/story-map.drawio'
const STORY_MAP = '.context/story-map.md'
const LACKS = `${DRAWING} lacks Story 'Remove Cart Line', which ${STORY_MAP} holds. Align renders ${DRAWING} from ${STORY_MAP}.`
const CONFLICT = `${STORY_MAP} and ${DRAWING} each hold what the other lacks. A person decides which is right; both files are left as they are.`
const RENDER_FAILED = `Rendering ${STORY_MAP} to whiteboard failed: NothingToRender: ${STORY_MAP} is empty`

const gap = (kind: string, message: string, isAlignable: boolean): AlignmentGapData => ({ kind, fidelity: 'stories-story-map', file: DRAWING, format: 'drawio', source: isAlignable ? STORY_MAP : '', is_alignable: isAlignable, missing_nodes: [], missing_edges: [], message })
const diagnosis = (...gaps: AlignmentGapData[]): AlignmentDiagnosisData => ({ fidelities: ['stories-story-map'], gaps, is_aligned: !gaps.length })

// The session as the page calls it: it answers the diagnosis and the alignment it is given, or refuses.
class FakeSession implements AlignmentSession {
  calls: string[] = []
  refusal = ''

  constructor(
    private readonly diagnosed: AlignmentDiagnosisData,
    private readonly result: AlignmentResultData | null = null,
  ) {}

  async diagnoseAlignment(): Promise<AlignmentDiagnosisData | null> {
    this.calls.push('diagnose')
    if (this.refusal) throw new Error(this.refusal)
    return this.diagnosed
  }

  async alignFormats(): Promise<AlignmentResultData | null> {
    this.calls.push('align')
    return this.result
  }
}

class FakeBand implements FailureBand {
  shown: { failure: string; context: string; kind: string }[] = []

  show(failure: string, context: string, kind = ''): void {
    this.shown.push({ failure, context, kind })
  }
}

function alignment(session: FakeSession) {
  const band = new FakeBand()
  return { session, band, formats: new FormatAlignment(session, band) }
}

describe('the formats of a session in the Files app', () => {
  describe('that nobody has diagnosed', () => {
    it('should show no diagnosis', () => {
      expect(alignment(new FakeSession(diagnosis())).formats.state.step).toBe('idle')
    })
  })

  describe('that a person diagnoses', () => {
    it('should say it is diagnosing until the session answers', () => {
      const { formats } = alignment(new FakeSession(diagnosis()))
      void formats.diagnose()
      expect(formats.state.step).toBe('diagnosing')
    })

    it('should show each gap the session answers', async () => {
      const { formats } = alignment(new FakeSession(diagnosis(gap('format_lacks', LACKS, true), gap('formats_conflict', CONFLICT, false))))
      await formats.diagnose()
      expect(formats.state.gaps.map(each => each.message)).toEqual([LACKS, CONFLICT])
    })

    it('should offer Align while a gap is one a render closes', async () => {
      const { formats } = alignment(new FakeSession(diagnosis(gap('format_lacks', LACKS, true))))
      await formats.diagnose()
      expect(formats.canAlign).toBe(true)
    })

    it('should not offer Align while every gap waits for a person', async () => {
      const { formats } = alignment(new FakeSession(diagnosis(gap('formats_conflict', CONFLICT, false))))
      await formats.diagnose()
      expect(formats.canAlign).toBe(false)
    })

    describe('with a session that refuses', () => {
      it('should say what the session said, and go back to waiting for a press', async () => {
        const { session, formats } = alignment(new FakeSession(diagnosis()))
        session.refusal = 'no session at .sessions/checkout-flow/session.json'
        await formats.diagnose()
        expect([formats.state.step, formats.state.problem]).toEqual(['idle', 'The formats were not diagnosed: no session at .sessions/checkout-flow/session.json'])
      })
    })
  })

  describe('that a person aligns after a diagnosis', () => {
    const aligned: AlignmentResultData = {
      aligned: [{ file: DRAWING, format: 'drawio', source: STORY_MAP, follow_up: '' }],
      failures: [{ kind: 'render_failed', file: '.context/story-map.whiteboard', message: RENDER_FAILED }],
      diagnosis: diagnosis(gap('formats_conflict', CONFLICT, false)),
    }

    it('should show the files the session rendered', async () => {
      const { formats } = alignment(new FakeSession(diagnosis(gap('format_lacks', LACKS, true)), aligned))
      await formats.diagnose()
      await formats.align()
      expect(formats.state.aligned.map(each => each.file)).toEqual([DRAWING])
    })

    it('should show the gaps still there afterwards', async () => {
      const { formats } = alignment(new FakeSession(diagnosis(gap('format_lacks', LACKS, true)), aligned))
      await formats.diagnose()
      await formats.align()
      expect(formats.state.gaps.map(each => each.kind)).toEqual(['formats_conflict'])
    })

    it('should show each failure the alignment met', async () => {
      const { formats } = alignment(new FakeSession(diagnosis(gap('format_lacks', LACKS, true)), aligned))
      await formats.diagnose()
      await formats.align()
      expect(formats.state.failures.map(each => each.message)).toEqual([RENDER_FAILED])
    })

    describe('and sends a failure to be fixed', () => {
      it('should hand the band the failure as a render failure, with the file it was writing', async () => {
        const { band, formats } = alignment(new FakeSession(diagnosis(gap('format_lacks', LACKS, true)), aligned))
        await formats.diagnose()
        await formats.align()
        formats.fixFailure(formats.state.failures[0])
        expect(band.shown).toEqual([{ failure: RENDER_FAILED, context: 'Aligning the formats of the session, writing .context/story-map.whiteboard, calling format-alignment.align_formats', kind: 'render' }])
      })
    })
  })

  describe('whose gap a person sends to be fixed', () => {
    it('should hand the band the gap in the session\'s own words, with its file', async () => {
      const { band, formats } = alignment(new FakeSession(diagnosis(gap('formats_conflict', CONFLICT, false))))
      await formats.diagnose()
      formats.fixGap(formats.state.gaps[0])
      expect(band.shown).toEqual([{ failure: CONFLICT, context: `Diagnosing the formats of the session, in ${DRAWING}, calling format-alignment.diagnose_alignment`, kind: '' }])
    })
  })

  describe('whose diagnosis a person closes', () => {
    it('should show no diagnosis again', async () => {
      const { formats } = alignment(new FakeSession(diagnosis(gap('format_lacks', LACKS, true))))
      await formats.diagnose()
      formats.close()
      expect([formats.state.step, formats.state.gaps]).toEqual(['idle', []])
    })
  })
})
