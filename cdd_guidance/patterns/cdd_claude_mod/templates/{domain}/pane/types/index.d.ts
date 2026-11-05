// {Object}Data comes from the language adapter, generated from the properties {Object} marks with @data_field.
import type { {Object}Data } from '@cdd/{source-folders}/{object}'

declare module 'claude-code' {
  interface PluginState {
    'cdd-{domain}': {
      {object}: {Object}Data | null
    }
  }
}
