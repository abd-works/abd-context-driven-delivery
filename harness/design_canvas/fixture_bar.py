"""The fixture bar every fixture-driven Claude Design screen shows, and the methods behind it.

Opened on its own, a screen shows its story's scenario picker and *Load from fixture*; inside the story explorer the
picker hides and the screen loads the explorer's selected scenario itself. *Paste seed data* shows wherever dev mode's
seed overlay has a paste for the screen's path. ``follow(event, story)`` moves the explorer to the next story, or lets
the link open the next screen when the screen stands alone. See ``claude_design.md``."""

BAR = '''<div style="position: absolute; top: 12px; left: 12px; display: flex; gap: 8px; align-items: center; font: 600 12px/1 ui-monospace, Consolas, monospace; z-index: 5">
<sc-if value="{{standalone}}" hint-placeholder-val="{{ true }}">
<select aria-label="Scenario" value="{{scenario}}" onChange="{{pickScenario}}" style="padding: 6px 8px; border: 1px solid #2A2A2A; border-radius: 4px; background: #0B0B0B; color: #E8E8ED">
<sc-for list="{{scenarioOptions}}" as="o" hint-placeholder-count="3"><option value="{{o.name}}">{{o.name}}</option></sc-for>
</select>
<button type="button" onClick="{{loadFromFixture}}" style="padding: 6px 10px; border: 1px solid #E5531A; border-radius: 4px; background: #0B0B0B; color: #E8E8ED; cursor: pointer">Load from fixture</button>
</sc-if>
<sc-if value="{{canPaste}}" hint-placeholder-val="{{ false }}">
<button type="button" onClick="{{pasteSeedData}}" title="{{pasteTitle}}" style="padding: 6px 10px; border: 1px solid #2A2A2A; border-radius: 4px; background: #0B0B0B; color: #E8E8ED; cursor: pointer">Paste seed data</button>
</sc-if>
<span style="padding: 6px 10px; border-radius: 4px; background: #0B0B0B; color: #E5531A">{{source}}</span>
</div>
'''

# Methods every fixture-driven screen shares. The screen supplies STORY, SCENARIO, PATH, and fromFixture(repositories, scenario)
# returning the state that scenario shows, and paste(field) mapping one pasted field into state.
METHODS = '''fixtures() {
return typeof CanvasFixtures !== 'undefined' ? CanvasFixtures : null;
}
componentDidMount() {
let tries = 0;
const wait = () => { if (this.fixtures() || tries++ > 50) { this.forceUpdate(); return; } setTimeout(wait, 100); };
wait();
if (this.props.scenario) this.followExplorer();
}
componentDidUpdate(previous) {
if (this.props.scenario && previous.scenario !== this.props.scenario) this.followExplorer();
}
followExplorer() {
let tries = 0;
const attempt = () => { if (this.fixtures()) { this.loadFromFixture(); return; } if (tries++ < 50) setTimeout(attempt, 100); };
attempt();
}
storyName() {
return this.props.story || '__STORY__';
}
scenarioName() {
return (this.state && this.state.scenario) || this.props.scenario || '__SCENARIO__';
}
loadFromFixture() {
const fixtures = this.fixtures();
const story = this.storyName();
const scenario = this.scenarioName();
if (!fixtures) { this.setState({ source: 'fixtures not loaded' }); return; }
fixtures.load(story, scenario)
.then((repositories) => Promise.resolve(this.fromFixture(repositories, scenario, fixtures.examples)))
.then((state) => this.setState(Object.assign({}, state, { source: story + ' › ' + scenario })))
.catch((problem) => this.setState({ source: String(problem && problem.message || problem) }));
}
pasteSeedData() {
const paste = this.fixtures() && this.fixtures().pasteFor('__PATH__');
if (!paste) return;
const state = { source: 'pasted: ' + paste.title };
paste.fields.forEach((field) => Object.assign(state, this.paste(field)));
this.setState(state);
}
follow(event, story) {
if (!this.props.go) return;
if (event && event.preventDefault) event.preventDefault();
this.props.go(story);
}
barVals() {
const fixtures = this.fixtures();
const options = (fixtures && fixtures.scenarios(this.storyName())) || [];
const paste = fixtures && fixtures.pasteFor('__PATH__');
return {
standalone: !this.props.scenario,
scenario: this.scenarioName(),
scenarioOptions: (options.length ? options : [this.scenarioName()]).map((name) => ({ name: name })),
pickScenario: (event) => this.setState({ scenario: event.target.value }),
loadFromFixture: () => this.loadFromFixture(),
canPaste: Boolean(paste),
pasteTitle: paste ? paste.title : '',
pasteSeedData: () => this.pasteSeedData(),
source: (this.state && this.state.source) || 'no fixture loaded'
};
}
'''


def methods(story: str, scenario: str, path: str) -> str:
    return METHODS.replace('__STORY__', story).replace('__SCENARIO__', scenario).replace('__PATH__', path)
