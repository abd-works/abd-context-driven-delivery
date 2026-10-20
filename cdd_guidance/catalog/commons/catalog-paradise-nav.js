/**
 * Paradise-branded catalog nav — same dual-mode chrome as catalog-nav.js.
 */
(function () {
  'use strict';

  var KEY = 'paradise-mode';
  var EXECUTIVE = 'executive';
  var ENGINEERING = 'engineering';
  var SITE = 'https://paradisemobile.bm/';

  var _mode = EXECUTIVE;

  function isExternalHtmlPreview() {
    var h = location.hostname.toLowerCase();
    return h === 'htmlpreview.github.io'
      || h === 'raw.githack.com'
      || h === 'rawcdn.githack.com'
      || h === 'html-preview.github.io';
  }

  function modeFromUrl() {
    try {
      var q = new URLSearchParams(location.search);
      var m = q.get('mode') || q.get('paradise-mode');
      if (m === ENGINEERING || m === EXECUTIVE) return m;
    } catch (e) {}
    return null;
  }

  function resolveInitialMode() {
    var fromUrl = modeFromUrl();
    if (fromUrl) return fromUrl;
    if (isExternalHtmlPreview()) return ENGINEERING;
    try {
      var stored = localStorage.getItem(KEY);
      if (stored === ENGINEERING) return stored;
    } catch (e) {}
    return EXECUTIVE;
  }

  _mode = resolveInitialMode();
  document.documentElement.classList.add('paradise-brand');
  if (_mode === ENGINEERING) {
    document.documentElement.setAttribute('data-theme', ENGINEERING);
  }

  function assetBase() {
    var s = document.currentScript;
    if (s && s.src) {
      try {
        return new URL('.', s.src).href;
      } catch (e) {}
    }
    return 'commons/';
  }

  function navPrefix() {
    var body = document.body;
    if (body && body.getAttribute('data-nav-prefix') != null) {
      return body.getAttribute('data-nav-prefix') || '';
    }
    return '';
  }

  function navCurrent() {
    var body = document.body;
    return (body && body.getAttribute('data-nav-current')) || '';
  }

  function logoSrc() {
    return assetBase() + 'brand/paradise-logo.svg';
  }

  function catalogLinks() {
    var p = navPrefix();
    return [
      { id: 'hub', label: 'catalog', href: p + 'paradise.html' },
      { id: 'workflow', label: 'workflow', href: p + 'paradise-workflow.html' }
    ];
  }

  function linkHTML(links, currentPage) {
    return links.map(function (l) {
      var isCurrent = l.id === currentPage;
      return '<li><a href="' + l.href + '"' +
        (isCurrent ? ' aria-current="page"' : '') +
        '>' + l.label + '</a></li>';
    }).join('');
  }

  function inject() {
    var currentPage = navCurrent();
    var links = catalogLinks();
    var linksHTML = linkHTML(links, currentPage);

    var nav = document.createElement('nav');
    nav.className = 'site-nav';
    nav.setAttribute('aria-label', 'Paradise Mobile catalog');
    nav.innerHTML =
      '<a href="' + SITE + '" class="nav-logo" aria-label="Paradise Mobile">' +
        '<img id="site-wordmark" src="' + logoSrc() + '" alt="Paradise Mobile" width="215" height="32" style="display:block;width:auto">' +
      '</a>' +
      '<ul class="nav-links" role="list">' + linksHTML + '</ul>' +
      '<div class="nav-actions">' +
        '<a href="' + SITE + '" class="nav-talk-trigger">Plans</a>' +
        '<button class="nav-hamburger" id="nav-hamburger" aria-label="Open menu" aria-expanded="false" type="button">' +
          '<span></span><span></span><span></span>' +
        '</button>' +
      '</div>';

    document.body.insertBefore(nav, document.body.firstChild);

    var drawerWrap = document.createElement('div');
    drawerWrap.innerHTML =
      '<div class="nav-drawer-overlay" id="nav-drawer-overlay" hidden></div>' +
      '<div class="nav-drawer" id="nav-drawer" hidden aria-label="Navigation menu" role="dialog" aria-modal="true">' +
        '<div class="nav-drawer-inner">' +
          '<ul class="nav-drawer-links" role="list">' + linksHTML + '</ul>' +
        '</div>' +
      '</div>';
    document.body.appendChild(drawerWrap.firstElementChild);
    document.body.appendChild(drawerWrap.firstElementChild);

    var hamburger = document.getElementById('nav-hamburger');
    var drawer = document.getElementById('nav-drawer');
    var drawerOverlay = document.getElementById('nav-drawer-overlay');

    function closeDrawer() {
      if (!drawer || !drawerOverlay) return;
      drawerOverlay.classList.remove('is-visible');
      drawer.classList.remove('is-visible');
      if (hamburger) {
        hamburger.classList.remove('is-active');
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.setAttribute('aria-label', 'Open menu');
      }
      setTimeout(function () {
        drawerOverlay.hidden = true;
        drawer.hidden = true;
      }, 350);
    }

    function openDrawer() {
      if (!drawer || !drawerOverlay) return;
      drawerOverlay.hidden = false;
      drawer.hidden = false;
      drawerOverlay.getBoundingClientRect();
      drawer.getBoundingClientRect();
      drawerOverlay.classList.add('is-visible');
      drawer.classList.add('is-visible');
      if (hamburger) {
        hamburger.classList.add('is-active');
        hamburger.setAttribute('aria-expanded', 'true');
        hamburger.setAttribute('aria-label', 'Close menu');
      }
    }

    if (hamburger) {
      hamburger.addEventListener('click', function () {
        if (drawer && !drawer.hidden && drawer.classList.contains('is-visible')) {
          closeDrawer();
        } else {
          openDrawer();
        }
      });
    }
    if (drawerOverlay) drawerOverlay.addEventListener('click', closeDrawer);
    if (drawer) {
      drawer.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', closeDrawer);
      });
    }
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer && !drawer.hidden && drawer.classList.contains('is-visible')) {
        closeDrawer();
      }
    });

    var footer = document.createElement('footer');
    footer.className = 'site-footer';
    footer.innerHTML =
      '<a href="' + SITE + '" class="footer-logo" aria-label="Paradise Mobile">' +
        '<img id="footer-wordmark" src="' + logoSrc() + '" alt="Paradise Mobile" style="display:block;height:20px;width:auto">' +
      '</a>' +
      '<p class="footer-tagline">Context-Driven Delivery — AI generates from executable context.</p>' +
      '<div class="footer-mode">' +
        '<div class="mode-switch" role="group" aria-label="Display mode">' +
          '<button class="mode-btn" type="button" data-mode="executive" aria-label="Switch to Executive (light) mode">' +
            '<span class="mode-icon mode-icon--sun" aria-hidden="true">☀</span>' +
            '<span class="mode-text">Executive</span>' +
          '</button>' +
          '<button class="mode-btn" type="button" data-mode="engineering" aria-label="Switch to Engineering (dark) mode">' +
            '<span class="mode-icon mode-icon--moon" aria-hidden="true">☾</span>' +
            '<span class="mode-text">Engineer</span>' +
          '</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(footer);

    applyMode(_mode);
    document.querySelectorAll('.mode-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        _mode = btn.dataset.mode;
        try { localStorage.setItem(KEY, _mode); } catch (e) {}
        applyMode(_mode);
      });
    });
  }

  function applyMode(m) {
    var isEng = m === ENGINEERING;
    document.documentElement.classList.add('paradise-brand');
    document.documentElement.setAttribute('data-theme', isEng ? ENGINEERING : '');
    document.querySelectorAll('.mode-btn').forEach(function (btn) {
      btn.classList.toggle('is-active', btn.dataset.mode === m);
    });
  }

  function handleScroll() {
    var nav = document.querySelector('.site-nav');
    if (!nav) return;
    nav.classList.toggle('is-scrolled', window.scrollY > 20);
  }

  function boot() {
    inject();
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
}());
