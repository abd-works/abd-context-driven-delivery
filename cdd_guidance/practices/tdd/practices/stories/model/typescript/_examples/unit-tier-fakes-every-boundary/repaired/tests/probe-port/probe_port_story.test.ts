import { scenario, story } from "stories/story-test";
import { silentPort } from "./probe-port.examples";

story('Probe Port', () => {
  scenario('a person probes a port', ({ given }) => {
    given('a port nothing listens on', () => {
      silentPort.probe();
    });
  });
});
