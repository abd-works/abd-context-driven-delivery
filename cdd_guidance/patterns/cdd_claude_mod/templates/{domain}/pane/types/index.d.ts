// {Object}Json is exactly what {Object}.to_json() returns. It is the agreement between Python and the mod.
export type {Object}Json = {
  name: string
  next_action: string | null
}

declare module 'claude-code' {
  interface PluginState {
    'cdd-{domain}': {
      {object}: {Object}Json | null
    }
  }
}
