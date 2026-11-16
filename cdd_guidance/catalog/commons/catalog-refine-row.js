/**
 * Shared Discovery / Specification / Implementation expand row.
 * Each `.approach-refine-row` owns its own rewind/play and open columns.
 * One example expands to full width; switching collapses the previous then opens the next.
 */
(function () {
  'use strict';

  var STAGE_IDS = ['discovery', 'specification', 'implementation'];
  // How long a column takes to collapse or expand (its CSS transition), and a little after it for the layout to settle.
  var ANIM_MS = 380;
  var ANIM_SETTLE_MS = 40;
  // By then an example's late content (fonts, diagrams, editors) has loaded and its height is final.
  var CONTENT_SETTLED_MS = 1000;
  // Monaco measures an editor only once it is visible, so show it again as the column finishes opening.
  var EDITOR_RESHOW_MS = [460, 1000, 1600];
  // An example is at least this tall, and at most this share of the window or this many pixels, whichever is less.
  var EXAMPLE_MIN_HEIGHT_PX = 240;
  var EXAMPLE_MAX_WINDOW_SHARE = 0.88;
  var EXAMPLE_MAX_HEIGHT_PX = 1200;
  // Room around what an example shows: a story map's scrollbar, an editor's or preview's padding, an iframe's border.
  var STORY_MAP_ROOM_PX = 20;
  var CONTENT_ROOM_PX = 12;
  var IFRAME_ROOM_PX = 24;
  // A story map shown before its zoom fits may be drawn up to this much larger than its page.
  var STORY_MAP_MAX_FIT = 1.2;

  function heightCap() {
    return Math.min(window.innerHeight * EXAMPLE_MAX_WINDOW_SHARE, EXAMPLE_MAX_HEIGHT_PX);
  }

  /** The height a story map or framed diagram needs: its zoomed spacer once drawn, else its page fitted to the width. */
  function storyMapHeight(storyMap) {
    var spacer = storyMap.querySelector('.approach-stage-drawio__spacer');
    if (spacer && spacer.offsetHeight) return spacer.offsetHeight + STORY_MAP_ROOM_PX;
    var pageHeight = parseFloat(storyMap.dataset.pageH || '0');
    if (!pageHeight) return 0;
    var fit = storyMap.clientWidth > 0 ? storyMap.clientWidth / parseFloat(storyMap.dataset.pageW || pageHeight) : 1;
    return Math.ceil(pageHeight * Math.min(fit, STORY_MAP_MAX_FIT)) + STORY_MAP_ROOM_PX;
  }

  function iframeHeight(iframe) {
    var height = iframe.offsetHeight || parseFloat(iframe.getAttribute('height') || '0');
    return height ? Math.min(height + IFRAME_ROOM_PX, heightCap()) : 0;
  }

  function scrolledHeight(element) {
    return Math.min(element.scrollHeight + CONTENT_ROOM_PX, heightCap());
  }

  /** The height an example column's body needs for what it shows: a diagram, an editor, a preview, or an iframe. */
  function exampleContentHeight(body) {
    var heights = [EXAMPLE_MIN_HEIGHT_PX];
    var storyMap = body.querySelector('.approach-stage-drawio--story-map, .approach-stage-drawio--framed');
    var monaco = body.querySelector('.catalog-monaco');
    var preview = body.querySelector('.skill-md-preview');
    var iframe = body.querySelector('.catalog-example__frame, .catalog-example iframe');
    if (storyMap) {
      heights.push(storyMapHeight(storyMap));
      if (window.catalogDrawioRefitStoryMap) window.catalogDrawioRefitStoryMap(storyMap);
    }
    if (monaco) heights.push(scrolledHeight(monaco));
    if (preview) heights.push(scrolledHeight(preview));
    if (iframe) heights.push(iframeHeight(iframe));
    if (!storyMap && !monaco && !preview && !iframe) heights.push(scrolledHeight(body));
    return Math.min(Math.max(Math.ceil(Math.max.apply(null, heights)), EXAMPLE_MIN_HEIGHT_PX), heightCap());
  }

  /** One refine row: its stage buttons, the example column each opens, and its rewind and play buttons. */
  function RefineRow(host) {
    this.host = host;
  }

  RefineRow.prototype.column = function (stageId) {
    return this.host.querySelector('.approach-stage-column[data-stage-id="' + stageId + '"]');
  };

  RefineRow.prototype.openColumn = function () {
    return this.host.querySelector('.approach-stage-column.is-open');
  };

  RefineRow.prototype.isOpen = function (stageId) {
    var column = this.column(stageId);
    return !!column && column.classList.contains('is-open');
  };

  RefineRow.prototype.button = function (stageId) {
    var found = null;
    this.host.querySelectorAll('.approach-window__stage').forEach(function (button) {
      if (button.getAttribute('data-stage-id') === stageId) found = button;
    });
    return found;
  };

  /** The stages this row has an example column for, in stage order. */
  RefineRow.prototype.expandableIds = function () {
    var row = this;
    return STAGE_IDS.filter(function (stageId) {
      return !!row.column(stageId);
    });
  };

  RefineRow.prototype.paint = function () {
    var ids = this.expandableIds();
    var openCount = ids.filter(this.isOpen, this).length;
    var back = this.host.querySelector('[data-refine-nav="-1"]');
    var next = this.host.querySelector('[data-refine-nav="1"]');
    if (back) back.disabled = openCount === 0;
    if (next) next.disabled = ids.length === 0 || openCount === ids.length;
  };

  RefineRow.prototype.measure = function (column) {
    var body = column && column.querySelector('.approach-stage-column__body');
    if (!body) return;
    var height = exampleContentHeight(body) + 'px';
    this.host.style.setProperty('--approach-example-h', height);
    column.style.setProperty('--approach-example-h', height);
  };

  RefineRow.prototype.showEditors = function (column) {
    if (!window.catalogMonacoShow) return;
    column.querySelectorAll('.catalog-monaco').forEach(function (editor) {
      window.catalogMonacoShow(editor);
      EDITOR_RESHOW_MS.forEach(function (delay) {
        window.setTimeout(function () {
          window.catalogMonacoShow(editor);
        }, delay);
      });
    });
  };

  RefineRow.prototype.afterOpen = function (column) {
    var row = this;
    this.measure(column);
    if (window.catalogApproachStageScroll) window.catalogApproachStageScroll(column);
    if (window.catalogDrawioRefreshColumn) window.catalogDrawioRefreshColumn(column);
    this.showEditors(column);
    window.requestAnimationFrame(function () {
      row.measure(column);
    });
    window.setTimeout(function () {
      row.measure(column);
      if (window.catalogApproachStageScroll) window.catalogApproachStageScroll(column);
    }, ANIM_MS + ANIM_SETTLE_MS);
    window.setTimeout(function () {
      row.measure(column);
    }, CONTENT_SETTLED_MS);
  };

  RefineRow.prototype.setColumnOpen = function (stageId, open) {
    var column = this.column(stageId);
    var button = this.button(stageId);
    if (!column || !button) return;
    column.classList.toggle('is-open', open);
    var opening = this.host.querySelector('.approach-refine__opening[data-stage-id="' + stageId + '"]');
    if (opening) opening.classList.toggle('is-open', open);
    button.classList.toggle('is-active', open);
    button.setAttribute('aria-pressed', open ? 'true' : 'false');
    button.setAttribute('aria-expanded', open ? 'true' : 'false');
    this.paint();
  };

  RefineRow.prototype.open = function (stageId) {
    var row = this;
    var column = this.column(stageId);
    if (!column) return;
    this.expandableIds().forEach(function (otherId) {
      if (otherId !== stageId && row.isOpen(otherId)) row.setColumnOpen(otherId, false);
    });
    this.setColumnOpen(stageId, true);
    this.host.classList.add('is-open');
    this.afterOpen(column);
  };

  RefineRow.prototype.close = function (stageId) {
    this.setColumnOpen(stageId, false);
    this.host.classList.toggle('is-open', !!this.openColumn());
    if (window.catalogApproachStageScrollAfterClose) window.catalogApproachStageScrollAfterClose(this.host);
  };

  /** Collapse the column that is open, then open stageId once it has collapsed; right away when none is open. */
  RefineRow.prototype.switchTo = function (stageId) {
    var row = this;
    var open = this.openColumn();
    if (!open) {
      this.open(stageId);
      return;
    }
    this.setColumnOpen(open.getAttribute('data-stage-id'), false);
    this.host.classList.remove('is-open');
    window.setTimeout(function () {
      row.open(stageId);
    }, ANIM_MS);
  };

  RefineRow.prototype.toggle = function (stageId) {
    if (!this.column(stageId)) return;
    if (this.isOpen(stageId)) this.close(stageId);
    else this.switchTo(stageId);
  };

  RefineRow.prototype.openNext = function () {
    var next = this.expandableIds().filter(function (stageId) { return !this.isOpen(stageId); }, this)[0];
    if (!next) return false;
    if (this.button(next)) this.switchTo(next);
    return true;
  };

  RefineRow.prototype.closeLast = function () {
    var last = this.expandableIds().filter(this.isOpen, this).pop();
    if (!last) return false;
    if (this.button(last)) this.toggle(last);
    return true;
  };

  RefineRow.prototype.setStage = function (stageId, open) {
    var column = this.column(stageId);
    if (!column || !this.button(stageId)) return false;
    if (this.isOpen(stageId) === open) {
      if (open) this.afterOpen(column);
    } else if (open) {
      this.open(stageId);
    } else {
      this.close(stageId);
    }
    return true;
  };

  RefineRow.prototype.listen = function () {
    var row = this;
    this.host.querySelectorAll('.approach-window__stage').forEach(function (stageButton) {
      stageButton.addEventListener('click', function (event) {
        event.preventDefault();
        if (stageButton.classList.contains('approach-window__stage--context')) return;
        row.toggle(stageButton.getAttribute('data-stage-id'));
      });
    });
    this.host.querySelectorAll('[data-refine-nav]').forEach(function (navButton) {
      navButton.addEventListener('click', function (event) {
        event.preventDefault();
        if (navButton.getAttribute('data-refine-nav') === '1') row.openNext();
        else row.closeLast();
      });
    });
    if (typeof ResizeObserver !== 'undefined') {
      new ResizeObserver(function () {
        var open = row.openColumn();
        if (open) row.measure(open);
      }).observe(this.host);
    }
  };

  // The row of each refine host, made once, so the approach page's arrow keys and its buttons act on the same row.
  var rows = new WeakMap();

  function rowOf(host) {
    if (!rows.has(host)) rows.set(host, new RefineRow(host));
    return rows.get(host);
  }

  window.catalogRefineOpenNext = function (host) {
    return !!host && rowOf(host).openNext();
  };
  window.catalogRefineCloseLast = function (host) {
    return !!host && rowOf(host).closeLast();
  };
  window.catalogRefineSetStage = function (host, stageId, open) {
    return !!host && rowOf(host).setStage(stageId, open);
  };
  window.catalogRefinePaint = function (host) {
    rowOf(host).paint();
  };

  function init() {
    document.querySelectorAll('.approach-refine-row').forEach(function (host) {
      var row = rowOf(host);
      row.listen();
      row.paint();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
