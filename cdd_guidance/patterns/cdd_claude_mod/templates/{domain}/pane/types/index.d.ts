// {Object}Data comes from the language adapter, generated from what {Object}.to_json() returns.
import type { {Object}Data } from '@cdd/{source-folders}/{object}'

declare module 'claude-code' {
  interface PluginState {
    'cdd-{domain}': {
      {object}: {Object}Data | null
    }
  }
}
