/**
 * Shared Discovery / Specification / Implementation expand row.
 * Each `.approach-refine-row` owns its own rewind/play and open columns.
 */
(function () {
  'use strict';

  var STAGE_IDS = ['discovery', 'specification', 'implementation'];

  function expandableIds(host) {
    return STAGE_IDS.filter(function (id) {
      return !!host.querySelector('.approach-stage-column[data-stage-id="' + id + '"]');
    });
  }

  function stageButton(host, id) {
    var found = null;
    host.querySelectorAll('.approach-window__stage').forEach(function (btn) {
      if (btn.getAttribute('data-stage-id') === id) found = btn;
    });
    return found;
  }

  function paint(host) {
    var ids = expandableIds(host);
    var open = 0;
    ids.forEach(function (id) {
      var col = host.querySelector('.approach-stage-column[data-stage-id="' + id + '"]');
      if (col && col.classList.contains('is-open')) open += 1;
    });
    var back = host.querySelector('[data-refine-nav="-1"]');
    var next = host.querySelector('[data-refine-nav="1"]');
    if (back) back.disabled = open === 0;
    if (next) next.disabled = ids.length === 0 || open === ids.length;
  }

  function scrollExampleColumn(col) {
    if (window.catalogApproachStageScroll) {
      window.catalogApproachStageScroll(col);
    }
  }

  function refreshExampleColumn(col) {
    if (window.catalogDrawioRefreshColumn) {
      window.catalogDrawioRefreshColumn(col);
    }
  }

  function showExampleEditors(col) {
    if (!col) return;
    col.querySelectorAll('.catalog-monaco').forEach(function (editor) {
      if (!window.catalogMonacoShow) return;
      window.catalogMonacoShow(editor);
      [460, 1000, 1600].forEach(function (ms) {
        window.setTimeout(function () {
          window.catalogMonacoShow(editor);
        }, ms);
      });
    });
  }

  function setStageOpen(host, col, button, on) {
    col.classList.toggle('is-open', on);
    var stageId = col.getAttribute('data-stage-id');
    var opening = host.querySelector('.approach-refine__opening[data-stage-id="' + stageId + '"]');
    if (opening) opening.classList.toggle('is-open', on);
    button.classList.toggle('is-active', on);
    button.setAttribute('aria-pressed', on ? 'true' : 'false');
    button.setAttribute('aria-expanded', on ? 'true' : 'false');
    paint(host);
  }

  function toggleStageColumn(host, id, button) {
    var col = host.querySelector('.approach-stage-column[data-stage-id="' + id + '"]');
    if (!col) return;
    if (col.classList.contains('is-open')) {
      var open = Array.prototype.slice.call(host.querySelectorAll('.approach-stage-column.is-open'));
      if (open.length === 1) {
        setStageOpen(host, col, button, false);
        host.classList.toggle('is-open', false);
        return;
      }
      if (open[open.length - 1] === col) {
        setStageOpen(host, col, button, false);
        host.classList.toggle('is-open', !!host.querySelector('.approach-stage-column.is-open'));
        if (window.catalogApproachStageScrollAfterClose) {
          window.catalogApproachStageScrollAfterClose(host);
        }
        return;
      }
      scrollExampleColumn(col);
      refreshExampleColumn(col);
      showExampleEditors(col);
      return;
    }
    setStageOpen(host, col, button, true);
    host.classList.toggle('is-open', true);
    scrollExampleColumn(col);
    refreshExampleColumn(col);
    showExampleEditors(col);
  }

  function openNext(host) {
    if (!host) return false;
    var ids = expandableIds(host);
    for (var i = 0; i < ids.length; i += 1) {
      var col = host.querySelector('.approach-stage-column[data-stage-id="' + ids[i] + '"]');
      if (col && !col.classList.contains('is-open')) {
        var button = stageButton(host, ids[i]);
        if (button) toggleStageColumn(host, ids[i], button);
        return true;
      }
    }
    return false;
  }

  function closeLast(host) {
    if (!host) return false;
    var ids = expandableIds(host);
    for (var i = ids.length - 1; i >= 0; i -= 1) {
      var col = host.querySelector('.approach-stage-column[data-stage-id="' + ids[i] + '"]');
      if (col && col.classList.contains('is-open')) {
        var button = stageButton(host, ids[i]);
        if (button) toggleStageColumn(host, ids[i], button);
        return true;
      }
    }
    return false;
  }

  function setStage(host, id, on) {
    if (!host) return false;
    var col = host.querySelector('.approach-stage-column[data-stage-id="' + id + '"]');
    var button = stageButton(host, id);
    if (!col || !button) return false;
    if (col.classList.contains('is-open') === on) {
      if (on) {
        scrollExampleColumn(col);
        refreshExampleColumn(col);
        showExampleEditors(col);
      }
      return true;
    }
    setStageOpen(host, col, button, on);
    host.classList.toggle('is-open', !!host.querySelector('.approach-stage-column.is-open'));
    if (on) {
      scrollExampleColumn(col);
      refreshExampleColumn(col);
      showExampleEditors(col);
    } else if (window.catalogApproachStageScrollAfterClose) {
      window.catalogApproachStageScrollAfterClose(host);
    }
    return true;
  }

  window.catalogRefineOpenNext = openNext;
  window.catalogRefineCloseLast = closeLast;
  window.catalogRefineSetStage = setStage;
  window.catalogRefinePaint = paint;

  function bindHost(host) {
    host.querySelectorAll('.approach-window__stage').forEach(function (stageBtn) {
      stageBtn.addEventListener('click', function (e) {
        e.preventDefault();
        if (stageBtn.classList.contains('approach-window__stage--context')) return;
        toggleStageColumn(host, stageBtn.getAttribute('data-stage-id'), stageBtn);
      });
    });
    host.querySelectorAll('[data-refine-nav]').forEach(function (navBtn) {
      navBtn.addEventListener('click', function (e) {
        e.preventDefault();
        if (navBtn.getAttribute('data-refine-nav') === '1') openNext(host);
        else closeLast(host);
      });
    });
    paint(host);
  }

  function init() {
    document.querySelectorAll('.approach-refine-row').forEach(bindHost);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
