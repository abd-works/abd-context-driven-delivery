(function () {
  if (window.__catalogMonacoLoaded) return;
  window.__catalogMonacoLoaded = true;
  if (typeof require !== "function") return;
  var base = "https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min";
  require.config({ paths: { vs: base + "/vs" } });
  window.MonacoEnvironment = {
    getWorkerUrl: function () {
      return (
        "data:text/javascript;charset=utf-8," +
        encodeURIComponent(
          "self.MonacoEnvironment={baseUrl:'" +
            base +
            "/'};importScripts('" +
            base +
            "/vs/base/worker/workerMain.js');"
        )
      );
    },
  };
  // An editor root shorter than this is still collapsed or hidden, so Monaco would measure it at no size.
  var MIN_VISIBLE_HEIGHT_PX = 40;
  // How many times, a tenth of a second apart, to try folding before Monaco has computed every fold region.
  var MAX_FOLD_ATTEMPTS = 40;
  var FOLD_RETRY_MS = 100;
  var EDITOR_FONT_SIZE_PX = 13;
  var EDITOR_PADDING_PX = 12;
  var pending = [];
  var monacoReady = false;
  var catalogModelFolds = new Map();
  // The editor mounted in each .catalog-monaco root, kept here so no other script reaches into the element for it.
  var editors = new WeakMap();

  function visible(root) {
    return !!root && root.offsetHeight > MIN_VISIBLE_HEIGHT_PX && !root.closest("[hidden]");
  }

  function registerCatalogFolding() {
    monaco.languages.registerFoldingRangeProvider(
      ["typescript", "javascript", "python"],
      {
        provideFoldingRanges: function (model) {
          var folds = catalogModelFolds.get(model.id);
          if (!folds || !folds.length) return [];
          return folds.map(function (fold) {
            return {
              start: fold.start,
              end: fold.end,
              kind: monaco.languages.FoldingRangeKind.Region,
            };
          });
        },
      }
    );
  }

  /** The index of the region Monaco computed for fold, or -1 while it has not computed it yet. */
  function regionIndexOf(regions, fold) {
    for (var index = 0; index < regions.length; index++) {
      if (regions.getStartLineNumber(index) === fold.start && regions.getEndLineNumber(index) === fold.end) {
        return index;
      }
    }
    return -1;
  }

  function foldAt(editor, foldAction, startLine) {
    editor.setPosition({ lineNumber: startLine, column: 1 });
    return Promise.resolve(foldAction.run());
  }

  /** Fold every catalog fold Monaco has a region for; resolves with how many folds it found, folded or already folded. */
  function collapseAllFolds(editor, folds) {
    var folding = editor.getContribution("editor.contrib.folding");
    if (!folding || !folding.getFoldingModel) return Promise.resolve(0);
    return folding.getFoldingModel().then(function (model) {
      var foldAction = editor.getAction("editor.fold");
      if (!model || !model.regions || !foldAction) return 0;
      var chain = Promise.resolve();
      var matched = 0;
      folds.forEach(function (fold) {
        var regionIndex = regionIndexOf(model.regions, fold);
        if (regionIndex < 0) return;
        matched += 1;
        if (model.regions.isCollapsed(regionIndex)) return;
        chain = chain.then(foldAt.bind(null, editor, foldAction, fold.start));
      });
      return chain.then(function () {
        return matched;
      });
    });
  }

  function revealStart(root, editor) {
    var line = parseInt(root.getAttribute("data-start-line") || "0", 10);
    if (!line) return;
    editor.revealLineNearTop(line);
    editor.setPosition({ lineNumber: line, column: 1 });
  }

  function scheduleCollapse(root, editor, folds) {
    function finish() {
      revealStart(root, editor);
    }
    if (!folds.length) {
      finish();
      return;
    }
    var tries = 0;
    function attempt() {
      tries += 1;
      collapseAllFolds(editor, folds).then(function (matched) {
        if (matched < folds.length && tries < MAX_FOLD_ATTEMPTS) {
          window.setTimeout(attempt, FOLD_RETRY_MS);
        } else {
          finish();
        }
      });
    }
    attempt();
  }

  /** JSON the generator wrote into the page; a value that does not parse is shown as if absent rather than break the page. */
  function parsePageJson(text, absent) {
    try {
      return JSON.parse(text);
    } catch (err) {
      if (err instanceof SyntaxError) return absent;
      throw err;
    }
  }

  function parseFolds(root) {
    return parsePageJson(root.getAttribute("data-folds") || "[]", []);
  }

  function readSource(root) {
    var sourceElement = document.getElementById(root.getAttribute("data-source-id") || "catalog-monaco-source");
    return sourceElement ? parsePageJson(sourceElement.textContent || '""', "") : "";
  }

  /** Lay out an editor already mounted in root again, now that root may have its real size; false when none is. */
  function relayout(root) {
    var editor = editors.get(root);
    if (!editor) return false;
    editor.layout();
    bindFolds(root, editor);
    return true;
  }

  var EDITOR_OPTIONS = {
    theme: "catalog-code",
    readOnly: true,
    folding: true,
    automaticLayout: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    wordWrap: "on",
    wrappingStrategy: "advanced",
    scrollbar: { vertical: "auto", horizontal: "hidden", handleMouseWheel: true },
    fontSize: EDITOR_FONT_SIZE_PX,
    fontFamily: "JetBrains Mono, ui-monospace, monospace",
    padding: { top: EDITOR_PADDING_PX, bottom: EDITOR_PADDING_PX },
  };

  function bindFolds(root, editor) {
    var folds = parseFolds(root);
    var model = editor.getModel();
    if (!model) return;
    catalogModelFolds.set(model.id, folds);
    scheduleCollapse(root, editor, folds);
  }

  function mount(root) {
    if (relayout(root)) return;
    var folds = parseFolds(root);
    var model = monaco.editor.createModel(readSource(root), root.getAttribute("data-language") || "typescript");
    catalogModelFolds.set(model.id, folds);
    var editor = monaco.editor.create(root, Object.assign({ model: model }, EDITOR_OPTIONS));
    editors.set(root, editor);
    scheduleCollapse(root, editor, folds);
  }

  function drain() {
    var next = pending.splice(0, pending.length);
    next.forEach(function (root) {
      if (!root || relayout(root)) return;
      if (!visible(root)) {
        pending.push(root);
        return;
      }
      mount(root);
    });
  }

  window.catalogMonacoShow = function (root) {
    if (!root) return;
    pending.push(root);
    if (monacoReady) drain();
  };

  require(["vs/editor/editor.main"], function () {
    registerCatalogFolding();
    monaco.editor.defineTheme("catalog-code", {
      base: "vs",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#F6F5F3",
        "editor.foreground": "#111113",
        "editorLineNumber.foreground": "#595A61",
        "editorGutter.background": "#F6F5F3",
      },
    });
    monacoReady = true;
    document.querySelectorAll(".catalog-monaco").forEach(function (root) {
      if (visible(root)) pending.push(root);
    });
    drain();
  });
})();
