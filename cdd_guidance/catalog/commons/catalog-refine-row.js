/**
 * Shared Discovery / Specification / Implementation expand row.
 * Each `.approach-refine-row` owns its own rewind/play and open columns.
 * One example expands to full width; switching collapses the previous then opens the next.
 */
(function () {
  'use strict';

  var STAGE_IDS = ['discovery', 'specification', 'implementation'];
  var ANIM_MS = 380;

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

  function measureExampleHeight(host, col) {
    if (!host || !col) return;
    var body = col.querySelector('.approach-stage-column__body');
    if (!body) return;

    var cap = Math.min(window.innerHeight * 0.88, 1200);
    var floor = 240;
    var height = floor;

    var storyMap = body.querySelector('.approach-stage-drawio--story-map, .approach-stage-drawio--framed');
    if (storyMap) {
      var spacer = storyMap.querySelector('.approach-stage-drawio__spacer');
      var pageH = parseFloat(storyMap.dataset.pageH || '0');
      if (spacer && spacer.offsetHeight) {
        height = Math.max(height, spacer.offsetHeight + 20);
      } else if (pageH) {
        var fit = storyMap.clientWidth > 0 ? storyMap.clientWidth / parseFloat(storyMap.dataset.pageW || pageH) : 1;
        height = Math.max(height, Math.ceil(pageH * Math.min(fit, 1.2)) + 20);
      }
      if (storyMap._storyMapRefit) storyMap._storyMapRefit();
    }

    var monaco = body.querySelector('.catalog-monaco');
    if (monaco) {
      height = Math.max(height, Math.min(monaco.scrollHeight + 12, cap));
    }

    var preview = body.querySelector('.skill-md-preview');
    if (preview) {
      height = Math.max(height, Math.min(preview.scrollHeight + 12, cap));
    }

    var iframeExample = body.querySelector('.catalog-example__frame, .catalog-example iframe');
    if (iframeExample) {
      var iframeH = iframeExample.offsetHeight || parseFloat(iframeExample.getAttribute('height') || '0');
      if (iframeH) height = Math.max(height, Math.min(iframeH + 24, cap));
    }

    if (!storyMap && !monaco && !preview && !iframeExample) {
      height = Math.max(height, Math.min(body.scrollHeight + 12, cap));
    }

    height = Math.min(Math.max(Math.ceil(height), floor), cap);
    var px = height + 'px';
    host.style.setProperty('--approach-example-h', px);
    col.style.setProperty('--approach-example-h', px);
  }

  function afterOpen(host, col) {
    measureExampleHeight(host, col);
    scrollExampleColumn(col);
    refreshExampleColumn(col);
    showExampleEditors(col);
    window.requestAnimationFrame(function () {
      measureExampleHeight(host, col);
    });
    window.setTimeout(function () {
      measureExampleHeight(host, col);
      scrollExampleColumn(col);
    }, ANIM_MS + 40);
    window.setTimeout(function () {
      measureExampleHeight(host, col);
    }, 1000);
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

  function closeOtherColumns(host, exceptId) {
    expandableIds(host).forEach(function (id) {
      if (id === exceptId) return;
      var other = host.querySelector('.approach-stage-column[data-stage-id="' + id + '"]');
      if (!other || !other.classList.contains('is-open')) return;
      var otherBtn = stageButton(host, id);
      if (otherBtn) setStageOpen(host, other, otherBtn, false);
    });
  }

  function openStageColumn(host, id, button) {
    var col = host.querySelector('.approach-stage-column[data-stage-id="' + id + '"]');
    if (!col) return;
    closeOtherColumns(host, id);
    setStageOpen(host, col, button, true);
    host.classList.add('is-open');
    afterOpen(host, col);
  }

  function toggleStageColumn(host, id, button) {
    var col = host.querySelector('.approach-stage-column[data-stage-id="' + id + '"]');
    if (!col) return;

    if (col.classList.contains('is-open')) {
      setStageOpen(host, col, button, false);
      host.classList.toggle('is-open', !!host.querySelector('.approach-stage-column.is-open'));
      if (window.catalogApproachStageScrollAfterClose) {
        window.catalogApproachStageScrollAfterClose(host);
      }
      return;
    }

    var open = host.querySelector('.approach-stage-column.is-open');
    if (open && open !== col) {
      var openId = open.getAttribute('data-stage-id');
      var openBtn = stageButton(host, openId);
      if (openBtn) setStageOpen(host, open, openBtn, false);
      host.classList.remove('is-open');
      window.setTimeout(function () {
        openStageColumn(host, id, button);
      }, ANIM_MS);
      return;
    }

    openStageColumn(host, id, button);
  }

  function openNext(host) {
    if (!host) return false;
    var ids = expandableIds(host);
    var targetId = null;
    for (var i = 0; i < ids.length; i += 1) {
      var col = host.querySelector('.approach-stage-column[data-stage-id="' + ids[i] + '"]');
      if (col && !col.classList.contains('is-open')) {
        targetId = ids[i];
        break;
      }
    }
    if (!targetId) return false;

    var open = host.querySelector('.approach-stage-column.is-open');
    if (open) {
      var openId = open.getAttribute('data-stage-id');
      var openBtn = stageButton(host, openId);
      if (openBtn) setStageOpen(host, open, openBtn, false);
      host.classList.remove('is-open');
      window.setTimeout(function () {
        var button = stageButton(host, targetId);
        if (button) openStageColumn(host, targetId, button);
      }, ANIM_MS);
      return true;
    }

    var button = stageButton(host, targetId);
    if (button) openStageColumn(host, targetId, button);
    return true;
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
      if (on) afterOpen(host, col);
      return true;
    }
    if (on) {
      openStageColumn(host, id, button);
      return true;
    }
    setStageOpen(host, col, button, false);
    host.classList.toggle('is-open', !!host.querySelector('.approach-stage-column.is-open'));
    if (window.catalogApproachStageScrollAfterClose) {
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
    if (typeof ResizeObserver !== 'undefined') {
      new ResizeObserver(function () {
        var openCol = host.querySelector('.approach-stage-column.is-open');
        if (openCol) measureExampleHeight(host, openCol);
      }).observe(host);
    }
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
