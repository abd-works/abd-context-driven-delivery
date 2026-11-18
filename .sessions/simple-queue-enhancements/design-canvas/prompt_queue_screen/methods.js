domain() {
return typeof QueueCanvas !== 'undefined' ? QueueCanvas.mod : null;
}
queueEngine() {
if (!this.engine) {
this.engine = QueueCanvas.engine(() => this.redraw());
this.redraw();
}
return this.engine;
}
redraw() {
if (this.redrawing) return;
this.redrawing = true;
Promise.resolve().then(() => {
this.redrawing = false;
return this.domain().currentQueue(this.engine);
}).then((queueState) => this.setState({ queueState: queueState }));
}
fromFixture(repositories) {
const engine = this.queueEngine();
engine.load(repositories);
return this.domain().currentQueue(engine).then((queueState) => ({ queueState: queueState }));
}
act(run) {
return () => { run(this.domain(), this.queueEngine()); };
}
svgSource(svg) {
return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
}
iconOf(icon, press) {
const look = this.domain().LOOK;
return { src: this.svgSource(icon.svg(icon.isOn ? look.accent : look.muted)), tip: icon.tip, press: press };
}
bandVals(queueState) {
const mod = this.domain();
const open = queueState.isExpanded;
return {
stack: this.iconOf(mod.stackIcon(queueState), this.act((m, $) => m.toggleExpanded($))),
add: this.iconOf(mod.ADD_ICON, this.act((m, $) => m.queueDraft($))),
openIcons: open ? [
this.iconOf(mod.playIcon(queueState), this.act((m, $) => m.togglePlaying($))),
this.iconOf(mod.subAgentsIcon(queueState), this.act((m, $) => m.toggleSubAgentMode($))),
this.iconOf(mod.CLEAR_ICON, this.act((m, $) => m.clearQueue($))),
] : [],
};
}
groupsOf(queueState) {
const mod = this.domain();
const prompts = queueState.queue.prompts;
if (!queueState.isExpanded || queueState.queue.isEmpty) return [];
if (!(queueState.isSubAgentMode && queueState.tasks.length > 0)) return [this.groupOf(queueState, prompts, null)];
return queueState.tasks.map((task, place) => this.groupOf(queueState, mod.robotPromptsOf(prompts, task, place), { task: task, place: place }));
}
groupOf(queueState, items, robot) {
const mod = this.domain();
const pointer = mod.pointerOf(items);
const isCollapsed = robot !== null && queueState.collapsedAgents.includes(robot.place);
const group = {
cls: 'pq-group' + (isCollapsed ? ' pq-collapsed' : ''),
hasRobot: robot !== null,
isCollapsed: isCollapsed,
isOpen: !isCollapsed,
cards: isCollapsed ? [] : items.map((prompt, place) => this.cardOf(queueState, prompt, place === pointer, items, robot !== null)),
isPointerAfter: !isCollapsed && items.length > 0 && pointer === items.length,
arrowsAfter: [this.control('▲', 'Open the done card above again', (m, $) => m.movePointerUp($, items))],
};
return robot === null ? group : Object.assign(group, this.robotOf(robot, items));
}
robotOf(robot, items) {
const mod = this.domain();
const name = mod.agentNameOf(robot.task, robot.place);
return {
name: name,
robotTip: name + ', a robot: press to fold or open its queue',
robotSrc: this.svgSource(mod.robotSvgOf(robot.place)),
toggle: this.act((m, $) => m.toggleCollapsedAgent($, robot.place)),
progress: items.filter((item) => item.is_done).length + '/' + items.length,
};
}
control(label, tip, run) {
return { label: label, tip: tip, press: this.act(run) };
}
cardOf(queueState, prompt, isPointer, items, isInColumn) {
const mod = this.domain();
const index = queueState.queue.prompts.indexOf(prompt);
const isEditing = prompt.id === queueState.editingId;
const isFinished = Boolean(prompt.is_done);
const progress = mod.progressOf(prompt.steps);
const steps = prompt.steps || [];
const stepPointer = mod.stepPointerOf(steps);
const attachments = prompt.attachments || [];
return {
showProgress: progress !== '',
progress: progress,
showAddTask: progress === '' && !isFinished && !isPointer,
toggleSteps: this.act((m, $) => m.toggleSteps($, prompt.id)),
addTask: this.act((m, $) => m.addStep($, prompt)),
hasAttachments: attachments.length > 0,
attached: '📎' + attachments.length,
boxClass: 'pq-textbox' + (isPointer ? ' pq-pointed' : ''),
pillClass: 'pq-pill' + (isEditing ? ' pq-editing' : isPointer ? ' pq-working' : '') + (isFinished ? ' pq-finished' : ''),
text: prompt.text,
label: (index + 1) + '. ' + prompt.text.replace(/\s+/g, ' ') + (isEditing ? '  (editing)' : ''),
press: this.act((m, $) => (isInColumn ? m.toggleOpenedCard($, prompt.id) : m.editPrompt($, prompt))),
isPointer: isPointer,
arrows: [this.control('▲', 'Open the done card above again', (m, $) => m.movePointerUp($, items)),
this.control('▼', 'Mark this card done', (m, $) => m.movePointerDown($, items))],
hasHoverButtons: !isInColumn,
isOpened: isInColumn && prompt.id === queueState.openedId,
buttons: this.cardButtons(prompt, index),
showSteps: queueState.openSteps.includes(prompt.id) && steps.length > 0,
steps: steps.map((step, place) => this.stepOf(prompt, step, place, place === stepPointer)),
isStepPointerAfter: steps.length > 0 && stepPointer === steps.length,
stepArrowsAfter: [this.control('▲', 'Work the done step above again', (m, $) => m.moveStepPointerUp($, prompt))],
};
}
cardButtons(prompt, index) {
return [
this.control('↵', 'Send this prompt to the chat now', (m, $) => m.sendNow($, prompt)),
this.control('✎', 'Edit this prompt in the prompt box', (m, $) => m.editPrompt($, prompt)),
this.control('↑', 'Move up one place', (m, $) => m.movePrompt($, index, index - 1)),
this.control('↓', 'Move down one place', (m, $) => m.movePrompt($, index, index + 1)),
this.control('✕', 'Take this prompt off the queue', (m, $) => m.removePrompt($, prompt.id)),
];
}
stepOf(prompt, step, place, isPointer) {
const mod = this.domain();
return {
label: mod.STEP_MARK[step.state] + ' ' + step.text,
cls: 'pq-step-text' + (step.state === 'done' ? ' pq-done' : step.state === 'in_progress' ? ' pq-in-progress' : ''),
isPointer: isPointer,
arrows: [this.control('▲', 'Work the done step above again', (m, $) => m.moveStepPointerUp($, prompt)),
this.control('▼', 'Mark this step done', (m, $) => m.moveStepPointerDown($, prompt))],
buttons: [
this.control('↵', 'Send this step to the chat now', (m, $) => m.sendStepNow($, prompt, place)),
this.control('✎', 'Edit this step: an empty prompt box takes its text, a draft replaces it', (m, $) => m.editStep($, prompt, place)),
this.control('↑', 'Move up one place', (m, $) => m.moveStep($, prompt, place, place - 1)),
this.control('↓', 'Move down one place', (m, $) => m.moveStep($, prompt, place, place + 1)),
this.control('✕', 'Take this step off', (m, $) => m.removeStep($, prompt, place)),
],
};
}
typeDraft(event) {
this.queueEngine().draft = event.target.value;
this.forceUpdate();
}
draftKey(event) {
if (event.key !== 'Enter' || !event.altKey) return;
event.preventDefault();
const $ = this.queueEngine();
const text = $.draft;
this.domain().queueByKey($, text).then(() => $.prompt.fill({ text: '', mode: 'replace' }));
}
queueVals() {
const mod = this.domain();
const queueState = this.state && this.state.queueState;
if (!mod || !queueState) {
if (mod) this.queueEngine();
return { isExpanded: false, groups: [], boxClass: 'pq-box', hasNotice: false, stack: {}, add: {}, openIcons: [], look: {}, sent: [], hasSent: false, hasFailure: false, draft: '' };
}
const $ = this.engine;
const failure = $.store.held('failure');
return Object.assign(this.bandVals(queueState), {
look: mod.LOOK,
taskColumns: mod.TASK_BUTTON_COLUMNS,
pointerColumns: mod.POINTER_COLUMNS,
addColumns: mod.ADD_COLUMNS,
robotPixels: mod.ROBOT_PIXELS,
isExpanded: queueState.isExpanded,
boxClass: 'pq-box' + (queueState.isExpanded ? ' pq-open' : ''),
groups: this.groupsOf(queueState),
hasNotice: queueState.notice !== '',
notice: queueState.notice,
sent: $.sent,
hasSent: $.sent.length > 0,
hasFailure: Boolean(failure),
failure: failure ? failure.failure : '',
draft: $.draft,
typeDraft: (event) => this.typeDraft(event),
draftKey: (event) => this.draftKey(event),
});
}
