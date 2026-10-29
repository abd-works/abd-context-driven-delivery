"""The fixture bar every fixture-driven Claude Design screen shows, and the methods behind it.

Every screen shows its story's scenario picker. Opened on its own it also shows *Load from fixture*; inside the story
explorer the screen loads the explorer's selected scenario itself, and picking another scenario loads it at once and
moves the explorer's tree to it. *Paste seed data* is a list box: the values any scenario of
the story enters (an outline's example rows among them), and dev mode's seed paste for the screen's path. ``follow(event, story)`` moves the explorer to the next story, or lets
the link open the next screen when the screen stands alone. See ``claude_design.md``."""

BAR = '''<div style="position: absolute; top: 12px; left: 12px; display: flex; gap: 8px; align-items: center; font: 600 12px/1 ui-monospace, Consolas, monospace; z-index: 5">
<a href="/Main.dc.html" aria-label="Back to the story map" style="padding: 6px 10px; border: 1px solid #2A2A2A; border-radius: 4px; background: #0B0B0B; color: #E8E8ED; text-decoration: none">← Story map</a>
<select aria-label="Scenario" value="{{scenario}}" onChange="{{pickScenario}}" style="max-width: 420px; padding: 6px 8px; border: 1px solid #2A2A2A; border-radius: 4px; background: #0B0B0B; color: #E8E8ED">
<sc-for list="{{scenarioOptions}}" as="o" hint-placeholder-count="3"><option value="{{o.name}}">{{o.name}}</option></sc-for>
</select>
<sc-if value="{{standalone}}" hint-placeholder-val="{{ true }}">
<button type="button" onClick="{{loadFromFixture}}" style="padding: 6px 10px; border: 1px solid #E5531A; border-radius: 4px; background: #0B0B0B; color: #E8E8ED; cursor: pointer">Load from fixture</button>
</sc-if>
<sc-if value="{{canPaste}}" hint-placeholder-val="{{ false }}">
<select aria-label="Paste seed data" value="" onChange="{{pasteChoice}}" style="max-width: 320px; padding: 6px 8px; border: 1px solid #E5531A; border-radius: 4px; background: #0B0B0B; color: #E8E8ED">
<option value="">Paste seed data…</option>
<sc-for list="{{pasteOptions}}" as="p" hint-placeholder-count="3"><option value="{{p.value}}">{{p.label}}</option></sc-for>
</select>
</sc-if>
__EDIT_LINK__<span style="padding: 6px 10px; border-radius: 4px; background: #0B0B0B; color: #E5531A">{{source}}</span>
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
if (this.props.scenario && previous.scenario !== this.props.scenario) {
this.setState({ scenario: this.props.scenario });
this.followExplorer();
}
}
followExplorer() {
let tries = 0;
const scenario = this.props.scenario;
const attempt = () => { if (this.fixtures()) { this.loadFromFixture(scenario); return; } if (tries++ < 50) setTimeout(attempt, 100); };
attempt();
}
storyName() {
return this.props.story || '__STORY__';
}
scenarioName() {
return (this.state && this.state.scenario) || this.props.scenario || '__SCENARIO__';
}
loadFromFixture(chosen) {
const fixtures = this.fixtures();
const story = this.storyName();
const scenario = chosen || this.scenarioName();
if (!fixtures) { this.setState({ source: 'fixtures not loaded' }); return; }
fixtures.load(story, scenario)
.then((repositories) => Promise.resolve(this.fromFixture(repositories, scenario, fixtures.examples)))
.then((state) => this.setState(Object.assign({}, state, state && state.entered, { source: story + ' › ' + scenario })))
.catch((problem) => this.setState({ source: String(problem && problem.message || problem) }));
}
pasteSeedData() {
const paste = this.fixtures() && this.fixtures().pasteFor('__PATH__');
if (!paste) return;
const state = { source: 'pasted: ' + paste.title };
paste.fields.forEach((field) => Object.assign(state, this.paste(field)));
this.setState(state);
}
pasteScenario(scenario) {
const fixtures = this.fixtures();
if (!fixtures || !this.fromFixture) return;
Promise.resolve(this.fromFixture(fixtures.repositories(), scenario, fixtures.examples))
.then((state) => this.setState(Object.assign({}, (state && state.entered) || state, { source: 'pasted: ' + scenario })))
.catch((problem) => this.setState({ source: String(problem && problem.message || problem) }));
}
pasteChoice(value) {
if (value === 'dev-seed') { this.pasteSeedData(); return; }
if (value) this.pasteScenario(value);
}
pickScenario(scenario) {
this.setState({ scenario: scenario });
if (!this.props.go) return;
this.loadFromFixture(scenario);
this.props.go(this.storyName(), scenario);
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
const rows = this.fromFixture ? options.map((name) => ({ value: name, label: name })) : [];
const pasteOptions = paste ? rows.concat([{ value: 'dev-seed', label: 'Dev seed: ' + paste.title }]) : rows;
return {
standalone: !this.props.scenario,
inExplorer: Boolean(this.props.scenario),
scenario: this.scenarioName(),
scenarioOptions: (options.length ? options : [this.scenarioName()]).map((name) => ({ name: name })),
pickScenario: (event) => this.pickScenario(event.target.value),
loadFromFixture: () => this.loadFromFixture(),
canPaste: pasteOptions.length > 0,
pasteOptions: pasteOptions,
pasteChoice: (event) => this.pasteChoice(event.target.value),
source: (this.state && this.state.source) || 'no fixture loaded'
};
}
'''


