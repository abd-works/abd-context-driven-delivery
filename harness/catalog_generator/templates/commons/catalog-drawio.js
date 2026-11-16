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
  // How often to look for the diagrams.net viewer's rendered root, and how long to keep looking before giving up.
  var VIEWER_POLL_MS = 120;
  var VIEWER_WAIT_MS = 12000;
  // The gap kept between the fixed site navigation, or the window's bottom edge, and an example the page scrolls to.
  var NAV_GAP_PX = 16;
  var EDGE_MARGIN_PX = 16;
  // An example column opens over a CSS transition: scroll as it starts, once it has opened, and once its content settled.
  var COLUMN_OPENED_MS = 480;
  var COLUMN_SETTLED_MS = 1000;
  // A draw.io frame needs a moment to load before it can be resized, and longer before its final height is known.
  var DRAWIO_LOAD_MS = 500;
  var DRAWIO_SETTLED_MS = 1200;
  // The story map zoom of each wrap, so a wrap bound again refits the zoom it already has.
  var storyMapZooms = new WeakMap();

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

  /** The diagram page's size, which the generator writes on the wrap; zero when it did not. */
  function pageSizeOf(wrap) {
    return { width: parseFloat(wrap.dataset.pageW || '0'), height: parseFloat(wrap.dataset.pageH || '0') };
  }

  function sizeToPage(element, page) {
    element.style.width = page.width + 'px';
    element.style.height = page.height + 'px';
  }

  function sizeFrameToPage(wrap, page) {
    var frame = wrap.querySelector('.catalog-drawio-frame');
    if (!frame || !page.width || !page.height) return null;
    sizeToPage(frame, page);
    frame.style.maxWidth = 'none';
    return frame;
  }

  function scrollWrapToTopLeft(wrap) {
    wrap.style.overflowX = 'auto';
    wrap.style.overflowY = 'auto';
    wrap.scrollLeft = 0;
    wrap.scrollTop = 0;
  }

  /** A story map's zoom: it fits the map's height to the wrap until the reader zooms with the wheel. */
  function StoryMapZoom(wrap, scaleElement) {
    this.wrap = wrap;
    this.scaleElement = scaleElement;
    this.page = pageSizeOf(wrap);
    this.spacer = storyMapSpacer(wrap);
    this.scale = storyMapFitScale(wrap, this.page.width, this.page.height);
    this.readerZoomed = false;
  }

  StoryMapZoom.prototype.apply = function () {
    var page = this.page;
    if (page.width && page.height) {
      sizeToPage(this.scaleElement, page);
      this.spacer.style.width = Math.ceil(page.width * this.scale) + 'px';
      this.spacer.style.height = Math.ceil(page.height * this.scale) + 'px';
    }
    this.scaleElement.style.transformOrigin = 'left top';
    this.scaleElement.style.transform = 'scale(' + this.scale + ')';
    this.scaleElement.style.overflow = 'visible';
    this.wrap.dataset.storyMapScale = String(this.scale);
    scrollWrapToTopLeft(this.wrap);
  };

  StoryMapZoom.prototype.refit = function () {
    if (this.readerZoomed) return;
    this.scale = storyMapFitScale(this.wrap, this.page.width, this.page.height);
    this.apply();
  };

  StoryMapZoom.prototype.zoomBy = function (direction) {
    this.readerZoomed = true;
    this.scale = Math.min(STORY_MAP_MAX, Math.max(STORY_MAP_MIN, this.scale + direction * STORY_MAP_STEP));
    this.apply();
  };

  StoryMapZoom.prototype.listen = function () {
    var zoom = this;
    if (typeof ResizeObserver !== 'undefined') {
      new ResizeObserver(function () { zoom.refit(); }).observe(this.wrap);
    }
    this.wrap.addEventListener(
      'wheel',
      function (event) {
        event.preventDefault();
        event.stopPropagation();
        zoom.zoomBy(event.deltaY < 0 ? 1 : -1);
      },
      { passive: false }
    );
  };

  function bindStoryMapWrap(wrap) {
    if (storyMapZooms.has(wrap)) {
      refitStoryMap(wrap);
      return;
    }
    var scaleElement = wrap.querySelector('.approach-stage-drawio__scale');
    if (!scaleElement) return;
    sizeFrameToPage(wrap, pageSizeOf(wrap));
    var zoom = new StoryMapZoom(wrap, scaleElement);
    storyMapZooms.set(wrap, zoom);
    zoom.refit();
    zoom.listen();
  }

  /** Refit a story map that is already bound, now that its column has its real size. */
  function refitStoryMap(wrap) {
    var zoom = storyMapZooms.get(wrap);
    if (zoom) zoom.refit();
  }

  function bindFramedWrap(wrap) {
    if (wrap.dataset.framedZoomBound === '1') return;
    wrap.dataset.framedZoomBound = '1';
    var page = pageSizeOf(wrap);
    var frame = sizeFrameToPage(wrap, page);
    if (frame) frame.style.transform = 'none';
    var scaleElement = wrap.querySelector('.approach-stage-drawio__scale');
    if (scaleElement && page.width && page.height) {
      sizeToPage(scaleElement, page);
      scaleElement.style.position = 'static';
      scaleElement.style.transform = 'none';
    }
    scrollWrapToTopLeft(wrap);
    wrap.querySelectorAll('.catalog-drawio-frame').forEach(loadDrawioFrame);
  }

  /** Zoom a live viewer with the wheel, starting from the scale it was rendered at. */
  function zoomViewerOnWheel(wrap, viewer) {
    var scale = parseFloat(viewer.dataset.drawioScale) || 1;
    wrap.addEventListener(
      'wheel',
      function (event) {
        var target = viewerRoot(wrap);
        if (!target) return;
        event.preventDefault();
        scale = Math.min(MAX, Math.max(MIN, scale + (event.deltaY < 0 ? 1 : -1) * STEP));
        applyScale(target, scale);
      },
      { passive: false }
    );
  }

  /** The viewer renders after the page loads, so wait for its root, then zoom it; stop waiting after a while. */
  function bindViewerWrap(wrap) {
    if (wrap.dataset.drawioZoomBound === '1') return;
    wrap.dataset.drawioZoomBound = '1';
    var poll = window.setInterval(function () {
      var viewer = viewerRoot(wrap);
      if (!viewer) return;
      window.clearInterval(poll);
      zoomViewerOnWheel(wrap, viewer);
    }, VIEWER_POLL_MS);
    window.setTimeout(function () {
      window.clearInterval(poll);
    }, VIEWER_WAIT_MS);
  }

  function bindWrap(wrap) {
    if (wrap.classList.contains('approach-stage-drawio--story-map')) {
      bindStoryMapWrap(wrap);
    } else if (wrap.classList.contains('approach-stage-drawio--framed')) {
      bindFramedWrap(wrap);
    } else {
      bindViewerWrap(wrap);
    }
  }

  function scan() {
    document.querySelectorAll('.skill-drawio-wrap').forEach(bindWrap);
  }

  function navOffset() {
    var nav = document.querySelector('.site-nav');
    return (nav ? nav.getBoundingClientRect().height : 0) + NAV_GAP_PX;
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

  /** Where to scroll so the example shows whole below the navigation, or shows its bottom when it is taller than the
   * window; null when it already shows as well as it can. */
  function exampleScrollY(target) {
    var navigation = navOffset();
    var rect = target.getBoundingClientRect();
    var top = rect.top + window.pageYOffset;
    var bottom = top + rect.height;
    var windowHeight = window.innerHeight;
    var bottomAlignedY = bottom - windowHeight + EDGE_MARGIN_PX;
    if (rect.height <= windowHeight - navigation - EDGE_MARGIN_PX) {
      var topAlignedY = top - navigation;
      return bottom > topAlignedY + windowHeight - EDGE_MARGIN_PX ? bottomAlignedY : topAlignedY;
    }
    if (bottom > window.pageYOffset + windowHeight - EDGE_MARGIN_PX) return bottomAlignedY;
    if (rect.top < navigation) return top - navigation;
    return null;
  }

  function scrollPageToExample(col) {
    var target = exampleScrollTarget(col);
    if (!target) return;
    var y = exampleScrollY(target);
    if (y !== null) window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
  }

  function layoutMonacoInColumn(col) {
    if (!col) return;
    if (!window.catalogMonacoShow) return;
    col.querySelectorAll('.catalog-monaco').forEach(function (root) {
      window.catalogMonacoShow(root);
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
    window.setTimeout(runScroll, COLUMN_OPENED_MS);
    window.setTimeout(runScroll, COLUMN_SETTLED_MS);
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
    }, DRAWIO_LOAD_MS);
    window.setTimeout(function () {
      scrollPageToExample(col);
    }, DRAWIO_SETTLED_MS);
  }

  window.catalogApproachStageScroll = approachStageScroll;
  window.catalogApproachStageScrollAfterClose = approachStageScrollAfterClose;
  window.catalogDrawioRefreshColumn = refreshDrawioColumn;
  window.catalogDrawioRefitStoryMap = refitStoryMap;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scan);
  } else {
    scan();
  }
}());
