function mountMapMockup(options = {}) {
  const toast = document.querySelector("#toast");
  const explorer = document.querySelector("#explorer-tree");
  const frame = document.querySelector("#story-demo-frame");
  const tree = readExplorerTree(document);
  const expanded = new Set();
  let openScreen = null;
  const startScreen = options.startScreen || "Create Account";

  function screens() {
    return [...document.querySelectorAll("#mockup .screen")];
  }

  function flash(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("show");
    clearTimeout(flash._t);
    flash._t = setTimeout(() => toast.classList.remove("show"), 1600);
  }

  function paintTree({ scrollToCurrentScreen = false } = {}) {
    const name = document.querySelector("#mockup .screen.current")?.getAttribute("data-slug") || "";
    if (name && openScreen !== name) {
      openScreen = name;
      for (const key of tree.screenKeys[name] || []) expanded.add(key);
    }
    renderScreenTree(
      explorer,
      {
        nodes: tree.nodes,
        expanded,
        currentScreen: name,
        scrollToCurrentScreen,
      },
      {
        onToggle(key) {
          if (expanded.has(key)) expanded.delete(key);
          else expanded.add(key);
          paintTree();
        },
        onScreen(screenName) {
          openScreen = null;
          showScreen(screenName);
        },
        onStory() {},
        onScenario() {},
      },
    );
  }

  function showScreen(name, scroll) {
    const screen = screens().find(
      (el) => el.getAttribute("data-slug") === name || el.querySelector("h2")?.textContent?.trim() === name,
    );
    if (!screen) return;
    document.querySelectorAll(".screen.current").forEach((el) => el.classList.remove("current"));
    screen.classList.add("current");
    if (scroll !== false) {
      screen.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });
    }
    paintTree({ scrollToCurrentScreen: true });
  }

  document.querySelector("#mockup")?.addEventListener("click", (event) => {
    const mockup = document.querySelector("#mockup");
    const goto = event.target.closest("[data-goto]");
    if (goto && mockup.contains(goto)) {
      showScreen(goto.getAttribute("data-goto"));
      flash(`→ ${goto.getAttribute("data-goto")}`);
      return;
    }
    const screen = event.target.closest(".screen");
    if (!screen || !mockup.contains(screen)) return;
    const name = screen.getAttribute("data-slug") || screen.querySelector("h2")?.textContent?.trim();
    showScreen(name, false);
  });

  document.querySelector("[data-reset]")?.addEventListener("click", () => {
    document.querySelectorAll(".screen.current").forEach((el) => el.classList.remove("current"));
    expanded.clear();
    openScreen = null;
    frame?.scrollTo({ top: 0, left: 0, behavior: "smooth" });
    paintTree();
  });

  document.querySelector("[data-play-next]")?.addEventListener("click", () => {
    const all = screens();
    const current = document.querySelector("#mockup .screen.current");
    const index = all.indexOf(current);
    const next = all[(index + 1 + all.length) % all.length];
    showScreen(next.getAttribute("data-slug"));
  });

  bindFlowZoom(frame, document.querySelector("#mockup"));

  showScreen(startScreen, false);
}