EDIT_LINK = ('<sc-if value="{{inExplorer}}" hint-placeholder-val="{{ false }}"><a href="__ARTBOARD__" title="Edit this screen on its own artboard" '
             'style="padding: 6px 10px; border: 1px solid #E5531A; border-radius: 4px; background: #E5531A; color: #0B0B0B; text-decoration: none">Edit</a></sc-if>\n')


def bar(artboard: str = "") -> str:
    """The bar for a screen whose own artboard is *artboard* (its canvas path, e.g. ``/screens/select-plan.dc.html``).
    Inside the story explorer it adds **Edit**: the explorer draws the screen through ``dc-import``, so an edit there
    would land on the explorer; the link moves Play to the screen's own artboard, where its markup lives."""
    return BAR.replace("__EDIT_LINK__", EDIT_LINK.replace("__ARTBOARD__", artboard) if artboard else "")


def methods(story: str, scenario: str, path: str) -> str:
    return METHODS.replace('__STORY__', story).replace('__SCENARIO__', scenario).replace('__PATH__', path)


def fixture_screen(title: str, head: str, root_class: str, body: str, story: str, scenario: str, path: str,
                   own_methods: str, vals: str, width: int = 1280, height: int = 900, artboard: str = "") -> str:
    """A whole fixture-driven screen artboard: *head* (stylesheets, the fixtures script), the bar at the top of the
    ``root_class`` element, *body* inside it, and a ``DCLogic`` class with the shared methods, *own_methods* (its
    ``fromFixture`` and ``paste``), and ``renderVals`` returning the bar's values with *vals* (JS object entries;
    ``st`` is the state). *artboard* is the screen's own canvas path, for the explorer's Edit link."""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
{head}
</head>
<body>
<x-dc>
<helmet>
<style>
body{{margin:0}}
a.button-primary{{display:inline-flex;align-items:center;justify-content:center;text-decoration:none}}
</style>
</helmet>
<div class="{root_class}">
{bar(artboard)}{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"story":{{"editor":null}},"scenario":{{"editor":null}},"go":{{"editor":null}},"$preview":{{"width":{width},"height":{height}}}}}'>
class Component extends DCLogic {{
{methods(story, scenario, path)}{own_methods}renderVals() {{
const st = this.state || {{}};
return Object.assign(this.barVals(), {{
{vals}
}});
}}
}}
</script>
</body>
</html>
'''
