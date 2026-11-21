import type { AlignedFileData, AlignmentDiagnosisData, AlignmentFailureData, AlignmentGapData, AlignmentResultData } from '@cdd/space/session/session'
import { reasonOf } from './reason'

// What the page asks of the session: its diagnosis and its alignment (session.diagnose_alignment, session.align_formats).
export type AlignmentSession = {
  diagnoseAlignment(): Promise<AlignmentDiagnosisData | null>
  alignFormats(): Promise<AlignmentResultData | null>
}

// The band of failures under the page's head, whose Fix button sends a failure to the chat to be fixed.
export type FailureBand = { show(failure: string, context: string, kind?: 'render' | ''): void }

export type AlignmentState = {
  // idle until Diagnose is pressed; diagnosed and aligned show what the session answered last.
  step: 'idle' | 'diagnosing' | 'diagnosed' | 'aligning' | 'aligned'
  fidelities: string[]
  gaps: AlignmentGapData[]
  aligned: AlignedFileData[]
  failures: AlignmentFailureData[]
  problem: string
}

const NOTHING: AlignmentState = { step: 'idle', fidelities: [], gaps: [], aligned: [], failures: [], problem: '' }

// Diagnose and Align on the Files app: Diagnose asks the session for every gap between its formats and shows them as
// the session worded them; Align asks it to render the files a render brings in step and shows what it rendered, each
// failure it met, and the gaps still there. Which gaps there are, which a render closes and which file it reads from
// are all the session's answers; the page decides none of it. A gap or a failure goes to the band of failures, whose
// Fix sends it to the chat.
export class FormatAlignment {
  private held: AlignmentState = NOTHING
  private readonly listeners = new Set<() => void>()

  constructor(
    private readonly session: AlignmentSession,
    private readonly band: FailureBand,
  ) {}

  get state(): AlignmentState {
    return this.held
  }

  readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  get isBusy(): boolean {
    return this.held.step === 'diagnosing' || this.held.step === 'aligning'
  }

  get canAlign(): boolean {
    return !this.isBusy && this.held.gaps.some(gap => gap.is_alignable)
  }

  async diagnose(): Promise<void> {
    if (this.isBusy) return
    this.change({ ...NOTHING, step: 'diagnosing' })
    try {
      const diagnosis = await this.session.diagnoseAlignment()
      this.change({ ...NOTHING, step: 'diagnosed', fidelities: diagnosis?.fidelities ?? [], gaps: diagnosis?.gaps ?? [] })
    } catch (failure) {
      this.change({ ...NOTHING, problem: `The formats were not diagnosed: ${reasonOf(failure)}` })
    }
  }

  async align(): Promise<void> {
    if (!this.canAlign) return
    const before = this.held
    this.change({ ...before, step: 'aligning', problem: '' })
    try {
      const result = await this.session.alignFormats()
      const after = result?.diagnosis
      this.change({ step: 'aligned', fidelities: after?.fidelities ?? [], gaps: after?.gaps ?? [], aligned: result?.aligned ?? [], failures: result?.failures ?? [], problem: '' })
    } catch (failure) {
      this.change({ ...before, step: 'diagnosed', problem: `The formats were not aligned: ${reasonOf(failure)}` })
    }
  }

  fixGap(gap: AlignmentGapData): void {
    this.band.show(gap.message, `Diagnosing the formats of the session, in ${gap.file}, calling session.diagnose_alignment`, '')
  }

  fixFailure(failure: AlignmentFailureData): void {
    this.band.show(failure.message, `Aligning the formats of the session, writing ${failure.file}, calling session.align_formats`, 'render')
  }

  close(): void {
    this.change(NOTHING)
  }

  private change(state: AlignmentState): void {
    this.held = state
    this.listeners.forEach(listener => listener())
  }
}
