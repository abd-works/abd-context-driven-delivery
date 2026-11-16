/** The map mockup: every screen laid out on one map, with the explorer tree beside it following the current screen. */
class MapMockup {
  /** How long a navigation toast stays up. */
  static TOAST_MILLISECONDS = 1600;
  static DEFAULT_START_SCREEN = "Create Account";

  constructor(page, startScreen, expansion) {
    this.page = page;
    this.startScreen = startScreen || MapMockup.DEFAULT_START_SCREEN;
    this.toast = page.querySelector("#toast");
    this.explorer = page.querySelector("#explorer-tree");
    this.frame = page.querySelector("#story-demo-frame");
    this.mockup = page.querySelector("#mockup");
    this.tree = readExplorerTree(page);
    this.expansion = expansion;
    this.toastTimer = null;
  }

  mount() {
    this.mockup?.addEventListener("click", (event) => this._onMockupClick(event));
    this.page.querySelector("[data-reset]")?.addEventListener("click", () => this._reset());
    this.page.querySelector("[data-play-next]")?.addEventListener("click", () => this._playNext());
    bindFlowZoom(this.frame, this.mockup);
    this._showScreen(this.startScreen, false);
    return this;
  }

  _screens() {
    return [...this.page.querySelectorAll("#mockup .screen")];
  }

  _flash(message) {
    if (!this.toast) return;
    this.toast.textContent = message;
    this.toast.classList.add("show");
    clearTimeout(this.toastTimer);
    this.toastTimer = setTimeout(() => this.toast.classList.remove("show"), MapMockup.TOAST_MILLISECONDS);
  }

  _paintTree({ scrollToCurrentScreen = false } = {}) {
    const name = this.page.querySelector("#mockup .screen.current")?.getAttribute("data-slug") || "";
    this.expansion.followScreen(name, this.tree.screenKeys[name]);
    const model = { nodes: this.tree.nodes, expansion: this.expansion, currentScreen: name, scrollToCurrentScreen };
    new ScreenTree(model, this._treeHandlers()).drawInto(this.explorer);
  }

  _treeHandlers() {
    return {
      onToggle: (key) => {
        this.expansion.toggle(key);
        this._paintTree();
      },
      onScreen: (screenName) => {
        this.expansion.forgetOpenScreen();
        this._showScreen(screenName);
      },
      onStory() {},
      onScenario() {},
    };
  }

  _showScreen(name, scroll) {
    const screen = this._screens().find(
      (candidate) => candidate.getAttribute("data-slug") === name
        || candidate.querySelector("h2")?.textContent?.trim() === name,
    );
    if (!screen) return;
    this._clearCurrent();
    screen.classList.add("current");
    if (scroll !== false) {
      screen.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });
    }
    this._paintTree({ scrollToCurrentScreen: true });
  }

  _clearCurrent() {
    this.page.querySelectorAll(".screen.current").forEach((screen) => screen.classList.remove("current"));
  }

  _onMockupClick(event) {
    const goto = event.target.closest("[data-goto]");
    if (goto && this.mockup.contains(goto)) {
      this._showScreen(goto.getAttribute("data-goto"));
      this._flash(`→ ${goto.getAttribute("data-goto")}`);
      return;
    }
    const screen = event.target.closest(".screen");
    if (!screen || !this.mockup.contains(screen)) return;
    const name = screen.getAttribute("data-slug") || screen.querySelector("h2")?.textContent?.trim();
    this._showScreen(name, false);
  }

  _reset() {
    this._clearCurrent();
    this.expansion.clear();
    this.frame?.scrollTo({ top: 0, left: 0, behavior: "smooth" });
    this._paintTree();
  }

  _playNext() {
    const all = this._screens();
    const current = this.page.querySelector("#mockup .screen.current");
    const next = all[(all.indexOf(current) + 1 + all.length) % all.length];
    this._showScreen(next.getAttribute("data-slug"));
  }
}

function mountMapMockup({ startScreen } = {}) {
  new MapMockup(document, startScreen, new ScreenTreeExpansion()).mount();
}
