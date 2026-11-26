// The approach page: the arrow keys walk its stages and then its principles, one principle opens at a time, and the
// example columns can be dragged sideways. Read by cdd-approach.html, whose stages it reads from data-stages.
(function () {
  'use strict';

  // The gap kept between the fixed site navigation and whatever the page scrolls to.
  var NAV_GAP_PX = 16;
  var PRODUCT_ENGINEERING = 'product-engineering';
  var ITERATE_AND_LEARN = 'iterate-and-learn';
  var REFINE_STAGES = ['discovery', 'specification', 'implementation', 'hardening'];

  function navigationHeight() {
    var nav = document.querySelector('.site-nav');
    return nav ? nav.getBoundingClientRect().height : 0;
  }

  function pageTopOf(element) {
    return element.getBoundingClientRect().top + window.pageYOffset;
  }

  function restartAnimation(element, className) {
    element.classList.remove(className);
    void element.offsetWidth; // reading the width makes the browser restart the animation when the class returns
    element.classList.add(className);
  }

  function escapeHtml(text) {
    return text.replace(/</g, '&lt;');
  }

  /** The stage descriptions the page lists, read from its data-stages; none when the attribute is not valid JSON. */
  function readStages(root) {
    try {
      return JSON.parse(root.getAttribute('data-stages') || '[]');
    } catch (err) {
      if (err instanceof SyntaxError) return null;
      throw err;
    }
  }

  /** The product-engineering principle's refine rows, walked one stage column at a time. */
  function ProductEngineeringWalk() {
    this.step = -1;
  }

  ProductEngineeringWalk.prototype.restart = function () {
    this.step = -1;
  };

  ProductEngineeringWalk.prototype.steps = function () {
    var steps = [];
    document.querySelectorAll('#pe-engineering .approach-refine-row').forEach(function (row) {
      REFINE_STAGES.forEach(function (stageId) {
        if (row.querySelector('.approach-stage-column[data-stage-id="' + stageId + '"]')) {
          steps.push({ row: row, stageId: stageId });
        }
      });
    });
    return steps;
  };

  /** Open the next stage column, or close the last opened one; false when there is no column left to walk to. */
  ProductEngineeringWalk.prototype.walk = function (delta) {
    if (!window.catalogRefineSetStage) return false;
    var steps = this.steps();
    if (!steps.length) return false;
    if (delta > 0) {
      if (this.step >= steps.length - 1) return false;
      this.step += 1;
      return window.catalogRefineSetStage(steps[this.step].row, steps[this.step].stageId, true);
    }
    if (this.step < 0) return false;
    window.catalogRefineSetStage(steps[this.step].row, steps[this.step].stageId, false);
    this.step -= 1;
    return true;
  };

  /** The approach page's stage buttons and principles, and where the arrow keys have walked to in them. */
  function ApproachPage(root, stages) {
    this.stages = stages;
    this.buttons = [].slice.call(root.querySelectorAll('.approach-stage'));
    this.principles = [].slice.call(root.querySelectorAll('.approach-principle'));
    this.titleElement = document.getElementById('approach-detail-title');
    this.bodyElement = document.getElementById('approach-detail-body');
    this.principlesElement = document.getElementById('approach-principles');
    this.productEngineering = new ProductEngineeringWalk();
    this.stageIndex = 0;
    this.principleIndex = -1;
    this.phase = 'stages';
    this.started = false;
    this.ready = false;
  }

  ApproachPage.prototype.principleSlug = function (principleIndex) {
    var principle = this.principles[principleIndex];
    return principle ? principle.getAttribute('data-principle') : '';
  };

  ApproachPage.prototype.showPrinciple = function (principleIndex) {
    this.principleIndex = principleIndex;
    this.principles.forEach(function (principle, index) {
      var open = index === principleIndex;
      principle.classList.toggle('is-open', open);
      var toggle = principle.querySelector('.approach-principle__toggle');
      if (toggle) toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  };

  /** Open a principle by choosing it or walking forward onto it; product engineering then starts at its first column. */
  ApproachPage.prototype.enterPrinciple = function (principleIndex) {
    this.showPrinciple(principleIndex);
    if (this.principleSlug(principleIndex) === PRODUCT_ENGINEERING) this.productEngineering.restart();
  };

  ApproachPage.prototype.closePrinciples = function () {
    this.showPrinciple(-1);
  };

  ApproachPage.prototype.onPrinciples = function () {
    return this.principleIndex >= 0;
  };

  ApproachPage.prototype.paintButtons = function () {
    var page = this;
    this.buttons.forEach(function (button, index) {
      var active = !page.onPrinciples() && index === page.stageIndex;
      button.classList.toggle('is-active', active);
      button.classList.remove('is-done');
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
      if (active) restartAnimation(button, 'is-flash');
    });
  };

  ApproachPage.prototype.paintStage = function (stage) {
    this.titleElement.textContent = stage.detail_title;
    this.bodyElement.classList.remove('is-enter');
    void this.bodyElement.offsetWidth; // restart the enter animation for the new stage's text
    this.bodyElement.innerHTML = stage.paras.map(function (para) {
      return '<li>' + escapeHtml(para) + '</li>';
    }).join('');
    this.bodyElement.classList.add('is-enter');
  };

  ApproachPage.prototype.paint = function (scroll) {
    this.paintButtons();
    var stage = this.stages[this.stageIndex];
    if (!stage) return;
    this.paintStage(stage);
    if (scroll && !this.onPrinciples() && this.started && !stage.example_href) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  ApproachPage.prototype.scrollToPrinciples = function () {
    if (!this.principlesElement) return;
    var top = pageTopOf(this.principlesElement) - (navigationHeight() + NAV_GAP_PX);
    window.scrollTo(0, Math.max(0, top));
  };

  ApproachPage.prototype.moveThroughStages = function (delta) {
    if (delta > 0 && this.stageIndex >= this.stages.length - 1) {
      this.phase = 'principles';
      this.closePrinciples();
      this.scrollToPrinciples();
      return;
    }
    if (delta < 0 && this.stageIndex <= 0) return;
    this.stageIndex += delta;
    this.closePrinciples();
    this.paint(false);
  };

  /** Inside a principle, the arrow keys first walk its own columns: iterate-and-learn's and product engineering's. */
  ApproachPage.prototype.walkInsidePrinciple = function (delta) {
    var refineRows = document.getElementById('approach-stage-examples');
    var slug = this.principleSlug(this.principleIndex);
    if (slug === PRODUCT_ENGINEERING) return this.productEngineering.walk(delta);
    if (slug !== ITERATE_AND_LEARN) return false;
    var step = delta > 0 ? window.catalogRefineOpenNext : window.catalogRefineCloseLast;
    return !!(step && step(refineRows));
  };

  ApproachPage.prototype.moveForwardThroughPrinciples = function () {
    if (this.principleIndex < 0) {
      this.showPrinciple(0);
    } else {
      if (this.walkInsidePrinciple(1)) return;
      if (this.principleIndex >= this.principles.length - 1) return;
      this.enterPrinciple(this.principleIndex + 1);
    }
    this.paint(false);
  };

  ApproachPage.prototype.moveBackThroughPrinciples = function () {
    if (this.walkInsidePrinciple(-1)) return;
    if (this.principleIndex > 0) {
      this.showPrinciple(this.principleIndex - 1);
    } else if (this.principleIndex === 0) {
      this.closePrinciples();
    } else {
      this.phase = 'stages';
      this.stageIndex = this.stages.length - 1;
    }
    this.paint(false);
  };

  ApproachPage.prototype.move = function (delta) {
    this.started = true;
    if (this.phase === 'stages') {
      this.moveThroughStages(delta);
    } else if (delta > 0) {
      this.moveForwardThroughPrinciples();
    } else {
      this.moveBackThroughPrinciples();
    }
  };

  ApproachPage.prototype.chooseStage = function (stageIndex) {
    this.started = true;
    this.phase = 'stages';
    this.stageIndex = stageIndex;
    var stage = this.stages[stageIndex];
    if (!stage || !stage.example_href) this.closePrinciples();
    this.paint(this.ready);
  };

  ApproachPage.prototype.togglePrinciple = function (principleIndex) {
    this.started = true;
    this.phase = 'principles';
    if (this.principleIndex === principleIndex) this.closePrinciples();
    else this.enterPrinciple(principleIndex);
    this.paint(false);
  };

  ApproachPage.prototype.listenToStageButtons = function () {
    var page = this;
    this.buttons.forEach(function (button, stageIndex) {
      button.addEventListener('click', function (event) {
        if (event.target.closest && event.target.closest('a')) return;
        page.chooseStage(stageIndex);
      });
      button.addEventListener('keydown', function (event) {
        if (event.target !== button) return;
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          button.click();
        }
      });
    });
  };

  ApproachPage.prototype.listenToPrinciples = function () {
    var page = this;
    this.principles.forEach(function (principle, principleIndex) {
      var toggle = principle.querySelector('.approach-principle__toggle');
      if (toggle) toggle.addEventListener('click', function () { page.togglePrinciple(principleIndex); });
    });
  };

  ApproachPage.prototype.listenToArrowKeys = function () {
    var page = this;
    document.addEventListener('keydown', function (event) {
      if (event.target.closest('input,textarea,select,a')) return;
      var delta = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[event.key];
      if (!delta) return;
      event.preventDefault();
      page.move(delta);
    });
  };

  ApproachPage.prototype.start = function () {
    this.listenToStageButtons();
    this.listenToPrinciples();
    this.listenToArrowKeys();
    this.paint(false);
    this.ready = true;
  };

  /** Dragging an example strip sideways scrolls it, unless the drag starts on something that takes the pointer itself. */
  function listenToColumnDrags() {
    var drag = null;
    document.addEventListener('pointerdown', function (event) {
      var clip = event.target.closest && event.target.closest('.approach-stage-examples__clip');
      if (!clip || event.button !== 0) return;
      if (event.target.closest('button,a,input,textarea,select,.catalog-monaco,.mxgraph,.skill-drawio-wrap')) return;
      drag = { clip: clip, startX: event.clientX, startScrollLeft: clip.scrollLeft };
      clip.classList.add('is-dragging');
      if (clip.setPointerCapture) clip.setPointerCapture(event.pointerId);
    });
    document.addEventListener('pointermove', function (event) {
      if (drag) drag.clip.scrollLeft = drag.startScrollLeft - (event.clientX - drag.startX);
    });
    document.addEventListener('pointerup', function () {
      if (!drag) return;
      drag.clip.classList.remove('is-dragging');
      drag = null;
    });
  }

  var root = document.getElementById('approach-page');
  if (!root) return;
  var stages = readStages(root);
  if (!stages) return;
  new ApproachPage(root, stages).start();
  listenToColumnDrags();
})();
