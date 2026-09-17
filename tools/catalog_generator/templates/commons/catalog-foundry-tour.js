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

  var PERSPECTIVES_SLIDE_HTML =
    '<p class="foundry-guide__lead">Different windows that answer different questions — integrated with minimal overlap and redundancy. Replace scattered docs, tickets, and tribal memory with <strong>one connected source</strong> — each fact lives in one place and links to the rest.</p>' +
    '<div class="foundry-guide__perspectives">' +
    '<div class="foundry-guide__perspective-row foundry-guide__perspective-row--sdd"><span class="foundry-guide__perspective-name">Stories</span><span class="foundry-guide__perspective-desc">A shared map of the product: actors, systems, and the interactions that deliver the solution.</span></div>' +
    '<div class="foundry-guide__perspective-row foundry-guide__perspective-row--arc"><span class="foundry-guide__perspective-name">Clean Engineering</span><span class="foundry-guide__perspective-desc">Object design from modules through contracts to production code — structure AI can generate and verify.</span></div>' +
    '<div class="foundry-guide__perspective-row foundry-guide__perspective-row--uxd"><span class="foundry-guide__perspective-name">User Experience</span><span class="foundry-guide__perspective-desc">How users navigate and act on the solution — information architecture, screens, and interface.</span></div>' +
    '<div class="foundry-guide__perspective-row foundry-guide__perspective-row--bdd"><span class="foundry-guide__perspective-name">Behavior-Driven Development</span><span class="foundry-guide__perspective-desc">Domain vocabulary turned into hierarchical, passing behaviour tests.</span></div>' +
    '<div class="foundry-guide__perspective-row foundry-guide__perspective-row--ddd"><span class="foundry-guide__perspective-name">Domain-Driven Design</span><span class="foundry-guide__perspective-desc">Bounded contexts, aggregates, and building blocks that name and protect the business model.</span></div>' +
    '</div>';

  var EXECUTABLE_SLIDE_HTML =
    '<p class="foundry-guide__executable">Refine context into machine-readable, behavioural specification that AI can build from.</p>' +
    '<ul class="foundry-guide__bullets">' +
    '<li>Turn knowledge and org context into an <strong>executable, machine-readable asset</strong>. <strong>Behavioural</strong> specifications, <strong>templated</strong> for consistency.</li>' +
    '<li>Favor <strong>unambiguous artifacts</strong> — tests, templates, and directions — over narrative docs. Each states behaviour clearly enough to generate from, review against, and change without rework.</li>' +
    '</ul>' +
    '<div class="foundry-guide__exe-heading">What &ldquo;executable&rdquo; means per context tool</div>' +
    '<div class="foundry-guide__executable-rows">' +
    '<div class="foundry-guide__executable-row foundry-guide__executable-row--sdd"><span class="foundry-guide__executable-name">Stories</span><span class="foundry-guide__executable-desc">Executable scenario-specifications with real-world examples</span></div>' +
    '<div class="foundry-guide__executable-row foundry-guide__executable-row--arc"><span class="foundry-guide__executable-name">Clean Engineering</span><span class="foundry-guide__executable-desc">Deep modules with explicit, narrow seams and type-safe contracts created using clean code</span></div>' +
    '<div class="foundry-guide__executable-row foundry-guide__executable-row--uxd"><span class="foundry-guide__executable-name">User Experience</span><span class="foundry-guide__executable-desc">Interface mockups that work according to both story specifications and design templates</span></div>' +
    '<div class="foundry-guide__executable-row foundry-guide__executable-row--bdd"><span class="foundry-guide__executable-name">BDD</span><span class="foundry-guide__executable-desc">Nested describe/it behaviour specs that pass</span></div>' +
    '<div class="foundry-guide__executable-row foundry-guide__executable-row--ddd"><span class="foundry-guide__executable-name">DDD</span><span class="foundry-guide__executable-desc">Templates that generate domain building blocks using the target architecture</span></div>' +
    '</div>';

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
  var TEXT_EXPAND_MS = 480;
  var TEXT_APPEAR_MS = 520;

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

  if (!surface || !ring || !toggleBtn || !guidePanel) return;

  var cddBoard = surface.classList.contains('foundry-kanban-surface--cdd-always-expanded');
  var isSkillPage = surface.classList.contains('foundry-kanban-surface--skill-page');

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
    opts = opts || {};
    var targetRect = unionRect(elements, pad);
    return flyRingRect(fromRect, targetRect, {
      runId: opts.runId,
      duration: opts.duration || 400,
      hold: opts.hold != null ? opts.hold : 100,
      targets: elements,
      pad: pad
    });
  }

  function syncRingToTargets() {
    if (!lastRingTargets || !lastRingTargets.length) return;
    if (ringIsAnimating()) return;
    var r = unionRect(lastRingTargets, lastRingPad);
    placeRing(r);
    lastRingRect = r;
    ring.classList.add('is-visible');
    ring.style.opacity = '1';
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
    guideTag.textContent = '…';
    guideTag.classList.add('is-waiting');
    hideGuideText();
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
        guideTag.textContent = tag;
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

  function resetTour() {
    bumpRun();
    hideRing();
    clearLanded();
    lastRingRect = null;
    lastRingTargets = null;
    toggleBtn.classList.remove('is-active');
    guidePanel.classList.remove('is-tour-active');
    mode = 'idle';
    guideTag.classList.remove('is-waiting');
    guideTag.textContent = 'Click for overview';
    hideGuideText();
    if (typeof window.__foundrySetSkillsExpanded === 'function' && !cddBoard) {
      window.__foundrySetSkillsExpanded(false);
    }
  }

  /** Click 1: expand copy, then ring all column headers (positions after panel growth). */
  function animateScopeTour() {
    clearLanded();
    hideRing();
    lastRingRect = null;
    lastRingTargets = null;
    toggleBtn.classList.add('is-active');
    mode = 'scope';
    guidePanel.classList.add('is-tour-active');
    guideTag.textContent = '…';
    guideTag.classList.add('is-waiting');

    return runTour([
      function (runId) {
        return revealGuideText('Context scope', SCOPE_SLIDE_HTML)
          .then(function () {
            if (runId !== currentRunId) return;
            return flyRingToTargets(ringOriginFromButton(), colHeads, 5, {
              runId: runId,
              duration: 420,
              hold: 100
            });
          });
      }
    ]);
  }

  /** Click 2: expand copy, then ring perspective labels. */
  function animatePerspectiveTour() {
    clearLanded();
    mode = 'perspective';
    setGuideWaiting();
    if (typeof window.__foundrySetSkillsExpanded === 'function') window.__foundrySetSkillsExpanded(true);

    var targets = rowLabels.length ? rowLabels : [perspectiveCol];

    return runTour([
      function (runId) {
        return waitForLayoutAfterCollapse()
          .then(function () {
            return revealGuideText(
              'Context perspectives',
              PERSPECTIVES_SLIDE_HTML,
              { skipInitialPause: true }
            );
          })
          .then(function () {
            if (runId !== currentRunId) return;
            return flyRingToTargets(ringOriginFromButton(), targets, 4, {
              runId: runId,
              duration: 400,
              hold: 120
            });
          });
      }
    ]);
  }

  /** Click 3: expand copy, then ring Specification column. */
  function animateSpecColumn() {
    clearLanded();
    mode = 'column';
    activeColIndex = 3;
    setGuideWaiting();

    return runTour([
      function (runId) {
        return waitForLayoutAfterCollapse()
          .then(function () {
            return revealGuideText(
              'Executable context',
              EXECUTABLE_SLIDE_HTML,
              { skipInitialPause: true }
            );
          })
          .then(function () {
            if (runId !== currentRunId) return;
            return flyRingToTargets(ringOriginFromButton(), [specCol], 5, {
              runId: runId,
              duration: 380,
              hold: 140
            });
          });
      }
    ]);
  }

  /** Click 4: change implications — final panel; no ring. */
  function animateChangeImplications() {
    clearLanded();
    hideRing();
    lastRingRect = null;
    lastRingTargets = null;
    mode = 'change';
    guidePanel.classList.add('is-tour-active');

    return runTour([
      function (runId) {
        return revealGuideText(
          'Change implications',
          CHANGE_SLIDE_HTML,
          { skipInitialPause: true, skipRingPause: true, tall: true }
        ).then(function () {
          if (runId !== currentRunId) return;
          hideRing();
        });
      }
    ]);
  }

  function advanceMode() {
    if (tourBusy) return;
    if (mode === 'idle') {
      animateScopeTour();
      return;
    }
    if (mode === 'scope') {
      animatePerspectiveTour();
      return;
    }
    if (mode === 'perspective') {
      animateSpecColumn();
      return;
    }
    if (mode === 'column') {
      animateChangeImplications();
      return;
    }
    if (mode === 'change') {
      resetTour();
    }
  }

  toggleBtn.addEventListener('click', function () {
    advanceMode();
  });

  rowLabels.forEach(function (label) {
    label.addEventListener('click', function (e) {
      if (mode !== 'perspective' && mode !== 'column') return;
      var key = label.getAttribute('data-perspective');
      if (!key || !PERSPECTIVE_BY_KEY[key]) return;
      e.preventDefault();
      selectedPerspective = key;
      cancelRingAnimations();
      hideRing();
      guideTag.classList.remove('is-waiting');
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
    if (e.key !== ' ' && e.key !== 'Enter' && e.key !== 'ArrowRight') return;
    if (e.target.closest('input, textarea, select')) return;
    e.preventDefault();
    advanceMode();
  });

  if (window.ResizeObserver && guidePanel) {
    new ResizeObserver(function () {
      if (mode !== 'idle') syncRingToTargets();
    }).observe(guidePanel);
  }

  window.addEventListener('resize', function () {
    cancelRingAnimations();
    if (mode !== 'idle' && lastRingTargets) {
      syncRingToTargets();
      return;
    }
    lastRingRect = null;
    hideRing();
  });
})();