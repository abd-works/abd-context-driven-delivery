// What the prompt-queue mod runs against inside the canvas. The mod itself (prompt-queue.ts, plan-steps.ts,
// queue-order.ts, and the icons of icon-button-view.tsx) is bundled unchanged; these are the stand-ins for what the
// canvas does not have: Claude Code's plugin state (`claude-code`'s atom, read and update), the cdd server that keeps
// the queue (tools/prompt_queue/prompt_queue.py), the prompt box, and the model.

// `claude-code`: an atom names a stored value; read and update reach it through the engine, which holds the values.
const claudeCode = {
  atom: (spec, initial) => ({ key: spec.key, initial }),
  read: async ($, atom) => $.store.read(atom),
  update: async ($, atom, change) => $.store.update(atom, change),
};

// The plugin's stored values, by the key each atom names, telling the screen each time one changes.
class CanvasStore {
  constructor(changed) {
    this.values = new Map();
    this.changed = changed;
  }
  read(atom) {
    return this.values.has(atom.key) ? this.values.get(atom.key) : atom.initial;
  }
  update(atom, change) {
    this.values.set(atom.key, change(this.read(atom)));
    this.changed();
  }
  seed(values) {
    Object.entries(values).forEach(([key, value]) => this.values.set(key, value));
    this.changed();
  }
  held(key) {
    return this.values.get(key);
  }
}

// The cdd server's prompt-queue tools, as prompt_queue.py answers them: each answers the queue, or refuses a prompt id
// the queue does not hold with the server's own words.
class CanvasQueueServer {
  constructor(chat) {
    this.chat = chat;
    this.prompts = [];
    this.made = 0;
  }
  call(tool, args) {
    const operation = tool.replace(/^prompt-queue\./, '');
    try {
      this.prompts = this[operation](args);
      return { isError: false, content: [{ text: JSON.stringify({ chat: this.chat, prompts: this.prompts }) }] };
    } catch (refused) {
      return { isError: true, content: [{ text: refused.message }] };
    }
  }
  holding(prompt) {
    if (!this.prompts.some(held => held.id === prompt)) throw new Error(`no prompt '${prompt}' is on the queue: it was sent or removed`);
    return this.prompts;
  }
  changing(prompt, change) {
    return this.holding(prompt).map(held => (held.id === prompt ? change(held) : held));
  }
  newId() {
    this.made += 1;
    return `canvas${String(this.made).padStart(4, '0')}`;
  }
  show() { return this.prompts; }
  add({ text }) { return this.add_all({ texts: [text] }); }
  add_all({ texts }) {
    return [...this.prompts, ...texts.filter(text => text.trim()).map(text => ({ id: this.newId(), text: text.trim() }))];
  }
  edit({ prompt, text }) { return this.changing(prompt, held => ({ ...held, text: text.trim() })); }
  move({ prompt, to }) {
    const held = this.holding(prompt);
    const moving = held.find(item => item.id === prompt);
    const rest = held.filter(item => item.id !== prompt);
    rest.splice(Math.max(0, Math.min(to, rest.length)), 0, moving);
    return rest;
  }
  remove({ prompt }) { return this.holding(prompt).filter(item => item.id !== prompt); }
  clear() {
    const unfinished = this.prompts.filter(item => !item.is_done);
    return unfinished.length === this.prompts.length ? [] : unfinished;
  }
  done({ prompt }) { return this.changing(prompt, held => ({ ...held, is_done: true })); }
  reopen({ prompt }) {
    return this.changing(prompt, held => ({ ...held, is_done: false, ...(held.steps ? { steps: held.steps.map(step => ({ ...step, state: 'pending' })) } : {}) }));
  }
  assign({ prompt, robot }) {
    return this.changing(prompt, ({ robot: _given, ...held }) => (robot.trim() ? { ...held, robot: robot.trim() } : held));
  }
  set_steps({ prompt, steps }) {
    return this.changing(prompt, held => ({ ...held, steps: steps.map(step => ({ text: step.text.trim(), state: step.state })) }));
  }
  add_interruption({ prompt, text }) {
    return this.changing(prompt, held => ({ ...held, is_done: false, steps: [...(held.steps || []), { text: `[interruption] ${text.trim()}`, state: 'pending' }] }));
  }
}

// The canvas has no model. Placing a draft with + puts the whole draft on the queue as one card; grouping for
// sub-agents gives the cards to robots two at a time, in queue order, as the observed demo had four robots of two.
const CARDS_PER_ROBOT = 2;
const canvasModel = {
  fork: async () => ({ isAnswered: false, reason: 'the canvas has no model to place the draft; Alt+Enter queues it as it is' }),
  place: draft => JSON.stringify([{ card: draft.trim() }]),
  complete: async ({ prompt }) => {
    const texts = JSON.parse(prompt);
    const tasks = [];
    for (let at = 0; at < texts.length; at += CARDS_PER_ROBOT) {
      tasks.push({ description: `Cards ${at + 1} to ${Math.min(at + CARDS_PER_ROBOT, texts.length)}`, prompts: texts.slice(at, at + CARDS_PER_ROBOT) });
    }
    return { isAnswered: true, text: JSON.stringify(tasks) };
  },
};

// The engine the mod's functions take as `$`: the plugin's store, the stand-in server, the prompt box, and the chat,
// which keeps what was sent to it so the screen can show it.
class CanvasEngine {
  constructor(changed) {
    this.store = new CanvasStore(changed);
    this.server = new CanvasQueueServer('canvas-chat');
    this.draft = '';
    this.sent = [];
    const engine = this;
    this.session = { id: async () => engine.server.chat, root: async () => '' };
    this.mcp = { call: async (_server, tool, args) => engine.server.call(tool, args) };
    this.prompt = {
      read: async () => ({ text: engine.draft }),
      fill: async ({ text, mode }) => { engine.draft = mode === 'replace' ? text : engine.draft + text; changed(); },
      submit: async ({ text }) => { engine.sent.push(text); changed(); },
      media: async () => ({ unreadable: 'the canvas holds no pasted images' }),
    };
    this.model = {
      fork: async ({ prompt }) => (prompt.includes(engine.draft.trim()) && engine.draft.trim()
        ? { isAnswered: true, text: canvasModel.place(engine.draft) }
        : canvasModel.fork()),
      complete: canvasModel.complete,
    };
    this.command = { run: async ({ command }) => { engine.sent.push(`/${command}`); changed(); } };
    this.agent = { spawn: async ({ description }) => { engine.sent.push(`Sub-agent started: ${description}`); changed(); return {}; } };
    this.clock = { after: (milliseconds, then) => setTimeout(then, milliseconds) };
  }
  // A scenario's Givens: the queue the server holds, and the plugin values its view starts from.
  load(fixture) {
    this.server.prompts = fixture.queue.prompts;
    this.draft = '';
    this.sent = [];
    this.store.seed(Object.assign({ queue: fixture.queue }, fixture.view));
  }
}
