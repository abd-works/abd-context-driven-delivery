/**
 * Foundry catalog — measure stage example columns to their natural content width.
 * Uses off-DOM clones so open columns stay in the flex row during measurement.
 */
(function () {
  'use strict';

  function monacoWidth(body, clip) {
    var clipW = clip && clip.clientWidth ? clip.clientWidth : 960;
    return Math.min(Math.max(clipW * 0.58, 480), 920);
  }

  function measureStageColumn(col) {
    var body = col.querySelector('.approach-stage-column__body');
    if (!body) return 0;

    var clip = col.closest('.approach-stage-examples__clip');
    var width = 0;
    var monaco = body.querySelector('.catalog-monaco');
    var storyMap = body.querySelector('.approach-stage-drawio--story-map');

    if (monaco) {
      var mw = monacoWidth(body, clip);
      monaco.style.setProperty('--stage-monaco-width', mw + 'px');
      width = Math.max(width, mw);
    }

    if (storyMap) {
      var spacer = storyMap.querySelector('.approach-stage-drawio__spacer');
      if (spacer && spacer.offsetWidth) {
        width = Math.max(width, spacer.offsetWidth + 2);
      }
    }

    var probe = body.cloneNode(true);
    probe.style.cssText =
      'position:absolute;left:-10000px;top:0;visibility:hidden;width:max-content;pointer-events:none;';
    if (monaco) {
      var monacoProbe = probe.querySelector('.catalog-monaco');
      if (monacoProbe) {
        monacoProbe.style.width = (width || monacoWidth(body, clip)) + 'px';
      }
    }
    document.body.appendChild(probe);
    width = Math.max(width, Math.ceil(probe.scrollWidth));
    document.body.removeChild(probe);

    width = Math.ceil(width) || 320;
    var prev = parseFloat(col.style.getPropertyValue('--stage-column-width') || '0');
    if (!prev || Math.abs(prev - width) > 1) {
      col.style.setProperty('--stage-column-width', width + 'px');
    }
    return width;
  }

  function syncHost(host, onlyCol) {
    if (!host) return;
    if (onlyCol) {
      measureStageColumn(onlyCol);
      return;
    }
    host.querySelectorAll('.approach-stage-column').forEach(measureStageColumn);
  }

  function syncAll() {
    document.querySelectorAll('.approach-refine-row').forEach(function (host) {
      syncHost(host);
    });
  }

  window.catalogApproachStageColumnsSync = function (host, onlyCol) {
    if (host) {
      window.requestAnimationFrame(function () {
        syncHost(host, onlyCol || null);
      });
      if (onlyCol) {
        window.setTimeout(function () {
          syncHost(host, onlyCol);
        }, 480);
      }
      return;
    }
    syncAll();
  };

  function init() {
    syncAll();
    if (typeof ResizeObserver !== 'undefined') {
      document.querySelectorAll('.approach-stage-examples__clip').forEach(function (clip) {
        new ResizeObserver(function () {
          var host = clip.closest('.approach-refine-row, .approach-stage-examples');
          if (host) syncHost(host);
        }).observe(clip);
      });
    }
    window.addEventListener('resize', function () {
      window.clearTimeout(window._cddStageColResize);
      window._cddStageColResize = window.setTimeout(syncAll, 120);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
