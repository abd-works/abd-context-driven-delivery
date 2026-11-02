/**
 * Runs the shared behavior through the page, with the API answered from examples, so it proves what shows up.
 */
import { ExampleApi } from 'test-utils/behavior-test/example-api'
import { playwrightTier } from 'test-utils/behavior-test/behavior-playwright'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'

import { BOARD_WITH_REPORT, FILE_ANSWERS } from './examples/files_and_reports.examples'
import { FilesAndReportsPageDriver } from './files_and_reports.page-driver'
import { filesAndReportsBehavior } from './files_and_reports.spec.shared'

itBehavesLike(
  filesAndReportsBehavior,
  playwrightTier(async page => {
    await new ExampleApi(BOARD_WITH_REPORT, FILE_ANSWERS).answerOn(page)
    return FilesAndReportsPageDriver.fromPage(page)
  }),
)
