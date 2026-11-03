/** @jsxRuntime automatic @jsxImportSource react */
import { useState, type ReactNode } from 'react'

// The input a published argument type draws: text, a number, a checkbox, one string per line, or JSON for anything else.
export type InputKind = 'text' | 'number' | 'check' | 'list' | 'json'

export type ArgumentInput = { name: string; label: string; kind: InputKind; isRequired: boolean }

const shown = (value: unknown): string => (typeof value === 'string' ? value : JSON.stringify(value, null, 2))

// What a person typed, as the value its argument takes. An empty optional input sends nothing, so Python's default holds.
function sentValue(kind: InputKind, typed: string | boolean): unknown {
  if (kind === 'check') return typed
  const text = String(typed)
  if (text === '') return undefined
  if (kind === 'number') return Number(text)
  if (kind === 'list') return text.split('\n').filter(Boolean)
  return kind === 'json' ? JSON.parse(text) : text
}

function typedValue(kind: InputKind, value: unknown): string | boolean {
  if (kind === 'check') return value === true
  if (value === undefined || value === null) return ''
  if (kind === 'list' && Array.isArray(value)) return value.join('\n')
  return kind === 'json' ? JSON.stringify(value) : String(value)
}

function Input({ kind, value, onChange }: { kind: InputKind; value: string | boolean; onChange: (typed: string | boolean) => void }): ReactNode {
  if (kind === 'check') return <input type="checkbox" checked={value === true} onChange={event => onChange(event.target.checked)} />
  if (kind === 'list' || kind === 'json') return <textarea value={String(value)} onChange={event => onChange(event.target.value)} />
  return <input type={kind === 'number' ? 'number' : 'text'} value={String(value)} onChange={event => onChange(event.target.value)} />
}

export function ReadOnlyField({ label, value }: { label: string; value: unknown }): ReactNode {
  return (
    <div className="cdd-field">
      <span className="cdd-field-label">{label}</span>
      <span className="cdd-field-value">{shown(value)}</span>
    </div>
  )
}

// A field a domain operation changes: saving calls that operation, which answers with the object's new state.
export function EditableField({ label, kind, value, onSave }: { label: string; kind: InputKind; value: unknown; onSave: (value: unknown) => Promise<unknown> }): ReactNode {
  const [typed, setTyped] = useState(typedValue(kind, value))
  return (
    <label className="cdd-field cdd-field-editable">
      <span className="cdd-field-label">{label}</span>
      <Input kind={kind} value={typed} onChange={setTyped} />
      <button type="button" onClick={() => void onSave(sentValue(kind, typed))}>
        Save
      </button>
    </label>
  )
}

// One operation: a button when it takes no arguments of its own, a form when it does. An operation that answers with
// something other than the object's own state shows that answer.
export function OperationForm({
  label,
  inputs,
  showsResult = false,
  onRun,
}: {
  label: string
  inputs: ArgumentInput[]
  showsResult?: boolean
  onRun: (values: Record<string, unknown>) => Promise<unknown>
}): ReactNode {
  const [typed, setTyped] = useState<Record<string, string | boolean>>({})
  const [result, setResult] = useState<unknown>(undefined)
  const run = async (): Promise<void> => {
    const values = Object.fromEntries(inputs.map(input => [input.name, sentValue(input.kind, typed[input.name] ?? typedValue(input.kind, undefined))]))
    const answer = await onRun(values)
    if (showsResult) setResult(answer)
  }
  return (
    <form
      className="cdd-operation"
      onSubmit={event => {
        event.preventDefault()
        void run()
      }}
    >
      {inputs.map(input => (
        <label key={input.name} className="cdd-argument">
          <span className="cdd-field-label">
            {input.label}
            {input.isRequired ? ' *' : ''}
          </span>
          <Input kind={input.kind} value={typed[input.name] ?? typedValue(input.kind, undefined)} onChange={value => setTyped({ ...typed, [input.name]: value })} />
        </label>
      ))}
      <button type="submit">{label}</button>
      {result === undefined ? null : <pre className="cdd-result">{shown(result)}</pre>}
    </form>
  )
}
