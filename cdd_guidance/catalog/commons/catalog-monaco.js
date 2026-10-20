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
  var pending = [];
  var monacoReady = false;
  var catalogModelFolds = new Map();

  function visible(root) {
    return !!root && root.offsetHeight > 40 && !root.closest("[hidden]");
  }

  function registerCatalogFolding() {
    if (window.__catalogFoldingRegistered) return;
    window.__catalogFoldingRegistered = true;
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

  function collapseAllFolds(editor, folds) {
    var folding = editor.getContribution("editor.contrib.folding");
    if (!folding || !folding.getFoldingModel) return Promise.resolve(0);
    return folding.getFoldingModel().then(function (model) {
      if (!model || !model.regions) return 0;
      var regions = model.regions;
      var foldAction = editor.getAction("editor.fold");
      if (!foldAction) return 0;
      var chain = Promise.resolve();
      var collapsed = 0;
      for (var f = 0; f < folds.length; f++) {
        var fold = folds[f];
        var regionIndex = -1;
        for (var i = 0; i < regions.length; i++) {
          if (
            regions.getStartLineNumber(i) === fold.start &&
            regions.getEndLineNumber(i) === fold.end
          ) {
            regionIndex = i;
            break;
          }
        }
        if (regionIndex < 0) continue;
        if (regions.isCollapsed(regionIndex)) {
          collapsed += 1;
          continue;
        }
        chain = chain.then(function (startLine) {
          editor.setPosition({ lineNumber: startLine, column: 1 });
          return Promise.resolve(foldAction.run());
        }.bind(null, fold.start));
        collapsed += 1;
      }
      return chain.then(function () {
        return collapsed;
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
      if (tries > 40) {
        finish();
        return;
      }
      tries += 1;
      collapseAllFolds(editor, folds).then(function (matched) {
        if (matched < folds.length && tries < 40) {
          window.setTimeout(attempt, 100);
        } else {
          finish();
        }
      });
    }
    attempt();
  }

  function parseFolds(root) {
    try {
      return JSON.parse(root.getAttribute("data-folds") || "[]");
    } catch (e) {
      return [];
    }
  }

  function bindFolds(root, editor) {
    var folds = parseFolds(root);
    var model = editor.getModel();
    if (!model) return;
    catalogModelFolds.set(model.id, folds);
    scheduleCollapse(root, editor, folds);
  }

  function mount(root) {
    if (root._editor) {
      root._editor.layout();
      bindFolds(root, root._editor);
      return;
    }
    var sourceEl = document.getElementById(
      root.getAttribute("data-source-id") || "catalog-monaco-source"
    );
    var source = "";
    if (sourceEl) {
      try {
        source = JSON.parse(sourceEl.textContent || '""');
      } catch (e) {
        source = "";
      }
    }
    var language = root.getAttribute("data-language") || "typescript";
    var folds = parseFolds(root);
    var model = monaco.editor.createModel(source, language);
    catalogModelFolds.set(model.id, folds);
    var editor = monaco.editor.create(root, {
      model: model,
      theme: "catalog-code",
      readOnly: true,
      folding: true,
      automaticLayout: true,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      wordWrap: "on",
      wrappingStrategy: "advanced",
      scrollbar: {
        vertical: "auto",
        horizontal: "hidden",
        handleMouseWheel: true,
      },
      fontSize: 13,
      fontFamily: "JetBrains Mono, ui-monospace, monospace",
      padding: { top: 12, bottom: 12 },
    });
    root._editor = editor;
    scheduleCollapse(root, editor, folds);
  }

  function drain() {
    var next = pending.splice(0, pending.length);
    next.forEach(function (root) {
      if (!root) return;
      if (root._editor) {
        root._editor.layout();
        bindFolds(root, root._editor);
        return;
      }
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
