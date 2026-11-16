import { createConnection } from "node:net";
import { scenario, story } from "stories/story-test";

story('Probe Port', () => {
  scenario('a person probes a port', ({ given }) => {
    given('a port nothing listens on', () => {
      createConnection(47999);
    });
  });
});
