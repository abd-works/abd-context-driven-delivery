import { ThrowawayCddHome } from './throwaway-cdd-home'

// Playwright's global teardown: stop the cdd server the run started and remove its home.
export default function stopRunCddHome(): void {
  ThrowawayCddHome.ofRun()?.close()
}
