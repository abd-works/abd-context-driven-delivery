/**
 * Foundry catalog — wheel zoom on embedded diagrams.net viewers.
 * Toolbar zoom/lightbox still work; this restores scroll-wheel magnification.
 * Initial zoom comes from data-mxgraph "zoom" — do not CSS-scale on load.
 */
(function () {
  'use strict';

  var MIN = 0.35;
  var MAX = 3.5;
  var STEP = 0.12;

  function viewerRoot(wrap) {
    return wrap.querySelector('.mxgraph > div') || wrap.querySelector('.mxgraph');
  }

  function applyScale(root, scale) {
    root.style.transformOrigin = '0 0';
    root.style.transform = 'scale(' + scale + ')';
    root.dataset.drawioScale = String(scale);
  }

  function bindWrap(wrap) {
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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scan);
  } else {
    scan();
  }
}());
