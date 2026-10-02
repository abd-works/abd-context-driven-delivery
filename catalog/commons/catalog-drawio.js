/**
 * Foundry catalog — wheel zoom on embedded diagrams.net viewers.
 * Story maps use a framed page, start zoomed in, and stay pinned top-left.
 */
(function () {
  'use strict';

  var MIN = 0.35;
  var MAX = 3.5;
  var STEP = 0.12;
  var STORY_MAP_DEFAULT = 1;
  var STORY_MAP_MIN = 0.5;
  var STORY_MAP_MAX = 4;
  var STORY_MAP_STEP = 0.1;

  function viewerRoot(wrap) {
    return wrap.querySelector('.mxgraph > div') || wrap.querySelector('.mxgraph');
  }

  function applyScale(root, scale) {
    root.style.transformOrigin = 'left top';
    root.style.transform = 'scale(' + scale + ')';
    root.dataset.drawioScale = String(scale);
  }

  function storyMapSpacer(wrap) {
    var spacer = wrap.querySelector('.approach-stage-drawio__spacer');
    if (spacer) return spacer;
    spacer = document.createElement('div');
    spacer.className = 'approach-stage-drawio__spacer';
    spacer.setAttribute('aria-hidden', 'true');
    wrap.insertBefore(spacer, wrap.firstChild);
    return spacer;
  }

  function storyMapFitScale(wrap, pageW, pageH) {
    var pad = 4;
    var availableW = Math.max(1, wrap.clientWidth - pad);
    var availableH = Math.max(1, wrap.clientHeight - pad);
    if (!pageW || !pageH || !availableW || !availableH) {
      return STORY_MAP_DEFAULT;
    }
    var fit = availableH / pageH;
    return Math.min(STORY_MAP_MAX, Math.max(STORY_MAP_MIN, fit));
  }

  function bindStoryMapWrap(wrap) {
    if (wrap.dataset.storyMapZoomBound === '1') {
      if (wrap._storyMapRefit) wrap._storyMapRefit();
      return;
    }
    wrap.dataset.storyMapZoomBound = '1';
    var scaleEl = wrap.querySelector('.approach-stage-drawio__scale');
    if (!scaleEl) return;
    var pageW = parseFloat(wrap.dataset.pageW || '0');
    var pageH = parseFloat(wrap.dataset.pageH || '0');
    var frame = wrap.querySelector('.catalog-drawio-frame');
    if (frame && pageW && pageH) {
      frame.style.width = pageW + 'px';
      frame.style.height = pageH + 'px';
      frame.style.maxWidth = 'none';
    }
    var spacer = storyMapSpacer(wrap);
    var scale = storyMapFitScale(wrap, pageW, pageH);
    function apply() {
      if (pageW && pageH) {
        scaleEl.style.width = pageW + 'px';
        scaleEl.style.height = pageH + 'px';
        spacer.style.width = Math.ceil(pageW * scale) + 'px';
        spacer.style.height = Math.ceil(pageH * scale) + 'px';
      }
      scaleEl.style.transformOrigin = 'left top';
      scaleEl.style.transform = 'scale(' + scale + ')';
      scaleEl.style.overflow = 'visible';
      wrap.style.overflowX = 'auto';
      wrap.style.overflowY = 'auto';
      wrap.dataset.storyMapScale = String(scale);
      wrap.scrollLeft = 0;
      wrap.scrollTop = 0;
    }
    function refit() {
      if (wrap.dataset.storyMapScaleUser === '1') return;
      scale = storyMapFitScale(wrap, pageW, pageH);
      apply();
    }
    wrap._storyMapRefit = refit;
    refit();
    if (typeof ResizeObserver !== 'undefined') {
      new ResizeObserver(refit).observe(wrap);
    }
    wrap.addEventListener(
      'wheel',
      function (e) {
        e.preventDefault();
        e.stopPropagation();
        wrap.dataset.storyMapScaleUser = '1';
        var dir = e.deltaY < 0 ? 1 : -1;
        scale = Math.min(
          STORY_MAP_MAX,
          Math.max(STORY_MAP_MIN, scale + dir * STORY_MAP_STEP)
        );
        apply();
      },
      { passive: false }
    );
  }

  function bindFramedWrap(wrap) {
    if (wrap.dataset.framedZoomBound === '1') return;
    wrap.dataset.framedZoomBound = '1';
    var scaleEl = wrap.querySelector('.approach-stage-drawio__scale');
    var pageW = parseFloat(wrap.dataset.pageW || '0');
    var pageH = parseFloat(wrap.dataset.pageH || '0');
    var frame = wrap.querySelector('.catalog-drawio-frame');
    if (frame && pageW && pageH) {
      frame.style.width = pageW + 'px';
      frame.style.height = pageH + 'px';
      frame.style.maxWidth = 'none';
      frame.style.transform = 'none';
    }
    if (scaleEl && pageW && pageH) {
      scaleEl.style.width = pageW + 'px';
      scaleEl.style.height = pageH + 'px';
      scaleEl.style.position = 'static';
      scaleEl.style.transform = 'none';
    }
    wrap.style.overflowX = 'auto';
    wrap.style.overflowY = 'auto';
    wrap.scrollLeft = 0;
    wrap.scrollTop = 0;
    wrap.querySelectorAll('.catalog-drawio-frame').forEach(loadDrawioFrame);
  }

  function bindWrap(wrap) {
    if (wrap.classList.contains('approach-stage-drawio--story-map')) {
      bindStoryMapWrap(wrap);
      return;
    }
    if (wrap.classList.contains('approach-stage-drawio--framed')) {
      bindFramedWrap(wrap);
      return;
    }
    if (wrap.dataset.drawioZoomBound === '1') return;
    wrap.dataset.drawioZoomBound = '1';

    var scale = 1;
    var poll = window.setInterval(function () {
      var root = viewerRoot(wrap);
      if (!root) return;
      window.clearInterval(poll);
      if (root.dataset.drawioScale) {
        scale = parseFloat(root.dataset.drawioScale) || 1;
      }
      wrap.addEventListener(
        'wheel',
        function (e) {
          var target = viewerRoot(wrap);
          if (!target) return;
          e.preventDefault();
          var dir = e.deltaY < 0 ? 1 : -1;
          scale = Math.min(MAX, Math.max(MIN, scale + dir * STEP));
          applyScale(target, scale);
        },
        { passive: false }
      );
    }, 120);
    window.setTimeout(function () {
      window.clearInterval(poll);
    }, 12000);
  }

  function scan() {
    document.querySelectorAll('.skill-drawio-wrap').forEach(bindWrap);
  }

  function navOffset() {
    var nav = document.querySelector('.site-nav');
    return nav ? nav.getBoundingClientRect().height + 16 : 16;
  }

  function exampleScrollTarget(col) {
    if (!col) return null;
    if (col.classList && col.classList.contains('approach-stage-column')) {
      return col;
    }
    return (
      col.closest('.approach-stage-column.is-open') ||
      col.closest('.approach-stage-examples') ||
      col.closest('.approach-refine-row') ||
      col
    );
  }

  function scrollPageToExample(col) {
    var target = exampleScrollTarget(col);
    if (!target) return;
    var pad = navOffset();
    var margin = 16;
    var rect = target.getBoundingClientRect();
    var height = rect.height;
    var elTop = rect.top + window.pageYOffset;
    var elBottom = elTop + height;
    var viewH = window.innerHeight;
    var room = viewH - pad - margin;
    var y = window.pageYOffset;
    var viewBottom = window.pageYOffset + viewH - margin;

    if (height <= room) {
      y = elTop - pad;
      if (elBottom > y + viewH - margin) {
        y = elBottom - viewH + margin;
      }
    } else if (elBottom > viewBottom) {
      y = elBottom - viewH + margin;
    } else if (rect.top < pad) {
      y = elTop - pad;
    } else {
      return;
    }

    window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
  }

  function layoutMonacoInColumn(col) {
    if (!col) return;
    col.querySelectorAll('.catalog-monaco').forEach(function (root) {
      if (window.catalogMonacoShow) window.catalogMonacoShow(root);
      if (root._editor && typeof root._editor.layout === 'function') {
        root._editor.layout();
      }
    });
  }

  function approachStageScroll(col) {
    if (!col) return;
    function runScroll() {
      if (!col.classList.contains('is-open')) return;
      layoutMonacoInColumn(col);
      scrollPageToExample(col);
    }
    window.requestAnimationFrame(runScroll);
    window.setTimeout(runScroll, 480);
    window.setTimeout(runScroll, 1000);
  }

  function approachStageScrollAfterClose(host) {
    if (!host) return;
    var open = host.querySelectorAll('.approach-stage-column.is-open');
    if (!open.length) return;
    approachStageScroll(open[open.length - 1]);
  }

  function loadDrawioFrame(frame) {
    var next = frame.getAttribute('data-src');
    if (!next) return;
    if (frame.getAttribute('src') !== next) {
      frame.setAttribute('src', next);
    }
  }

  function refreshDrawioColumn(col) {
    if (!col) return;
    window.setTimeout(function () {
      col.querySelectorAll('.catalog-drawio-frame').forEach(loadDrawioFrame);
      col.querySelectorAll('.approach-stage-drawio--story-map').forEach(bindStoryMapWrap);
      col.querySelectorAll('.approach-stage-drawio--framed').forEach(bindFramedWrap);
      col.querySelectorAll('.mxgraph').forEach(function (el) {
        if (el.viewer && typeof el.viewer.resize === 'function') {
          el.viewer.resize();
          return;
        }
        if (window.GraphViewer) {
          window.GraphViewer.processElements([el]);
        }
      });
      scrollPageToExample(col);
    }, 500);
    window.setTimeout(function () {
      scrollPageToExample(col);
    }, 1200);
  }

  window.catalogApproachStageScroll = approachStageScroll;
  window.catalogApproachStageScrollAfterClose = approachStageScrollAfterClose;
  window.catalogDrawioRefreshColumn = refreshDrawioColumn;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scan);
  } else {
    scan();
  }
}());
