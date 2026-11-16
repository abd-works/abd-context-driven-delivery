/* Foundry hub CDD tour — requires .foundry-kanban-surface on the page */
(function () {
  'use strict';

  var PERSPECTIVE_ORDER = ['sdd', 'arc', 'uxd', 'bdd', 'ddd'];

  var SCOPE_SLIDE_HTML =
    '<ul class="foundry-guide__bullets">' +
    '<li>Limit context to cognitive load of the team, so humans can guide, review, and adjust what AI generates.</li>' +
    '<li>Keeping context windows small leads to better output, even with frontier models.</li>' +
    '<li>Layer context with increased fidelity through successive generations — so humans and AI can focus on big decisions before small decisions.</li>' +
    '</ul>';

  var PERSPECTIVES_LEAD_HTML =
    '<ul class="foundry-guide__bullets">' +
    '<li>The fundamentals of product engineering have not changed. Ground AI delivery in practices so you can develop artifacts that are easy to drill down and roll up — so the right conversations and decisions sit at the right level of detail — define specifications that also serve as automated tests so context is executed and machine validated, connect outcomes to code in one shared language, and force simplicity from outcome and impact through build and operation.</li>' +
    '<li>Guide AI through Customer Discovery, UX, Story Specs, DevOps, and Software Craftsmanship.</li>' +
    '</ul>';

  var EXECUTABLE_LEAD_HTML =
    '<ul class="foundry-guide__bullets">' +
    '<li>Your code is the primary source of truth for how things actually work — linking, versioning, reviews, and auditing come for free.</li>' +
    '<li>Structure context into executable, machine-executable specification that tests the actual solution.</li>' +
    '<li>Write code so that it is a direct expression of the design — easily transformed to docs and back.</li>' +
    '</ul>';

  var CHANGE_SLIDE_HTML =
    '<p class="foundry-guide__lead">Context-Driven Delivery will fundamentally change how people work. AI is moving people towards a <strong>builder culture</strong>.</p>' +
    '<div class="foundry-guide__change-rows">' +
    '<div class="foundry-guide__change-row foundry-guide__change-row--sdd">' +
    '<span class="foundry-guide__change-name">Stories</span>' +
    '<ul class="foundry-guide__change-bullets">' +
    '<li>Story maps, scenarios, and acceptance tests are one continuous loop—not handoffs between roles.</li>' +
    '<li>Every test tier iterates the same way: write behaviour, write code, run, fix—not as separate stages.</li>' +
    '</ul></div>' +
    '<div class="foundry-guide__change-row foundry-guide__change-row--arc">' +
    '<span class="foundry-guide__change-name">Clean Engineering</span>' +
    '<ul class="foundry-guide__change-bullets">' +
    '<li>Deepen modules → model → code as executable structure, not narrative design docs.</li>' +
    '<li>Templated contracts and patterns accelerate AI when extending systems already in production.</li>' +
    '</ul></div>' +
    '<div class="foundry-guide__change-row foundry-guide__change-row--uxd">' +
    '<span class="foundry-guide__change-name">User Experience</span>' +
    '<ul class="foundry-guide__change-bullets">' +
    '<li>UX keeps evolving with stories and model—not arriving in one complete pass.</li>' +
    '<li>Lock navigation and information flow before controls and labels—overall picture first, detail second.</li>' +
    '</ul></div>' +
    '<div class="foundry-guide__change-row foundry-guide__change-row--bdd">' +
    '<span class="foundry-guide__change-name">Behavior-Driven Development</span>' +
    '<ul class="foundry-guide__change-bullets">' +
    '<li>Domain vocabulary becomes nested, passing tests—not prose checklists.</li>' +
    '<li>Behaviour specs and production code stay in the same loop so AI can verify outcomes.</li>' +
    '</ul></div>' +
    '<div class="foundry-guide__change-row foundry-guide__change-row--ddd">' +
    '<span class="foundry-guide__change-name">Domain-Driven Design</span>' +
    '<ul class="foundry-guide__change-bullets">' +
    '<li>Business concepts must be explicit artifacts—mandatory at scale.</li>' +
    '<li>Bounded contexts and aggregates isolate domain logic so AI can verify code against the model.</li>' +
    '</ul></div>' +
    '<div class="foundry-guide__change-row foundry-guide__change-row--team">' +
    '<span class="foundry-guide__change-name">The team</span>' +
    '<ul class="foundry-guide__change-bullets">' +
    '<li>Large squads (9–12) working on a single outcome will only accelerate dysfunction.</li>' +
    '<li>At this pace, the days of a team member disappearing for a couple of days to work in isolation are no longer feasible.</li>' +
    '<li>Groups of 3–4 highly interactive and paired work—in the same room, virtual or physical; hand-offs are frequent and teamwork needs to be real across legacy job functions.</li>' +
    '<li>Expertise builds context, skills, and scaffolding; specialists validate output. The goal is builder capability and culture across the team.</li>' +
    '</ul></div>' +
    '</div>';

  var TEXT_EXPAND_MS = 320;
  var TEXT_APPEAR_MS = 320;
  var STEP_FADE_MS = 320;
  // How long the smooth scroll to the guide takes before the step's text fades in.
  var SCROLL_SETTLE_MS = 320;
  // The gap kept between the fixed site navigation and the guide the tour scrolls to.
  var NAV_GAP_PX = 16;
  // Overlay cells span the board right of the practice labels, at least this wide, stopping short of its right edge.
  var MIN_OVERLAY_WIDTH_PX = 80;
  var OVERLAY_RIGHT_GAP_PX = 6;
  // A tooltip opens after the pointer rests this long, closes after it fades, and sits this far from what it explains.
  var TIP_SHOW_DELAY_MS = 260;
  var TIP_HIDE_MS = 140;
  var TIP_OFFSET_PX = 8;

  var PERSPECTIVE_BY_KEY = {
    sdd: 'A shared map of the product: actors, systems, and the interactions that deliver the solution.',
    arc: 'Object design from modules through contracts to production code — structure AI can generate and verify.',
    uxd: 'How users navigate and act on the solution — information architecture, screens, and interface.',
    bdd: 'Domain vocabulary turned into hierarchical, passing behaviour tests.',
    ddd: 'Bounded contexts, aggregates, and building blocks that name and protect the business model.'
  };

  var SPEC_CELL_TEXT = {
    sdd: 'Executable scenario-specifications with real-world examples',
    arc: 'Deep modules with explicit, narrow seams and type-safe contracts',
    uxd: 'Interface mockups that work according to story specs and design templates',
    bdd: 'Nested describe/it behaviour specs that pass',
    ddd: 'Templates that generate domain building blocks for the target architecture'
  };

  var CONTEXT_STORMING_HTML =
    '<ul class="foundry-guide__bullets"><li>Define and connect context across product, engineering, and operations. Bring those artifacts into one knowledge graph, in place of scattered docs, tickets, and tribal memory.</li><li>Collaboratively build artifacts at the right level of abstraction to support the right level of decision making.</li></ul>';

  // The board's classes for each state the tour puts it in; each state shows what the one before it did, and more.
  var BOARD_STATE_CLASSES = {
    blank: ['is-tour-blank'],
    stages: ['is-tour-stages'],
    practices: ['is-tour-practices'],
    'practices-shown': ['is-tour-practices', 'is-tour-practices-shown'],
    'spec-focus': ['is-tour-practices', 'is-tour-practices-shown', 'is-tour-spec-focus'],
    full: ['is-tour-practices', 'is-tour-practices-shown', 'is-tour-fidelities-shown']
  };
  var TOUR_BOARD_CLASSES = [
    'is-tour-blank', 'is-tour-stages', 'is-tour-practices', 'is-tour-practices-shown',
    'is-tour-fidelities-shown', 'is-tour-spec-focus', 'is-tour-details-open'
  ];

  var surface = document.querySelector('.foundry-kanban-surface');
  var ring = document.getElementById('travel-ring');
  var guidePanel = document.getElementById('foundry-guide');
  var toggleBtn = document.getElementById('cdd-toggle');
  var guideTag = document.getElementById('guide-tag');
  var guideText = document.getElementById('guide-text');
  var advanceBtn = document.getElementById('tour-advance');
  var IDLE_HINT = 'to advance';
  var rowLabels = Array.prototype.slice.call(
    document.querySelectorAll('.foundry-perspective-label')
  ).filter(function (label) {
    return label.getAttribute('data-perspective') !== 'cdd';
  });

  var mode = 'idle';
  var currentRunId = 0;
  var tourBusy = false;

  if (!surface || !ring || !toggleBtn || !guidePanel) return;

  var cddBoard = surface.classList.contains('foundry-kanban-surface--cdd-always-expanded');

  function showIdleHint() {
    if (guideTag) guideTag.textContent = IDLE_HINT;
  }

  function boardElement() {
    return document.querySelector('.foundry-board-grid') || document.getElementById('board');
  }

  function setTourBoardState(state) {
    surface.classList.remove.apply(surface.classList, TOUR_BOARD_CLASSES);
    surface.classList.add.apply(surface.classList, BOARD_STATE_CLASSES[state] || []);
  }

  /** The skill rows across the columns open or close, through the board's own control (catalog-foundry-skill-nav.js). */
  function setSkillsExpanded(expanded) {
    if (typeof window.catalogBoardSetSkillsExpanded === 'function') window.catalogBoardSetSkillsExpanded(expanded);
  }

  function pause(delay) {
    return new Promise(function (resolve) {
      window.setTimeout(resolve, delay);
    });
  }

  function nextTwoFrames() {
    return new Promise(function (resolve) {
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(resolve);
      });
    });
  }

  function nextFrame(change) {
    return new Promise(function (resolve) {
      window.requestAnimationFrame(function () {
        change();
        resolve();
      });
    });
  }

  function scrollTourToFold() {
    var target = guidePanel || boardElement();
    if (!target) return Promise.resolve();
    var nav = document.querySelector('.site-nav');
    var navHeight = nav ? nav.getBoundingClientRect().height : 0;
    var y = target.getBoundingClientRect().top + window.pageYOffset - (navHeight + NAV_GAP_PX);
    window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    return pause(SCROLL_SETTLE_MS);
  }

  /**
   * The explanations that float over the board: a column head's scope or a skill's summary, shown after the pointer
   * rests on it. Each tooltip moves to the body while it shows, so the board's overflow does not clip it, and returns
   * to its holder when it hides.
   */
  function FloatingTooltips() {
    this.activeTip = null;
    this.activeHolder = null;
    this.hideTimer = null;
  }

  FloatingTooltips.prototype.cancelHide = function () {
    if (!this.hideTimer) return;
    window.clearTimeout(this.hideTimer);
    this.hideTimer = null;
  };

  FloatingTooltips.prototype.position = function (trigger, tip) {
    var triggerRect = trigger.getBoundingClientRect();
    tip.style.left = Math.max(TIP_OFFSET_PX, triggerRect.left) + 'px';
    tip.style.top = triggerRect.bottom + TIP_OFFSET_PX + 'px';
  };

  FloatingTooltips.prototype.putBack = function (tip, holder) {
    tip.classList.remove('is-floating', 'is-visible');
    tip.style.left = '';
    tip.style.top = '';
    holder.appendChild(tip);
  };

  FloatingTooltips.prototype.hide = function (immediate) {
    this.cancelHide();
    if (!this.activeTip || !this.activeHolder) return;
    var tooltips = this;
    var tip = this.activeTip;
    var holder = this.activeHolder;
    this.activeTip = null;
    this.activeHolder = null;
    tip.classList.remove('is-visible');
    if (immediate) {
      this.putBack(tip, holder);
      return;
    }
    this.hideTimer = window.setTimeout(function () {
      tooltips.hideTimer = null;
      tooltips.putBack(tip, holder);
    }, TIP_HIDE_MS);
  };

  FloatingTooltips.prototype.show = function (trigger, holder) {
    this.cancelHide();
    var tip = holder && holder.querySelector('.kb-col-shape-tooltip');
    if (!tip) return;
    if (this.activeTip === tip) {
      this.position(trigger, tip);
      return;
    }
    if (this.activeTip && this.activeHolder) this.putBack(this.activeTip, this.activeHolder);
    tip.classList.add('is-floating');
    document.body.appendChild(tip);
    this.position(trigger, tip);
    void tip.offsetWidth; // lay the tip out where it floats before it fades in
    tip.classList.add('is-visible');
    this.activeTip = tip;
    this.activeHolder = holder;
  };

  /** Show the tooltip in each trigger's holder once the pointer rests on the trigger. */
  FloatingTooltips.prototype.showOnHover = function (triggers, holderSelector) {
    var tooltips = this;
    triggers.forEach(function (trigger) {
      var showTimer = null;
      trigger.addEventListener('mouseenter', function () {
        var holder = trigger.querySelector(holderSelector);
        showTimer = window.setTimeout(function () {
          showTimer = null;
          tooltips.show(trigger, holder);
        }, TIP_SHOW_DELAY_MS);
      });
      trigger.addEventListener('mouseleave', function () {
        if (showTimer) window.clearTimeout(showTimer);
        showTimer = null;
        tooltips.hide(false);
      });
    });
  };

  FloatingTooltips.prototype.listen = function () {
    var tooltips = this;
    this.showOnHover(surface.querySelectorAll('.kb-col-head'), '.kb-col-scope-shape-wrap');
    this.showOnHover(surface.querySelectorAll('.kb-ticket.aad-skill.has-skill-tooltip'), '.kb-skill-tooltip-wrap');
    window.addEventListener('scroll', function () { tooltips.hide(true); }, true);
    window.addEventListener('resize', function () { tooltips.hide(true); });
  };

  function clearLanded() {
    Array.prototype.forEach.call(
      document.querySelectorAll('.is-ring-landed'),
      function (landed) { landed.classList.remove('is-ring-landed'); }
    );
  }

  function cancelRingAnimations() {
    if (ring.getAnimations) {
      ring.getAnimations().forEach(function (animation) { animation.cancel(); });
    }
  }

  function hideRing() {
    cancelRingAnimations();
    ring.classList.remove('is-visible');
    ring.style.opacity = '0';
  }

  function waitForTransition(element, property, fallbackMs) {
    return new Promise(function (resolve) {
      var settled = false;
      function finish() {
        if (settled) return;
        settled = true;
        element.removeEventListener('transitionend', onEnd);
        resolve();
      }
      function onEnd(event) {
        if (event.target === element && event.propertyName === property) finish();
      }
      element.addEventListener('transitionend', onEnd);
      window.setTimeout(finish, fallbackMs);
    });
  }

  function clearStagesFocus() {
    var board = boardElement();
    if (board) board.classList.remove('is-tour-stages-focus');
  }

  function ensurePerspectiveOverlay() {
    var board = boardElement();
    if (!board) return null;
    var overlay = document.getElementById('board-perspective-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'board-perspective-overlay';
      overlay.className = 'foundry-board-overlay';
      overlay.setAttribute('aria-hidden', 'true');
      board.appendChild(overlay);
    }
    return overlay;
  }

  /** Where overlay cells sit: from the practice labels' right edge to just short of the board's right edge. */
  function overlaySpan(board, practiceCol) {
    var boardRect = board.getBoundingClientRect();
    var anchor = practiceCol.querySelector('[data-perspective]');
    var anchorRight = anchor ? anchor.getBoundingClientRect().right : practiceCol.getBoundingClientRect().right;
    return {
      boardRect: boardRect,
      left: Math.round(anchorRight - boardRect.left),
      width: Math.max(MIN_OVERLAY_WIDTH_PX, Math.round(boardRect.right - anchorRight - OVERLAY_RIGHT_GAP_PX))
    };
  }

  /** Place an overlay element across the span, level with what it lines up with. */
  function placeAcrossSpan(element, span, levelWith) {
    var levelRect = levelWith.getBoundingClientRect();
    element.style.top = Math.round(levelRect.top - span.boardRect.top) + 'px';
    element.style.height = Math.round(levelRect.height) + 'px';
    element.style.left = span.left + 'px';
    element.style.width = span.width + 'px';
  }

  function specColumnHead() {
    return document.querySelector('.kb-col[data-stage="spec"] > .kb-col-head')
      || document.querySelector('.kb-col[data-stage="specification"] > .kb-col-head');
  }

  function clearSpecHeaderAlign() {
    var head = specColumnHead();
    if (!head) return;
    ['position', 'left', 'width', 'height', 'top', 'zIndex', 'margin'].forEach(function (property) {
      head.style[property] = '';
    });
  }

  /** Stretch the specification column's head across the board, over the side columns the tour collapsed. */
  function lineUpSpecHeader() {
    clearSpecHeaderAlign();
    var board = boardElement();
    var head = specColumnHead();
    var practiceCol = document.querySelector('.foundry-practice-col');
    if (!board || !head || !practiceCol) return;
    void head.offsetHeight; // measure the head where the board lays it out, not where it was stretched
    var span = overlaySpan(board, practiceCol);
    var colRect = head.parentElement.getBoundingClientRect();
    var headRect = head.getBoundingClientRect();
    head.style.position = 'absolute';
    head.style.boxSizing = 'border-box';
    head.style.zIndex = '3';
    head.style.margin = '0';
    head.style.top = Math.round(headRect.top - colRect.top) + 'px';
    head.style.height = Math.round(headRect.height) + 'px';
    head.style.left = Math.round((span.boardRect.left + span.left) - colRect.left) + 'px';
    head.style.width = span.width + 'px';
  }

  function hidePerspectiveOverlay() {
    clearSpecHeaderAlign();
    var board = boardElement();
    var overlay = document.getElementById('board-perspective-overlay');
    if (board) board.classList.remove('has-perspective-overlay');
    if (overlay) {
      overlay.classList.remove('is-visible');
      overlay.innerHTML = '';
    }
  }

  function setCollapsedSideColumns(collapsed) {
    var board = boardElement();
    if (!board) return;
    ['discovery', 'engineer'].forEach(function (stage) {
      board.querySelectorAll(':scope > .kb-col[data-stage="' + stage + '"]').forEach(function (col) {
        col.classList.toggle('kb-col--collapsed', collapsed);
      });
    });
    board.classList.toggle('is-tour-spec-cols', collapsed);
    if (!collapsed) clearSpecHeaderAlign();
  }

  /** One overlay cell per practice row, each holding that practice's text. */
  function showAlignedCells(texts) {
    var board = boardElement();
    var practiceCol = document.querySelector('.foundry-practice-col');
    var overlay = ensurePerspectiveOverlay();
    if (!board || !practiceCol || !overlay) return;
    void board.offsetHeight; // measure the board after the step's classes have laid it out
    var span = overlaySpan(board, practiceCol);
    overlay.innerHTML = '';
    PERSPECTIVE_ORDER.forEach(function (key) {
      var label = practiceCol.querySelector('[data-perspective="' + key + '"]');
      if (!label || !texts[key]) return;
      var cell = document.createElement('div');
      cell.className = 'foundry-board-overlay__row is-shown';
      placeAcrossSpan(cell, span, label);
      cell.innerHTML = '<span class="foundry-board-overlay__desc">' + texts[key] + '</span>';
      overlay.appendChild(cell);
    });
    board.classList.add('has-perspective-overlay');
    overlay.classList.add('is-visible');
  }

  /** An empty head over the overlay cells, level with the practice column's head. */
  function placeEmptyColumnHead() {
    var board = boardElement();
    var practiceCol = document.querySelector('.foundry-practice-col');
    var overlay = document.getElementById('board-perspective-overlay');
    var practiceHead = practiceCol && practiceCol.querySelector('.foundry-practice-col__cdd-head');
    if (!board || !overlay || !practiceHead) return;
    var head = document.createElement('div');
    head.className = 'foundry-board-overlay__head';
    placeAcrossSpan(head, overlaySpan(board, practiceCol), practiceHead);
    overlay.appendChild(head);
  }

  function showPerspectiveOverlay() {
    showAlignedCells(PERSPECTIVE_BY_KEY);
    placeEmptyColumnHead();
  }

  function showSpecCells() {
    showAlignedCells(SPEC_CELL_TEXT);
    lineUpSpecHeader();
  }

  /** Run the steps one after another; a newer run (a key pressed again, the tour reset) stops this one between steps. */
  function runTour(steps) {
    currentRunId++;
    var runId = currentRunId;
    tourBusy = true;
    var chain = Promise.resolve();
    steps.forEach(function (step) {
      chain = chain.then(function () {
        if (runId !== currentRunId) return;
        return step(runId);
      });
    });
    function finished() {
      if (runId === currentRunId) tourBusy = false;
    }
    return chain.then(finished, finished);
  }

  function bumpRun() {
    currentRunId++;
    hideRing();
    tourBusy = false;
  }

  function hideGuideText() {
    guideText.classList.remove('is-expanding', 'is-revealed', 'is-tall');
    guideText.innerHTML = '';
  }

  function fadeOutTogether() {
    surface.classList.add('is-tour-fading-out');
    guideText.classList.remove('is-revealed');
    return pause(STEP_FADE_MS).then(function () {
      guideText.classList.remove('is-tall');
      guideText.innerHTML = '';
    });
  }

  /** Size the guide box to its tallest slide, so it does not jump as the tour moves between them. */
  function fitGuideBox() {
    if (!guideText) return;
    var width = guideText.getBoundingClientRect().width;
    if (!width) return;
    var probe = document.createElement('div');
    probe.style.cssText = 'position:absolute;left:-9999px;top:0;visibility:hidden;height:auto;';
    probe.style.width = width + 'px';
    document.body.appendChild(probe);
    var tallest = 0;
    [SCOPE_SLIDE_HTML, PERSPECTIVES_LEAD_HTML, EXECUTABLE_LEAD_HTML].forEach(function (html) {
      probe.innerHTML = html;
      tallest = Math.max(tallest, probe.offsetHeight);
    });
    probe.remove();
    if (!tallest) return;
    if (guidePanel) guidePanel.style.setProperty('--guide-slide-h', tallest + 'px');
    guideText.style.height = tallest + 'px';
    guideText.style.maxHeight = tallest + 'px';
  }

  /** In one frame: expand the guide box, reveal the step's text, and show the board it describes. */
  function fadeInTogether(step) {
    guidePanel.classList.add('is-tour-active');
    guideTag.classList.remove('is-waiting');
    showIdleHint();
    guideText.classList.remove('is-revealed', 'is-tall');
    guideText.innerHTML = step.html;
    if (step.tall) guideText.classList.add('is-tall');
    if (step.openDetails) surface.classList.add('is-tour-details-open');
    fitGuideBox();
    return nextFrame(function () {
      guideText.classList.add('is-expanding', 'is-revealed');
      surface.classList.remove('is-tour-fading-out');
    }).then(function () {
      return pause(STEP_FADE_MS);
    });
  }

  /** Fade out the text and board together, change the board, then fade the new text and board in together. */
  function transitionTourStep(runId, step) {
    return fadeOutTogether().then(function () {
      if (runId !== currentRunId) return;
      step.applyBoard();
      surface.classList.add('is-tour-fading-out'); // keep the new board hidden until the shared fade-in
      if (step.openDetails) surface.classList.add('is-tour-details-open');
      return nextTwoFrames();
    }).then(function () {
      if (runId !== currentRunId) return;
      return fadeInTogether(step);
    }).then(function () {
      if (runId === currentRunId) showIdleHint();
    });
  }

  /** Run one tour step, scrolling the guide into view first when the step asks. */
  function runStep(step) {
    return runTour([
      function (runId) {
        var ready = step.scrollFirst ? scrollTourToFold() : Promise.resolve();
        return ready.then(function () {
          if (runId === currentRunId) return transitionTourStep(runId, step);
        });
      }
    ]);
  }

  function setGuideWaiting() {
    hideRing();
    guidePanel.classList.add('is-tour-active');
    guideTag.classList.remove('is-waiting');
    showIdleHint();
  }

  /** Expand the guide box, then fade the text in. */
  function revealGuideText(html) {
    guidePanel.classList.add('is-tour-active');
    guideText.classList.remove('is-expanding', 'is-revealed', 'is-tall');
    guideText.innerHTML = html;
    guideTag.classList.remove('is-waiting');
    showIdleHint();
    return nextFrame(function () { guideText.classList.add('is-expanding'); })
      .then(function () { return waitForTransition(guideText, 'max-height', TEXT_EXPAND_MS); })
      .then(nextTwoFrames)
      .then(function () { return nextFrame(function () { guideText.classList.add('is-revealed'); }); })
      .then(function () { return waitForTransition(guideText, 'opacity', TEXT_APPEAR_MS); });
  }

  /** Begin a step: clear what the last one left on the board and name the step on the tour button. */
  function beginStep(stepMode, label) {
    clearLanded();
    hideRing();
    mode = stepMode;
    if (label) toggleBtn.textContent = label;
  }

  function resetTour() {
    bumpRun();
    beginStep('idle', 'Start tour');
    clearStagesFocus();
    hidePerspectiveOverlay();
    setCollapsedSideColumns(false);
    surface.classList.remove('is-tour-fading-out');
    toggleBtn.classList.remove('is-active');
    guidePanel.classList.remove('is-tour-active');
    guideTag.classList.remove('is-waiting');
    showIdleHint();
    hideGuideText();
    setTourBoardState('blank');
    if (!cddBoard) setSkillsExpanded(false);
  }

  /** Iterate and Learn — scroll, then text + stage details fade in together. */
  function animateScopeTour() {
    beginStep('scope', 'Iterate and Learn');
    hidePerspectiveOverlay();
    setCollapsedSideColumns(false);
    toggleBtn.classList.add('is-active');
    guidePanel.classList.add('is-tour-active');
    showIdleHint();
    guideTag.classList.add('is-waiting');
    return runStep({
      scrollFirst: true,
      html: SCOPE_SLIDE_HTML,
      openDetails: true,
      applyBoard: function () { setTourBoardState('stages'); }
    });
  }

  /** Product Engineering — practices + descriptions. */
  function animatePerspectiveTour() {
    beginStep('perspective', 'Product Engineering');
    setGuideWaiting();
    setCollapsedSideColumns(false);
    setSkillsExpanded(true);
    return runStep({
      scrollFirst: true,
      html: PERSPECTIVES_LEAD_HTML,
      applyBoard: function () {
        setTourBoardState('practices');
        surface.classList.add('is-tour-practices-shown');
        showPerspectiveOverlay();
      }
    });
  }

  /** Code Is Context — spec focus. */
  function animateSpecColumn() {
    beginStep('column', 'Code Is Context');
    setGuideWaiting();
    return runStep({
      html: EXECUTABLE_LEAD_HTML,
      applyBoard: function () {
        setTourBoardState('spec-focus');
        setCollapsedSideColumns(true);
        showSpecCells();
      }
    });
  }

  /** Context Storming — text and all fidelities fade in together. */
  function animateShowPractices() {
    beginStep('fidelities', 'Practice fidelities');
    hidePerspectiveOverlay();
    setGuideWaiting();
    return runStep({
      html: CONTEXT_STORMING_HTML,
      applyBoard: function () {
        setCollapsedSideColumns(false);
        setTourBoardState('full');
      }
    });
  }

  /** Change implications — the final panel. */
  function animateChangeImplications() {
    beginStep('change', '');
    hidePerspectiveOverlay();
    setGuideWaiting();
    return runStep({
      html: CHANGE_SLIDE_HTML,
      tall: true,
      applyBoard: function () {
        setCollapsedSideColumns(false);
        setTourBoardState('full');
      }
    });
  }

  // Where the arrow keys lead from each step: forward to the next step, back to the one before.
  var TOUR_MOVES = {
    idle: { next: animatePerspectiveTour },
    perspective: { next: animateSpecColumn, back: resetTour },
    column: {
      next: animateScopeTour,
      back: function () {
        setCollapsedSideColumns(false);
        animatePerspectiveTour();
      }
    },
    scope: {
      next: animateShowPractices,
      back: function () {
        hidePerspectiveOverlay();
        animateSpecColumn();
      }
    },
    fidelities: { next: animateChangeImplications, back: animateScopeTour },
    change: { next: resetTour, back: animateShowPractices }
  };

  function move(direction) {
    if (tourBusy) return;
    var moveTo = TOUR_MOVES[mode] && TOUR_MOVES[mode][direction];
    if (moveTo) moveTo();
  }

  function showPracticeDescription(label) {
    var key = label.getAttribute('data-perspective');
    hideRing();
    guideTag.classList.remove('is-waiting');
    if (mode === 'perspective') {
      showPerspectiveOverlay();
      showIdleHint();
      return;
    }
    revealGuideText('<p class="foundry-guide__lead">' + PERSPECTIVE_BY_KEY[key] + '</p>');
  }

  function listen() {
    toggleBtn.addEventListener('click', function () {
      if (mode === 'idle') move('next');
      else resetTour();
    });
    if (advanceBtn) advanceBtn.addEventListener('click', function () { move('next'); });
    rowLabels.forEach(function (label) {
      label.addEventListener('click', function (event) {
        if (mode !== 'perspective' && mode !== 'column') return;
        if (!PERSPECTIVE_BY_KEY[label.getAttribute('data-perspective')]) return;
        event.preventDefault();
        showPracticeDescription(label);
      });
    });
    document.addEventListener('keydown', function (event) {
      if (event.target.closest('input, textarea, select')) return;
      var direction = { ArrowRight: 'next', ' ': 'next', Enter: 'next', ArrowLeft: 'back' }[event.key];
      if (!direction) return;
      event.preventDefault();
      move(direction);
    });
  }

  function relayout() {
    if (mode === 'perspective') showPerspectiveOverlay();
    if (mode === 'column') showSpecCells();
  }

  function followResizes() {
    if (window.ResizeObserver && guidePanel) {
      new ResizeObserver(function () {
        if (mode !== 'idle') hideRing();
        relayout();
      }).observe(guidePanel);
    }
    window.addEventListener('resize', function () {
      fitGuideBox();
      relayout();
      hideRing();
    });
  }

  setTourBoardState('blank');
  new FloatingTooltips().listen();
  listen();
  followResizes();
  fitGuideBox();
})();
