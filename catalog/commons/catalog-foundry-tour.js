/* Foundry hub CDD tour — requires .foundry-kanban-surface on the page */
(function () {
  'use strict';

  var STAGES = ['discovery', 'spec', 'engineer'];
  var PERSPECTIVE_ORDER = ['sdd', 'arc', 'uxd', 'bdd', 'ddd'];

  var SCOPE_SLIDE_HTML =
    '<ul class="foundry-guide__bullets">' +
    '<li>Limit context to cognitive load of the team, so humans can guide, review, and adjust what AI generates.</li>' +
    '<li>Keeping context windows small leads to better output, even with frontier models.</li>' +
    '<li>Layer context through successive generations — adjust fidelity based on what has already been produced.</li>' +
    '</ul>';

  var PERSPECTIVES_LEAD_HTML =
    '<ul class="foundry-guide__bullets">' +
    '<li>The fundamentals of product engineering have not changed. Ground AI delivery in test-driven, iterative practices that easily connect business outcomes, user impact, and system behavior to technology implementation.</li>' +
    '<li>Guide AI through Customer Discovery, UX, Story Specs, DevOps, and Software Craftsmanship.</li>' +
    '</ul>';

  var PERSPECTIVES_SLIDE_HTML =
    PERSPECTIVES_LEAD_HTML +
    '<div class="foundry-guide__perspectives">' +
    '<div class="foundry-guide__perspective-row foundry-guide__perspective-row--sdd"><span class="foundry-guide__perspective-name">Stories</span><span class="foundry-guide__perspective-desc">A shared map of the product: actors, systems, and the interactions that deliver the solution.</span></div>' +
    '<div class="foundry-guide__perspective-row foundry-guide__perspective-row--arc"><span class="foundry-guide__perspective-name">Clean Engineering</span><span class="foundry-guide__perspective-desc">Object design from modules through contracts to production code — structure AI can generate and verify.</span></div>' +
    '<div class="foundry-guide__perspective-row foundry-guide__perspective-row--uxd"><span class="foundry-guide__perspective-name">User Experience</span><span class="foundry-guide__perspective-desc">How users navigate and act on the solution — information architecture, screens, and interface.</span></div>' +
    '<div class="foundry-guide__perspective-row foundry-guide__perspective-row--bdd"><span class="foundry-guide__perspective-name">Behavior-Driven Development</span><span class="foundry-guide__perspective-desc">Domain vocabulary turned into hierarchical, passing behaviour tests.</span></div>' +
    '<div class="foundry-guide__perspective-row foundry-guide__perspective-row--ddd"><span class="foundry-guide__perspective-name">Domain-Driven Design</span><span class="foundry-guide__perspective-desc">Bounded contexts, aggregates, and building blocks that name and protect the business model.</span></div>' +
    '</div>';

  var EXECUTABLE_LEAD_HTML =
    '<ul class="foundry-guide__bullets">' +
    '<li>Your code is the primary source of truth for how things actually work — linking, versioning, reviews, and auditing come for free.</li>' +
    '<li>Structure context into executable, machine-executable specification that tests the actual solution.</li>' +
    '<li>Write code so that it is a direct expression of the design — easily transformed to docs and back.</li>' +
    '</ul>';

  var EXECUTABLE_UNDER_HTML =
    '<div class="foundry-tour-spec-box__title">What &ldquo;executable&rdquo; means in specification</div>' +
    '<div class="foundry-tour-spec-box__rows">' +
    '<div class="foundry-tour-spec-box__row foundry-tour-spec-box__row--sdd"><span class="foundry-tour-spec-box__name">Stories</span><span class="foundry-tour-spec-box__desc">Executable scenario-specifications with real-world examples</span></div>' +
    '<div class="foundry-tour-spec-box__row foundry-tour-spec-box__row--arc"><span class="foundry-tour-spec-box__name">Clean Engineering</span><span class="foundry-tour-spec-box__desc">Deep modules with explicit, narrow seams and type-safe contracts</span></div>' +
    '<div class="foundry-tour-spec-box__row foundry-tour-spec-box__row--uxd"><span class="foundry-tour-spec-box__name">User Experience</span><span class="foundry-tour-spec-box__desc">Interface mockups that work according to story specs and design templates</span></div>' +
    '<div class="foundry-tour-spec-box__row foundry-tour-spec-box__row--bdd"><span class="foundry-tour-spec-box__name">BDD</span><span class="foundry-tour-spec-box__desc">Nested describe/it behaviour specs that pass</span></div>' +
    '<div class="foundry-tour-spec-box__row foundry-tour-spec-box__row--ddd"><span class="foundry-tour-spec-box__name">DDD</span><span class="foundry-tour-spec-box__desc">Templates that generate domain building blocks for the target architecture</span></div>' +
    '</div>';

  var EXECUTABLE_SLIDE_HTML = EXECUTABLE_LEAD_HTML;

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

  var PAUSE_BEFORE_STEP_MS = 320;
  var PAUSE_BEFORE_RING_MS = 480;
  var TEXT_EXPAND_MS = 320;
  var TEXT_APPEAR_MS = 320;
  var STEP_FADE_MS = 320;

  var PERSPECTIVE_BY_KEY = {
    sdd: 'A shared map of the product: actors, systems, and the interactions that deliver the solution.',
    arc: 'Object design from modules through contracts to production code — structure AI can generate and verify.',
    uxd: 'How users navigate and act on the solution — information architecture, screens, and interface.',
    bdd: 'Domain vocabulary turned into hierarchical, passing behaviour tests.',
    ddd: 'Bounded contexts, aggregates, and building blocks that name and protect the business model.'
  };

  var PERSPECTIVE_TAG_BY_KEY = {
    sdd: 'Stories',
    arc: 'Clean Engineering',
    uxd: 'User Experience',
    bdd: 'Behavior-Driven Development',
    ddd: 'Domain-Driven Design'
  };

  var surface = document.querySelector('.foundry-kanban-surface');
  var ring = document.getElementById('travel-ring');
  var guidePanel = document.getElementById('foundry-guide');
  var toggleBtn = document.getElementById('cdd-toggle');
  var guideTag = document.getElementById('guide-tag');
  var guideText = document.getElementById('guide-text');
  var IDLE_HINT = 'to advance';

  function setGuideHint(text, withArrow) {
    if (!guideTag) return;
    var label = text || IDLE_HINT;
    if (withArrow) {
      guideTag.innerHTML = label + ' <span class="foundry-cdd-panel__arrow">→</span>';
    } else {
      guideTag.textContent = label;
    }
  }
  var colHeads = Array.prototype.slice.call(document.querySelectorAll('.kb-col-head'));
  var rowLabels = Array.prototype.slice.call(
    document.querySelectorAll('.foundry-perspective-label')
  ).filter(function (el) {
    return el.getAttribute('data-perspective') !== 'cdd';
  });

  var mode = 'idle';
  var activeColIndex = 0;
  var selectedPerspective = 'sdd';
  var currentRunId = 0;
  var lastRingRect = null;
  var lastRingTargets = null;
  var lastRingPad = 5;
  var tourBusy = false;

  var specCol = document.querySelector('.kb-col[data-stage="spec"]')
    || document.querySelector('.kb-col[data-stage="specification"]');
  var perspectiveCol = document.querySelector('.foundry-practice-col');
  var advanceBtn = document.getElementById('tour-advance');

  if (!surface || !ring || !toggleBtn || !guidePanel) return;

  var cddBoard = surface.classList.contains('foundry-kanban-surface--cdd-always-expanded');
  var isSkillPage = surface.classList.contains('foundry-kanban-surface--skill-page');

  function setTourBoardState(state) {
    surface.classList.remove(
      'is-tour-blank',
      'is-tour-stages',
      'is-tour-practices',
      'is-tour-practices-shown',
      'is-tour-fidelities-shown',
      'is-tour-spec-focus',
      'is-tour-details-open'
    );
    if (state === 'blank') surface.classList.add('is-tour-blank');
    else if (state === 'stages') surface.classList.add('is-tour-stages');
    else if (state === 'practices') surface.classList.add('is-tour-practices');
    else if (state === 'practices-shown') {
      surface.classList.add('is-tour-practices', 'is-tour-practices-shown');
    }
    else if (state === 'spec-focus') {
      surface.classList.add(
        'is-tour-practices',
        'is-tour-practices-shown',
        'is-tour-spec-focus'
      );
    }
    else if (state === 'full') {
      surface.classList.add(
        'is-tour-practices',
        'is-tour-practices-shown',
        'is-tour-fidelities-shown'
      );
    }
  }

  function scrollTourToFold() {
    var board = document.querySelector('.foundry-board-grid') || document.getElementById('board');
    var target = guidePanel || board;
    if (!target) return Promise.resolve();
    var nav = document.querySelector('.site-nav');
    var navH = nav ? nav.getBoundingClientRect().height : 0;
    var pad = 16;
    var y = target.getBoundingClientRect().top + window.pageYOffset - (navH + pad);
    window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    return pause(320);
  }

  function openStageDetails() {
    surface.classList.add('is-tour-details-open');
    return pause(450);
  }

  function collapseStageDetails() {
    var details = surface.querySelectorAll('.tour-stage-detail');
    details.forEach(function (el) { el.classList.add('is-collapsing'); });
    surface.classList.remove('is-tour-details-open');
    return pause(400).then(function () {
      details.forEach(function (el) { el.classList.remove('is-collapsing'); });
    });
  }

  setTourBoardState('blank');

  function initFoundryTooltips() {
    var activeTip = null;
    var activeHolder = null;
    var hideTimer = null;
    var SKILL_TIP_SHOW_DELAY_MS = 260;
    var TIP_HIDE_MS = 140;
    var HEADER_TIP_SHOW_DELAY_MS = 260;

    function positionTip(trigger, tip) {
      var r = trigger.getBoundingClientRect();
      tip.style.left = Math.max(8, r.left) + 'px';
      tip.style.top = r.bottom + 8 + 'px';
    }

    function finalizeHide(tip, holder) {
      tip.classList.remove('is-floating', 'is-visible');
      tip.style.left = '';
      tip.style.top = '';
      holder.appendChild(tip);
    }

    function hideTip(immediate) {
      if (hideTimer) {
        window.clearTimeout(hideTimer);
        hideTimer = null;
      }
      if (!activeTip || !activeHolder) return;
      var tip = activeTip;
      var holder = activeHolder;
      activeTip = null;
      activeHolder = null;
      tip.classList.remove('is-visible');
      if (immediate) {
        finalizeHide(tip, holder);
        return;
      }
      hideTimer = window.setTimeout(function () {
        hideTimer = null;
        finalizeHide(tip, holder);
      }, TIP_HIDE_MS);
    }

    function showTip(trigger, holder) {
      if (hideTimer) {
        window.clearTimeout(hideTimer);
        hideTimer = null;
      }
      var tip = holder && holder.querySelector('.kb-col-shape-tooltip');
      if (!tip || !holder) return;
      if (activeTip === tip) {
        positionTip(trigger, tip);
        return;
      }
      if (activeTip && activeHolder) {
        finalizeHide(activeTip, activeHolder);
      }
      tip.classList.add('is-floating');
      document.body.appendChild(tip);
      positionTip(trigger, tip);
      void tip.offsetWidth;
      tip.classList.add('is-visible');
      activeTip = tip;
      activeHolder = holder;
    }

    function bindInstantTriggers(triggers, holderSelector) {
      triggers.forEach(function (trigger) {
        trigger.addEventListener('mouseenter', function () {
          showTip(trigger, trigger.querySelector(holderSelector));
        });
        trigger.addEventListener('mouseleave', function () {
          hideTip(false);
        });
      });
    }

    function bindDelayedSkillTriggers(triggers) {
      triggers.forEach(function (trigger) {
        var showTimer = null;
        trigger.addEventListener('mouseenter', function () {
          var holder = trigger.querySelector('.kb-skill-tooltip-wrap');
          showTimer = window.setTimeout(function () {
            showTimer = null;
            showTip(trigger, holder);
          }, SKILL_TIP_SHOW_DELAY_MS);
        });
        trigger.addEventListener('mouseleave', function () {
          if (showTimer) {
            window.clearTimeout(showTimer);
            showTimer = null;
          }
          hideTip(false);
        });
      });
    }

    function bindDelayedHeaderTriggers(triggers) {
      triggers.forEach(function (trigger) {
        var showTimer = null;
        trigger.addEventListener('mouseenter', function () {
          var holder = trigger.querySelector('.kb-col-scope-shape-wrap');
          showTimer = window.setTimeout(function () {
            showTimer = null;
            showTip(trigger, holder);
          }, HEADER_TIP_SHOW_DELAY_MS);
        });
        trigger.addEventListener('mouseleave', function () {
          if (showTimer) {
            window.clearTimeout(showTimer);
            showTimer = null;
          }
          hideTip(false);
        });
      });
    }

    bindDelayedHeaderTriggers(surface.querySelectorAll('.kb-col-head'));
    bindDelayedSkillTriggers(
      surface.querySelectorAll('.kb-ticket.aad-skill.has-skill-tooltip')
    );

    window.addEventListener('scroll', function () {
      hideTip(true);
    }, true);
    window.addEventListener('resize', function () {
      hideTip(true);
    });
  }

  initFoundryTooltips();

  function rectInSurface(el) {
    var er = el.getBoundingClientRect();
    var sr = surface.getBoundingClientRect();
    return {
      top: er.top - sr.top + surface.scrollTop,
      left: er.left - sr.left + surface.scrollLeft,
      width: er.width,
      height: er.height
    };
  }

  function ringIsAnimating() {
    if (!ring.getAnimations) return false;
    return ring.getAnimations().some(function (a) {
      return a.playState === 'running' || a.playState === 'pending';
    });
  }

  function clearLanded() {
    Array.prototype.forEach.call(
      document.querySelectorAll('.is-ring-landed'),
      function (el) { el.classList.remove('is-ring-landed'); }
    );
  }

  function hideRing() {
    cancelRingAnimations();
    ring.classList.remove('is-visible');
    ring.style.opacity = '0';
  }

  function prepareRingFlight(fromRect) {
    cancelRingAnimations();
    ring.classList.remove('is-visible');
    ring.style.opacity = '0';
    if (fromRect) placeRing(fromRect);
  }

  function placeRing(r) {
    ring.style.top = r.top + 'px';
    ring.style.left = r.left + 'px';
    ring.style.width = r.width + 'px';
    ring.style.height = r.height + 'px';
  }

  function unionRect(elements, pad) {
    pad = pad != null ? pad : 4;
    var top = Infinity;
    var left = Infinity;
    var right = -Infinity;
    var bottom = -Infinity;
    elements.forEach(function (el) {
      var r = rectInSurface(el);
      top = Math.min(top, r.top);
      left = Math.min(left, r.left);
      right = Math.max(right, r.left + r.width);
      bottom = Math.max(bottom, r.top + r.height);
    });
    return {
      top: top - pad,
      left: left - pad,
      width: right - left + pad * 2,
      height: bottom - top + pad * 2
    };
  }

  function getRingRect() {
    if (lastRingRect) return lastRingRect;
    return {
      top: parseFloat(ring.style.top) || 0,
      left: parseFloat(ring.style.left) || 0,
      width: parseFloat(ring.style.width) || 0,
      height: parseFloat(ring.style.height) || 0
    };
  }

  function rememberRingTargets(elements, pad) {
    lastRingTargets = elements && elements.length ? elements.slice() : null;
    lastRingPad = pad != null ? pad : 5;
  }

  function ringOriginFromButton() {
    var fromRaw = rectInSurface(toggleBtn);
    var pad = 3;
    return {
      top: fromRaw.top - pad,
      left: fromRaw.left - pad,
      width: fromRaw.width + pad * 2,
      height: fromRaw.height + pad * 2
    };
  }

  function pause(ms) {
    return new Promise(function (resolve) {
      window.setTimeout(resolve, ms);
    });
  }

  function waitForTransition(el, prop, fallbackMs) {
    return new Promise(function (resolve) {
      var settled = false;
      function finish() {
        if (settled) return;
        settled = true;
        el.removeEventListener('transitionend', onEnd);
        resolve();
      }
      function onEnd(e) {
        if (e.target === el && e.propertyName === prop) finish();
      }
      el.addEventListener('transitionend', onEnd);
      window.setTimeout(finish, fallbackMs);
    });
  }

  function waitForLayoutAfterExpand() {
    return waitForTransition(guideText, 'max-height', TEXT_EXPAND_MS).then(function () {
      return new Promise(function (resolve) {
        window.requestAnimationFrame(function () {
          window.requestAnimationFrame(resolve);
        });
      });
    });
  }

  function waitForTextAppear() {
    return waitForTransition(guideText, 'opacity', TEXT_APPEAR_MS);
  }

  function flyRingToTargets(fromRect, elements, pad, opts) {
    hideRing();
    return Promise.resolve();
  }

  function syncRingToTargets() {
    hideRing();
  }

  function focusStages(elements) {
    var board = document.querySelector('.foundry-board-grid') || document.getElementById('board');
    if (board) board.classList.add('is-tour-stages-focus');
    var els = elements && elements.length ? elements : colHeads;
    var target = els[0] || board;
    if (!target || typeof target.scrollIntoView !== 'function') return Promise.resolve();
    target.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });
    return pause(220);
  }

  function clearStagesFocus() {
    var board = document.querySelector('.foundry-board-grid') || document.getElementById('board');
    if (board) board.classList.remove('is-tour-stages-focus');
  }

  function ensurePerspectiveOverlay() {
    var board = document.querySelector('.foundry-board-grid') || document.getElementById('board');
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

  function specColumnHead() {
    return document.querySelector('.kb-col[data-stage="spec"] > .kb-col-head')
      || document.querySelector('.kb-col[data-stage="specification"] > .kb-col-head');
  }

  function clearSpecHeaderAlign() {
    var head = specColumnHead();
    if (!head) return;
    head.style.position = '';
    head.style.left = '';
    head.style.width = '';
    head.style.height = '';
    head.style.top = '';
    head.style.zIndex = '';
    head.style.margin = '';
  }

  function lineUpSpecHeader() {
    clearSpecHeaderAlign();
    var board = document.querySelector('.foundry-board-grid') || document.getElementById('board');
    var head = specColumnHead();
    var practiceCol = document.querySelector('.foundry-practice-col');
    if (!board || !head || !practiceCol) return;
    head.offsetHeight;
    var anchor = practiceCol.querySelector('[data-perspective]');
    var boardRect = board.getBoundingClientRect();
    var anchorRight = anchor ? anchor.getBoundingClientRect().right : practiceCol.getBoundingClientRect().right;
    var left = Math.round(anchorRight - boardRect.left);
    var width = Math.max(80, Math.round(boardRect.right - anchorRight - 6));
    var colRect = head.parentElement.getBoundingClientRect();
    var headRect = head.getBoundingClientRect();
    head.style.position = 'absolute';
    head.style.boxSizing = 'border-box';
    head.style.zIndex = '3';
    head.style.margin = '0';
    head.style.top = Math.round(headRect.top - colRect.top) + 'px';
    head.style.height = Math.round(headRect.height) + 'px';
    head.style.left = Math.round((boardRect.left + left) - colRect.left) + 'px';
    head.style.width = width + 'px';
  }

  function hidePerspectiveOverlay() {
    clearSpecHeaderAlign();
    var board = document.querySelector('.foundry-board-grid') || document.getElementById('board');
    var overlay = document.getElementById('board-perspective-overlay');
    if (board) board.classList.remove('has-perspective-overlay');
    if (overlay) {
      overlay.classList.remove('is-visible');
      overlay.innerHTML = '';
    }
  }

  function ensureSpecUnderBox() {
    return null;
  }

  function showSpecUnderBox() {
    /* Spec copy lives in the phase-description cells, not a separate under-box. */
  }

  function hideSpecUnderBox() {
    var box = document.getElementById('tour-spec-box');
    if (!box) return;
    box.classList.remove('is-visible');
    box.setAttribute('aria-hidden', 'true');
    box.innerHTML = '';
  }

  var stageQuestionsOriginal = null;

  var stageDetailOriginal = {};

  function fillSpecPhaseDescriptions() {
    var specDetail = document.querySelector('.tour-stage-detail[data-stage-detail="spec"]');
    if (specDetail) {
      if (!stageDetailOriginal.spec) stageDetailOriginal.spec = specDetail.innerHTML;
      specDetail.innerHTML = EXECUTABLE_UNDER_HTML;
    }
    var root = document.querySelector('.kanban-stage-questions');
    if (!root) return;
    if (stageQuestionsOriginal == null) stageQuestionsOriginal = root.innerHTML;
    var specCell = root.querySelector('.kanban-stage-questions__cell[data-stage="spec"]');
    if (specCell) specCell.innerHTML = EXECUTABLE_UNDER_HTML;
  }

  function restorePhaseDescriptions() {
    var specDetail = document.querySelector('.tour-stage-detail[data-stage-detail="spec"]');
    if (specDetail && stageDetailOriginal.spec) {
      specDetail.innerHTML = stageDetailOriginal.spec;
    }
    var root = document.querySelector('.kanban-stage-questions');
    if (!root || stageQuestionsOriginal == null) return;
    root.innerHTML = stageQuestionsOriginal;
  }

  function setCollapsedSideColumns(collapsed) {
    var board = document.querySelector('.foundry-board-grid') || document.getElementById('board');
    if (!board) return;
    ['discovery', 'engineer'].forEach(function (stage) {
      board.querySelectorAll(':scope > .kb-col[data-stage="' + stage + '"]').forEach(function (col) {
        col.classList.toggle('kb-col--collapsed', collapsed);
      });
    });
    if (collapsed) {
      board.classList.add('is-tour-spec-cols');
    } else {
      board.classList.remove('is-tour-spec-cols');
      clearSpecHeaderAlign();
    }
  }

  var SPEC_CELL_TEXT = {
    sdd: 'Executable scenario-specifications with real-world examples',
    arc: 'Deep modules with explicit, narrow seams and type-safe contracts',
    uxd: 'Interface mockups that work according to story specs and design templates',
    bdd: 'Nested describe/it behaviour specs that pass',
    ddd: 'Templates that generate domain building blocks for the target architecture'
  };

  function showAlignedCells(texts) {
    var board = document.querySelector('.foundry-board-grid') || document.getElementById('board');
    var practiceCol = document.querySelector('.foundry-practice-col');
    var overlay = ensurePerspectiveOverlay();
    if (!board || !practiceCol || !overlay) return Promise.resolve();
    board.offsetHeight;
    var boardRect = board.getBoundingClientRect();
    var anchor = practiceCol.querySelector('[data-perspective]');
    var anchorRight = anchor ? anchor.getBoundingClientRect().right : practiceCol.getBoundingClientRect().right;
    var left = Math.round(anchorRight - boardRect.left);
    var width = Math.max(80, Math.round(boardRect.right - anchorRight - 6));
    overlay.innerHTML = '';
    PERSPECTIVE_ORDER.forEach(function (key) {
      var label = practiceCol.querySelector('[data-perspective="' + key + '"]');
      var desc = texts[key];
      if (!label || !desc) return;
      var r = label.getBoundingClientRect();
      var row = document.createElement('div');
      row.className = 'foundry-board-overlay__row is-shown';
      row.style.top = Math.round(r.top - boardRect.top) + 'px';
      row.style.height = Math.round(r.height) + 'px';
      row.style.left = left + 'px';
      row.style.width = width + 'px';
      row.innerHTML = '<span class="foundry-board-overlay__desc">' + desc + '</span>';
      overlay.appendChild(row);
    });
    board.classList.add('has-perspective-overlay');
    overlay.classList.add('is-visible');
    return Promise.resolve();
  }

  function placeEmptyColumnHead() {
    var board = document.querySelector('.foundry-board-grid') || document.getElementById('board');
    var practiceCol = document.querySelector('.foundry-practice-col');
    var overlay = document.getElementById('board-perspective-overlay');
    var practiceHead = practiceCol && practiceCol.querySelector('.foundry-practice-col__cdd-head');
    if (!board || !practiceCol || !overlay || !practiceHead) return;
    var boardRect = board.getBoundingClientRect();
    var anchor = practiceCol.querySelector('[data-perspective]');
    var anchorRight = anchor ? anchor.getBoundingClientRect().right : practiceCol.getBoundingClientRect().right;
    var headRect = practiceHead.getBoundingClientRect();
    var head = document.createElement('div');
    head.className = 'foundry-board-overlay__head';
    head.style.top = Math.round(headRect.top - boardRect.top) + 'px';
    head.style.height = Math.round(headRect.height) + 'px';
    head.style.left = Math.round(anchorRight - boardRect.left) + 'px';
    head.style.width = Math.max(80, Math.round(boardRect.right - anchorRight - 6)) + 'px';
    overlay.appendChild(head);
  }

  function showPerspectiveOverlay() {
    return showAlignedCells(PERSPECTIVE_BY_KEY).then(function () {
      placeEmptyColumnHead();
    });
  }

  function showSpecCells() {
    return showAlignedCells(SPEC_CELL_TEXT).then(function () {
      lineUpSpecHeader();
    });
  }

  function flyRingRect(fromRect, toRect, opts) {
    opts = opts || {};
    var runId = opts.runId;
    var duration = opts.duration || 360;
    var hold = opts.hold || 80;

    prepareRingFlight(fromRect);
    clearLanded();
    void ring.offsetWidth;
    ring.classList.add('is-visible');
    ring.style.opacity = '1';

    var anim = ring.animate(
      [
        { top: fromRect.top + 'px', left: fromRect.left + 'px', width: fromRect.width + 'px', height: fromRect.height + 'px', opacity: 1 },
        { top: toRect.top + 'px', left: toRect.left + 'px', width: toRect.width + 'px', height: toRect.height + 'px', opacity: 1 }
      ],
      { duration: duration, easing: 'cubic-bezier(0.4, 0, 0.2, 1)', fill: 'forwards' }
    );

    return anim.finished.then(function () {
      if (runId != null && runId !== currentRunId) return;
      placeRing(toRect);
      lastRingRect = toRect;
      if (opts.targets) rememberRingTargets(opts.targets, opts.pad);
      return new Promise(function (resolve) {
        window.setTimeout(resolve, hold);
      });
    }).catch(function () {});
  }

  function cancelRingAnimations() {
    if (ring.getAnimations) {
      ring.getAnimations().forEach(function (a) { a.cancel(); });
    }
  }

  function flyRing(fromEl, toEl, opts) {
    opts = opts || {};
    var runId = opts.runId;
    var duration = opts.duration || 320;
    var hold = opts.hold || 120;
    var pad = opts.pad != null ? opts.pad : 3;

    var from = rectInSurface(fromEl);
    var toRaw = rectInSurface(toEl);
    var to = {
      top: toRaw.top - pad,
      left: toRaw.left - pad,
      width: toRaw.width + pad * 2,
      height: toRaw.height + pad * 2
    };

    prepareRingFlight(from);
    clearLanded();
    void ring.offsetWidth;
    ring.classList.add('is-visible');
    ring.style.opacity = '1';

    var anim = ring.animate(
      [
        { top: from.top + 'px', left: from.left + 'px', width: from.width + 'px', height: from.height + 'px', opacity: 1 },
        { top: to.top + 'px', left: to.left + 'px', width: to.width + 'px', height: to.height + 'px', opacity: 1 }
      ],
      { duration: duration, easing: 'cubic-bezier(0.4, 0, 0.2, 1)', fill: 'forwards' }
    );

    return anim.finished.then(function () {
      if (runId != null && runId !== currentRunId) return;
      placeRing(to);
      lastRingRect = to;
      if (opts.landTarget !== false && toEl.classList) {
        toEl.classList.add('is-ring-landed');
      }
      return new Promise(function (resolve) {
        window.setTimeout(resolve, hold);
      });
    }).catch(function () {});
  }

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

    return chain.then(function () {
      if (runId === currentRunId) tourBusy = false;
    }).catch(function () {
      if (runId === currentRunId) tourBusy = false;
    });
  }

  function bumpRun() {
    currentRunId++;
    cancelRingAnimations();
    hideRing();
    lastRingRect = null;
    lastRingTargets = null;
    tourBusy = false;
  }

  function hideGuideText() {
    guideText.classList.remove('is-expanding', 'is-revealed', 'is-tall');
    guideText.innerHTML = '';
  }

  function fadeOutGuideText() {
    if (!guideText.classList.contains('is-revealed') && !guideText.innerHTML) {
      guideText.classList.remove('is-expanding', 'is-tall');
      guideText.innerHTML = '';
      return Promise.resolve();
    }
    guideText.classList.remove('is-revealed');
    return pause(STEP_FADE_MS).then(function () {
      guideText.classList.remove('is-expanding', 'is-tall');
      guideText.innerHTML = '';
    });
  }

  function fadeOutBoardContent() {
    surface.classList.add('is-tour-fading-out');
    return pause(STEP_FADE_MS);
  }

  function fadeOutTogether() {
    surface.classList.add('is-tour-fading-out');
    if (guideText.classList.contains('is-revealed') || guideText.innerHTML) {
      guideText.classList.remove('is-revealed');
    }
    return pause(STEP_FADE_MS).then(function () {
      guideText.classList.remove('is-tall');
      guideText.innerHTML = '';
    });
  }

  function fitGuideBox() {
    if (!guideText) return;
    var width = guideText.getBoundingClientRect().width;
    if (!width) return;
    var samples = [SCOPE_SLIDE_HTML, PERSPECTIVES_LEAD_HTML, EXECUTABLE_LEAD_HTML];
    var probe = document.createElement('div');
    probe.style.cssText = 'position:absolute;left:-9999px;top:0;visibility:hidden;height:auto;';
    probe.style.width = width + 'px';
    document.body.appendChild(probe);
    var max = 0;
    samples.forEach(function (html) {
      probe.innerHTML = html;
      max = Math.max(max, probe.offsetHeight);
    });
    probe.remove();
    if (!max) return;
    if (guidePanel) guidePanel.style.setProperty('--guide-slide-h', max + 'px');
    guideText.style.height = max + 'px';
    guideText.style.maxHeight = max + 'px';
  }

  function fadeInTogether(tag, html, opts) {
    opts = opts || {};
    guidePanel.classList.add('is-tour-active');
    guideTag.classList.remove('is-waiting');
    setGuideHint(IDLE_HINT, false);
    guideText.classList.remove('is-revealed', 'is-tall');
    guideText.innerHTML = html;
    if (opts.tall) guideText.classList.add('is-tall');
    if (opts.openDetails) surface.classList.add('is-tour-details-open');
    fitGuideBox();
    /* Same frame: expand guide box, reveal text, and show board content. */
    return new Promise(function (resolve) {
      window.requestAnimationFrame(function () {
        guideText.classList.add('is-expanding', 'is-revealed');
        surface.classList.remove('is-tour-fading-out');
        resolve();
      });
    }).then(function () {
      return pause(STEP_FADE_MS);
    });
  }

  /** Fade out text+chips together, swap board, fade in text+grid together. */
  function transitionTourStep(runId, opts) {
    return fadeOutTogether().then(function () {
      if (runId !== currentRunId) return;
      if (typeof opts.applyBoard === 'function') opts.applyBoard();
      /* Keep new content invisible until the shared fade-in. */
      surface.classList.add('is-tour-fading-out');
      if (opts.openDetails) surface.classList.add('is-tour-details-open');
      return new Promise(function (resolve) {
        window.requestAnimationFrame(function () {
          window.requestAnimationFrame(resolve);
        });
      });
    }).then(function () {
      if (runId !== currentRunId) return;
      return fadeInTogether(opts.tag, opts.html, {
        tall: opts.tall,
        openDetails: opts.openDetails
      });
    }).then(function () {
      if (runId !== currentRunId) return;
      setGuideHint(IDLE_HINT, false);
    });
  }

  function waitForLayoutAfterCollapse() {
    return new Promise(function (resolve) {
      window.setTimeout(function () {
        window.requestAnimationFrame(function () {
          window.requestAnimationFrame(resolve);
        });
      }, 620);
    });
  }

  function setGuideWaiting() {
    cancelRingAnimations();
    hideRing();
    lastRingRect = null;
    lastRingTargets = null;
    guidePanel.classList.add('is-tour-active');
    guideTag.classList.remove('is-waiting');
    setGuideHint(IDLE_HINT, false);
  }

  /** Pause → expand box → text fades in → pause → caller flies orange ring. */
  function revealGuideText(tag, html, opts) {
    opts = opts || {};
    guidePanel.classList.add('is-tour-active');
    guideText.classList.remove('is-expanding', 'is-revealed', 'is-tall');
    guideText.innerHTML = html;

    var chain = opts.skipInitialPause ? Promise.resolve() : pause(PAUSE_BEFORE_STEP_MS);

    return chain
      .then(function () {
        guideTag.classList.remove('is-waiting');
        setGuideHint(IDLE_HINT, false);
        return new Promise(function (resolve) {
          window.requestAnimationFrame(function () {
            if (opts.tall) guideText.classList.add('is-tall');
            guideText.classList.add('is-expanding');
            resolve();
          });
        });
      })
      .then(function () { return waitForLayoutAfterExpand(); })
      .then(function () {
        return new Promise(function (resolve) {
          window.requestAnimationFrame(function () {
            guideText.classList.add('is-revealed');
            resolve();
          });
        });
      })
      .then(function () { return waitForTextAppear(); })
      .then(function () {
        return opts.skipRingPause ? Promise.resolve() : pause(PAUSE_BEFORE_RING_MS);
      });
  }

  function setTourButtonLabel(label) {
    if (!toggleBtn) return;
    toggleBtn.textContent = label;
  }

  function resetTour() {
    bumpRun();
    hideRing();
    clearLanded();
    clearStagesFocus();
    hidePerspectiveOverlay();
    hideSpecUnderBox();
    setCollapsedSideColumns(false);
    surface.classList.remove('is-tour-fading-out');
    lastRingRect = null;
    lastRingTargets = null;
    toggleBtn.classList.remove('is-active');
    guidePanel.classList.remove('is-tour-active');
    mode = 'idle';
    guideTag.classList.remove('is-waiting');
    setGuideHint(IDLE_HINT, false);
    setTourButtonLabel('Start tour');
    hideGuideText();
    hidePerspectiveOverlay();
    setTourBoardState('blank');
    restorePhaseDescriptions();
    if (typeof window.__foundrySetSkillsExpanded === 'function' && !cddBoard) {
      window.__foundrySetSkillsExpanded(false);
    }
  }

  /** Step 1: Iterate and Learn — scroll, then text + stage details fade in together. */
  function animateScopeTour() {
    clearLanded();
    hideRing();
    hidePerspectiveOverlay();
    hideSpecUnderBox();
    setCollapsedSideColumns(false);
    restorePhaseDescriptions();
    lastRingRect = null;
    lastRingTargets = null;
    toggleBtn.classList.add('is-active');
    setTourButtonLabel('Iterate and Learn');
    mode = 'scope';
    guidePanel.classList.add('is-tour-active');
    setGuideHint(IDLE_HINT, false);
    guideTag.classList.add('is-waiting');

    return runTour([
      function (runId) {
        return scrollTourToFold().then(function () {
          if (runId !== currentRunId) return;
          return transitionTourStep(runId, {
            tag: 'Iterate and Learn',
            html: SCOPE_SLIDE_HTML,
            openDetails: true,
            applyBoard: function () {
              setTourBoardState('stages');
            }
          });
        });
      }
    ]);
  }

  /** Step 2: Product Engineering — practices + descriptions. */
  function animatePerspectiveTour() {
    clearLanded();
    hideRing();
    lastRingRect = null;
    lastRingTargets = null;
    mode = 'perspective';
    setTourButtonLabel('Product Engineering');
    setGuideWaiting();
    hideSpecUnderBox();
    setCollapsedSideColumns(false);
    if (typeof window.__foundrySetSkillsExpanded === 'function') window.__foundrySetSkillsExpanded(true);

    return runTour([
      function (runId) {
        return scrollTourToFold().then(function () {
          if (runId !== currentRunId) return;
          return transitionTourStep(runId, {
            tag: 'Product Engineering',
            html: PERSPECTIVES_LEAD_HTML,
            applyBoard: function () {
              setTourBoardState('practices');
              surface.classList.add('is-tour-practices-shown');
              showPerspectiveOverlay(null, { stagger: false });
            }
          });
        });
      }
    ]);
  }

  /** Step 3: Code Is Context — spec focus. */
  function animateSpecColumn() {
    clearLanded();
    hideSpecUnderBox();
    hideRing();
    mode = 'column';
    activeColIndex = 3;
    setTourButtonLabel('Code Is Context');
    setGuideWaiting();

    return runTour([
      function (runId) {
        return transitionTourStep(runId, {
          tag: 'Code Is Context',
          html: EXECUTABLE_LEAD_HTML,
          applyBoard: function () {
            setTourBoardState('spec-focus');
            setCollapsedSideColumns(true);
            showSpecCells();
          }
        });
      }
    ]);
  }

  /** Step 4: text + all fidelities fade together. */
  function animateShowPractices() {
    clearLanded();
    hidePerspectiveOverlay();
    hideSpecUnderBox();
    hideRing();
    mode = 'fidelities';
    setTourButtonLabel('Practice fidelities');
    setGuideWaiting();

    return runTour([
      function (runId) {
        return transitionTourStep(runId, {
          tag: 'Context Storming',
          html: '<ul class="foundry-guide__bullets"><li>Define and connect context across product, engineering, and operations. Bring those artifacts into one knowledge graph, in place of scattered docs, tickets, and tribal memory.</li><li>Collaboratively build artifacts at the right level of abstraction to support the right level of decision making.</li></ul>',
          applyBoard: function () {
            restorePhaseDescriptions();
            setCollapsedSideColumns(false);
            setTourBoardState('full');
          }
        });
      }
    ]);
  }

  /** Step 5: change implications — final panel. */
  function animateChangeImplications() {
    clearLanded();
    hidePerspectiveOverlay();
    hideSpecUnderBox();
    hideRing();
    lastRingRect = null;
    lastRingTargets = null;
    mode = 'change';
    setGuideWaiting();

    return runTour([
      function (runId) {
        return transitionTourStep(runId, {
          tag: 'Change implications',
          html: CHANGE_SLIDE_HTML,
          tall: true,
          applyBoard: function () {
            setCollapsedSideColumns(false);
            setTourBoardState('full');
          }
        });
      }
    ]);
  }

  function advanceMode() {
    if (tourBusy) return;
    if (mode === 'idle') {
      animatePerspectiveTour();
      return;
    }
    if (mode === 'perspective') {
      animateSpecColumn();
      return;
    }
    if (mode === 'column') {
      animateScopeTour();
      return;
    }
    if (mode === 'scope') {
      animateShowPractices();
      return;
    }
    if (mode === 'fidelities') {
      animateChangeImplications();
      return;
    }
    if (mode === 'change') {
      resetTour();
    }
  }

  function retreatMode() {
    if (tourBusy) return;
    if (mode === 'idle') return;
    if (mode === 'perspective') {
      resetTour();
      return;
    }
    if (mode === 'column') {
      setCollapsedSideColumns(false);
      animatePerspectiveTour();
      return;
    }
    if (mode === 'scope') {
      hidePerspectiveOverlay();
      animateSpecColumn();
      return;
    }
    if (mode === 'fidelities') {
      animateScopeTour();
      return;
    }
    if (mode === 'change') {
      animateShowPractices();
    }
  }

  toggleBtn.addEventListener('click', function () {
    if (mode === 'idle') advanceMode();
    else resetTour();
  });

  if (advanceBtn) {
    advanceBtn.addEventListener('click', function () {
      advanceMode();
    });
  }

  rowLabels.forEach(function (label) {
    label.addEventListener('click', function (e) {
      if (mode !== 'perspective' && mode !== 'column') return;
      var key = label.getAttribute('data-perspective');
      if (!key || !PERSPECTIVE_BY_KEY[key]) return;
      e.preventDefault();
      selectedPerspective = key;
      cancelRingAnimations();
      lastRingTargets = [label];
      lastRingPad = 4;
      hideRing();
      guideTag.classList.remove('is-waiting');
      if (mode === 'perspective') {
        showPerspectiveOverlay(selectedPerspective);
        setGuideHint(IDLE_HINT, false);
        syncRingToTargets();
        return;
      }
      revealGuideText(
        PERSPECTIVE_TAG_BY_KEY[selectedPerspective],
        '<p class="foundry-guide__lead">' + PERSPECTIVE_BY_KEY[selectedPerspective] + '</p>',
        { skipInitialPause: true, skipRingPause: true }
      ).then(function () {
        syncRingToTargets();
      });
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.target.closest('input, textarea, select')) return;
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      advanceMode();
      return;
    }
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      retreatMode();
    }
  });

  if (window.ResizeObserver && guidePanel) {
    new ResizeObserver(function () {
      if (mode !== 'idle') syncRingToTargets();
      if (mode === 'perspective') showPerspectiveOverlay(selectedPerspective || null);
      if (mode === 'column') showSpecCells();
    }).observe(guidePanel);
  }

  fitGuideBox();

  window.addEventListener('resize', function () {
    fitGuideBox();
    if (mode === 'perspective') showPerspectiveOverlay(selectedPerspective || null);
    if (mode === 'column') showSpecCells();
    cancelRingAnimations();
    if (mode !== 'idle' && lastRingTargets) {
      syncRingToTargets();
      return;
    }
    lastRingRect = null;
    hideRing();
  });
})();
