/**

 * Foundry catalog — site nav (abd.works marketing header + Foundry section links).

 * Loads synchronously in <head> for mode init; injects nav + footer on DOMContentLoaded.

 *

 * Body attributes (set by generate_abd_catalog.py):

 *   data-nav-prefix     — relative path to catalog root ("" or "../")

 *   data-nav-current    — hub (forge link active on catalog index only)

 *   data-nav-site-base  — relative or absolute URL prefix to abd.works marketing site root

 */

(function () {

  'use strict';



  var KEY = 'abd-mode';

  var EXECUTIVE = 'executive';

  var ENGINEERING = 'engineering';



  var SITE_LINKS = [

    { label: 'The problem', href: 'the-problem.html' },

    { label: 'The work', href: 'the-work.html' },

    { label: 'The proof', href: 'the-proof.html' }

  ];



  var _mode = EXECUTIVE;

  function isExternalHtmlPreview() {
    var h = location.hostname.toLowerCase();
    return h === 'htmlpreview.github.io'
      || h === 'raw.githack.com'
      || h === 'rawcdn.githack.com'
      || h === 'html-preview.github.io';
  }

  var PREVIEW_CATALOG_COMMONS =
    'https://raw.githubusercontent.com/abd-works/abd-skills/main/catalog/commons/';

  function modeFromUrl() {
    try {
      var q = new URLSearchParams(location.search);
      var m = q.get('mode') || q.get('abd-mode');
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
      if (stored === ENGINEERING) return ENGINEERING;
    } catch (e) {}
    return EXECUTIVE;
  }

  _mode = resolveInitialMode();

  if (isExternalHtmlPreview()) {
    document.querySelectorAll('link[rel="stylesheet"]').forEach(function (link) {
      var href = link.getAttribute('href') || '';
      if (href.indexOf('site.css') !== -1) {
        link.href = PREVIEW_CATALOG_COMMONS + 'site.css?v=foundry-3';
      }
    });
  }

  if (_mode === ENGINEERING) {

    document.documentElement.setAttribute('data-theme', ENGINEERING);

    document.documentElement.setAttribute('data-abd-theme', ENGINEERING);

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

  function resolveCommonsBase() {
    if (isExternalHtmlPreview()) return PREVIEW_CATALOG_COMMONS;
    return assetBase();
  }

  var COMMONS = resolveCommonsBase();

  var BRAND = COMMONS + 'brand/';

  function brandWordmark(name) {
    return BRAND + name;
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



  function siteBase() {

    var body = document.body;

    var base = (body && body.getAttribute('data-nav-site-base')) || 'https://abd.works/';

    if (base.indexOf('http') !== 0 && base && base.charAt(0) !== '/') {

      /* relative — keep as-is */

    }

    if (base && base.charAt(base.length - 1) !== '/') {

      base += '/';

    }

    return base;

  }



  function foundryLinks() {

    var p = navPrefix();

    return [

      { id: 'forge', label: 'forge', href: p + 'index.html' }

    ];

  }



  function linkHTML(links, currentPage) {

    return links.map(function (l) {

      if (l.sep) {

        return '<li class="nav-links__sep" aria-hidden="true"></li>';

      }

      var isCurrent = l.id === 'forge'
        ? (currentPage === 'hub' || currentPage === '')
        : l.id === currentPage;

      return '<li><a href="' + l.href + '"' +

        (isCurrent ? ' aria-current="page"' : '') +

        (l.kind === 'foundry' ? ' class="nav-links__foundry"' : '') +

        '>' + l.label + '</a></li>';

    }).join('');

  }



  function allNavLinks(currentPage) {

    var site = siteBase();

    var items = SITE_LINKS.map(function (l) {

      return { label: l.label, href: site + l.href, kind: 'site' };

    });

    items.push({ sep: true });

    foundryLinks().forEach(function (l) {

      items.push({ id: l.id, label: l.label, href: l.href, kind: 'foundry' });

    });

    return items;

  }



  function inject() {

    var currentPage = navCurrent();

    var links = allNavLinks(currentPage);

    var linksHTML = linkHTML(links, currentPage);

    var homeHref = siteBase() + 'index.html';



    var nav = document.createElement('nav');

    nav.className = 'site-nav';

    nav.setAttribute('aria-label', 'Site navigation');

    nav.innerHTML =

      '<a href="' + homeHref + '" class="nav-logo" aria-label="abd.works home">' +

        '<img id="site-wordmark"' +

        ' src="' + brandWordmark('abd.works.wordmark.black.svg') + '"' +

        ' alt="abd.works" width="548" height="178"' +

        ' style="display:block;width:auto">' +

      '</a>' +

      '<ul class="nav-links" role="list">' + linksHTML + '</ul>' +

      '<div class="nav-actions">' +

        '<a href="' + homeHref + '" class="nav-talk-trigger">LET\'S TALK</a>' +

        '<button class="nav-hamburger" id="nav-hamburger" aria-label="Open menu" aria-expanded="false" type="button">' +

          '<span></span><span></span><span></span>' +

        '</button>' +

      '</div>';



    document.body.insertBefore(nav, document.body.firstChild);



    var drawerHTML =

      '<div class="nav-drawer-overlay" id="nav-drawer-overlay" hidden></div>' +

      '<div class="nav-drawer" id="nav-drawer" hidden aria-label="Navigation menu" role="dialog" aria-modal="true">' +

        '<div class="nav-drawer-inner">' +

          '<ul class="nav-drawer-links" role="list">' + linkHTML(links, currentPage) + '</ul>' +

        '</div>' +

      '</div>';



    var drawerWrap = document.createElement('div');

    drawerWrap.innerHTML = drawerHTML;

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

      '<a href="' + homeHref + '" class="footer-logo" aria-label="abd.works home">' +

        '<img id="footer-wordmark"' +

        ' src="' + brandWordmark('abd.works.wordmark.black.svg') + '"' +

        ' alt="abd.works"' +

        ' style="display:block;height:20px;width:auto;opacity:0.6">' +

      '</a>' +

      '<p class="footer-tagline">Tools don\'t transform companies. People do.</p>' +

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

    document.documentElement.setAttribute('data-theme', isEng ? ENGINEERING : '');

    document.documentElement.setAttribute('data-abd-theme', isEng ? ENGINEERING : EXECUTIVE);



    document.querySelectorAll('.mode-btn').forEach(function (btn) {

      btn.classList.toggle('is-active', btn.dataset.mode === m);

    });



    var logoSrc = isEng
      ? brandWordmark('abd.works.wordmark.white.svg')
      : brandWordmark('abd.works.wordmark.black.svg');



    document.querySelectorAll('#site-wordmark, #footer-wordmark').forEach(function (img) {

      img.setAttribute('src', logoSrc);

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


