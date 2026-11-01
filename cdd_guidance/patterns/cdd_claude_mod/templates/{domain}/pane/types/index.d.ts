// {Domain}Json is exactly what {Domain}.to_json() returns. It is the agreement between Python and the mod.
export type {Domain}Json = {
  name: string
  next_action: string | null
}

declare module 'claude-code' {
  interface PluginState {
    'cdd-{domain}': {
      {domain}: {Domain}Json | null
    }
  }
}
