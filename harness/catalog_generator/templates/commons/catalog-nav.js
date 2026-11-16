/**
 * Foundry catalog — site nav (the brand's header, drawer, and footer, and the executive / engineering display mode).
 * Loads synchronously in <head> for mode init; injects nav + footer on DOMContentLoaded.
 *
 * Body attributes (set by the catalog generator):
 *   data-nav-prefix     — relative path to catalog root ("" or "../")
 *   data-nav-current    — the page whose link is marked current (hub: the catalog index)
 *   data-nav-site-base  — relative or absolute URL prefix to the brand's marketing site root
 *
 * A page that wears another brand defines window.catalogNavBrand before loading this script (see
 * catalog-paradise-nav.js); every other page wears abd.works.
 *
 * It also publishes window.catalogPreferences, the one place the catalog's scripts remember a reader's choices.
 */
(function () {
  'use strict';

  var EXECUTIVE = 'executive';
  var ENGINEERING = 'engineering';
  // How long the drawer takes to slide away (its CSS transition) before it is hidden.
  var DRAWER_CLOSE_MS = 350;
  // How far the page scrolls before the navigation takes its scrolled look.
  var SCROLLED_AFTER_PX = 20;
  var EXTERNAL_PREVIEW_HOSTS = ['htmlpreview.github.io', 'raw.githack.com', 'rawcdn.githack.com', 'html-preview.github.io'];

  /**
   * A reader's remembered choices in one browser storage. A private window, or a browser that blocks site data,
   * refuses storage with a DOMException; the catalog then works without remembering, so those refusals are expected.
   */
  function StoredPreferences(storageName) {
    this.storageName = storageName;
  }

  StoredPreferences.prototype.storage = function () {
    try {
      return window[this.storageName];
    } catch (err) {
      if (err instanceof DOMException) return null;
      throw err;
    }
  };

  StoredPreferences.prototype.read = function (key) {
    var storage = this.storage();
    if (!storage) return null;
    try {
      return storage.getItem(key);
    } catch (err) {
      if (err instanceof DOMException) return null;
      throw err;
    }
  };

  /** A remembered value saved as JSON; absent when none is saved or an older page saved it in another shape. */
  StoredPreferences.prototype.readJson = function (key, absent) {
    var raw = this.read(key);
    if (!raw) return absent;
    try {
      return JSON.parse(raw);
    } catch (err) {
      if (err instanceof SyntaxError) return absent;
      throw err;
    }
  };

  StoredPreferences.prototype.save = function (key, value) {
    var storage = this.storage();
    if (!storage) return;
    try {
      storage.setItem(key, value);
    } catch (err) {
      if (!(err instanceof DOMException)) throw err;
    }
  };

  StoredPreferences.prototype.forget = function (key) {
    var storage = this.storage();
    if (!storage) return;
    try {
      storage.removeItem(key);
    } catch (err) {
      if (!(err instanceof DOMException)) throw err;
    }
  };

  window.catalogPreferences = {
    lasting: new StoredPreferences('localStorage'),
    session: new StoredPreferences('sessionStorage'),
  };

  function bodyAttribute(name) {
    return (document.body && document.body.getAttribute(name)) || '';
  }

  function siteBase() {
    var base = bodyAttribute('data-nav-site-base') || 'https://abd.works/';
    return base.charAt(base.length - 1) === '/' ? base : base + '/';
  }

  var ABD_WORKS = {
    modeKey: 'abd-mode',
    defaultMode: ENGINEERING,
    marksAbdTheme: true,
    rootClass: '',
    navLabel: 'Site navigation',
    homeLabel: 'abd.works home',
    logoAlt: 'abd.works',
    logoSize: { width: 548, height: 178 },
    footerLogoStyle: 'display:block;height:20px;width:auto;opacity:0.6',
    talkLabel: 'LET\'S TALK',
    footerTagline: 'Tools don\'t transform companies. People do.',
    previewCommons: 'https://raw.githubusercontent.com/abd-works/abd-skills/main/catalog/commons/',
    homeHref: function () {
      return siteBase() + 'index.html';
    },
    logo: function (mode) {
      return 'brand/abd.works.wordmark.' + (mode === ENGINEERING ? 'white' : 'black') + '.svg';
    },
    links: function (prefix) {
      return [{ id: 'forge', label: 'forge', href: prefix + 'index.html', currentOn: ['hub', ''], className: 'nav-links__foundry' }];
    },
  };

  var brand = window.catalogNavBrand || ABD_WORKS;

  function isExternalHtmlPreview() {
    return EXTERNAL_PREVIEW_HOSTS.indexOf(location.hostname.toLowerCase()) !== -1;
  }

  function modeFromUrl() {
    var query = new URLSearchParams(location.search);
    var mode = query.get('mode') || query.get(brand.modeKey);
    return mode === ENGINEERING || mode === EXECUTIVE ? mode : null;
  }

  function resolveInitialMode() {
    var fromUrl = modeFromUrl();
    if (fromUrl) return fromUrl;
    if (isExternalHtmlPreview()) return ENGINEERING;
    var stored = window.catalogPreferences.lasting.read(brand.modeKey);
    return stored === EXECUTIVE || stored === ENGINEERING ? stored : brand.defaultMode;
  }

  /** The folder this script was loaded from, where the brand's marks sit; a preview host serves them from GitHub. */
  function commonsBase() {
    if (isExternalHtmlPreview() && brand.previewCommons) return brand.previewCommons;
    var script = document.currentScript;
    return script && script.src ? new URL('.', script.src).href : 'commons/';
  }

  function pointStylesheetsAtPreview() {
    if (!isExternalHtmlPreview() || !brand.previewCommons) return;
    document.querySelectorAll('link[rel="stylesheet"]').forEach(function (link) {
      if ((link.getAttribute('href') || '').indexOf('site.css') !== -1) {
        link.href = brand.previewCommons + 'site.css?v=foundry-3';
      }
    });
  }

  var COMMONS = commonsBase();
  var mode = resolveInitialMode();

  function logoSrc(forMode) {
    return COMMONS + brand.logo(forMode);
  }

  function applyMode(chosen) {
    var root = document.documentElement;
    var engineering = chosen === ENGINEERING;
    if (brand.rootClass) root.classList.add(brand.rootClass);
    root.setAttribute('data-theme', engineering ? ENGINEERING : '');
    if (brand.marksAbdTheme) root.setAttribute('data-abd-theme', engineering ? ENGINEERING : EXECUTIVE);
    document.querySelectorAll('.mode-btn').forEach(function (button) {
      button.classList.toggle('is-active', button.dataset.mode === chosen);
    });
    document.querySelectorAll('#site-wordmark, #footer-wordmark').forEach(function (image) {
      image.setAttribute('src', logoSrc(chosen));
    });
  }

  /** Before the body renders, wear the brand and, in engineering mode, its dark theme, so the page does not flash. */
  function applyInitialTheme() {
    var root = document.documentElement;
    if (brand.rootClass) root.classList.add(brand.rootClass);
    if (mode !== ENGINEERING) return;
    root.setAttribute('data-theme', ENGINEERING);
    if (brand.marksAbdTheme) root.setAttribute('data-abd-theme', ENGINEERING);
  }

  function linksHtml(currentPage) {
    return brand.links(bodyAttribute('data-nav-prefix')).map(function (link) {
      var current = (link.currentOn || [link.id]).indexOf(currentPage) !== -1;
      return '<li><a href="' + link.href + '"' +
        (current ? ' aria-current="page"' : '') +
        (link.className ? ' class="' + link.className + '"' : '') +
        '>' + link.label + '</a></li>';
    }).join('');
  }

  function navHtml(links) {
    var home = brand.homeHref();
    return '<a href="' + home + '" class="nav-logo" aria-label="' + brand.homeLabel + '">' +
        '<img id="site-wordmark" src="' + logoSrc(mode) + '" alt="' + brand.logoAlt + '"' +
        ' width="' + brand.logoSize.width + '" height="' + brand.logoSize.height + '" style="display:block;width:auto">' +
      '</a>' +
      '<ul class="nav-links" role="list">' + links + '</ul>' +
      '<div class="nav-actions">' +
        '<a href="' + home + '" class="nav-talk-trigger">' + brand.talkLabel + '</a>' +
        '<button class="nav-hamburger" id="nav-hamburger" aria-label="Open menu" aria-expanded="false" type="button">' +
          '<span></span><span></span><span></span>' +
        '</button>' +
      '</div>';
  }

  function drawerHtml(links) {
    return '<div class="nav-drawer-overlay" id="nav-drawer-overlay" hidden></div>' +
      '<div class="nav-drawer" id="nav-drawer" hidden aria-label="Navigation menu" role="dialog" aria-modal="true">' +
        '<div class="nav-drawer-inner"><ul class="nav-drawer-links" role="list">' + links + '</ul></div>' +
      '</div>';
  }

  function modeButtonHtml(buttonMode, label, icon, iconClass) {
    return '<button class="mode-btn" type="button" data-mode="' + buttonMode + '"' +
      ' aria-label="Switch to ' + (buttonMode === EXECUTIVE ? 'Executive (light)' : 'Engineering (dark)') + ' mode">' +
        '<span class="mode-icon ' + iconClass + '" aria-hidden="true">' + icon + '</span>' +
        '<span class="mode-text">' + label + '</span>' +
      '</button>';
  }

  function footerHtml() {
    return '<a href="' + brand.homeHref() + '" class="footer-logo" aria-label="' + brand.homeLabel + '">' +
        '<img id="footer-wordmark" src="' + logoSrc(mode) + '" alt="' + brand.logoAlt + '" style="' + brand.footerLogoStyle + '">' +
      '</a>' +
      '<p class="footer-tagline">' + brand.footerTagline + '</p>' +
      '<div class="footer-mode"><div class="mode-switch" role="group" aria-label="Display mode">' +
        modeButtonHtml(EXECUTIVE, 'Executive', '☀', 'mode-icon--sun') +
        modeButtonHtml(ENGINEERING, 'Engineer', '☾', 'mode-icon--moon') +
      '</div></div>';
  }

  function element(tag, className, html) {
    var made = document.createElement(tag);
    made.className = className;
    made.innerHTML = html;
    return made;
  }

  /** The menu the hamburger opens on narrow screens: it slides in over an overlay and closes on Escape or a link. */
  function NavDrawer() {
    this.hamburger = document.getElementById('nav-hamburger');
    this.drawer = document.getElementById('nav-drawer');
    this.overlay = document.getElementById('nav-drawer-overlay');
  }

  NavDrawer.prototype.isOpen = function () {
    return !!this.drawer && !this.drawer.hidden && this.drawer.classList.contains('is-visible');
  };

  NavDrawer.prototype.markHamburger = function (open) {
    if (!this.hamburger) return;
    this.hamburger.classList.toggle('is-active', open);
    this.hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
    this.hamburger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  };

  NavDrawer.prototype.close = function () {
    var drawer = this.drawer;
    var overlay = this.overlay;
    if (!drawer || !overlay) return;
    overlay.classList.remove('is-visible');
    drawer.classList.remove('is-visible');
    this.markHamburger(false);
    setTimeout(function () {
      overlay.hidden = true;
      drawer.hidden = true;
    }, DRAWER_CLOSE_MS);
  };

  NavDrawer.prototype.open = function () {
    if (!this.drawer || !this.overlay) return;
    this.overlay.hidden = false;
    this.drawer.hidden = false;
    this.overlay.getBoundingClientRect(); // lay the unhidden drawer out first, so adding is-visible slides it in
    this.drawer.getBoundingClientRect();
    this.overlay.classList.add('is-visible');
    this.drawer.classList.add('is-visible');
    this.markHamburger(true);
  };

  NavDrawer.prototype.listen = function () {
    var navDrawer = this;
    var close = function () { navDrawer.close(); };
    if (this.hamburger) {
      this.hamburger.addEventListener('click', function () {
        if (navDrawer.isOpen()) navDrawer.close();
        else navDrawer.open();
      });
    }
    if (this.overlay) this.overlay.addEventListener('click', close);
    if (this.drawer) {
      this.drawer.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', close);
      });
    }
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && navDrawer.isOpen()) navDrawer.close();
    });
  };

  function listenToModeButtons() {
    document.querySelectorAll('.mode-btn').forEach(function (button) {
      button.addEventListener('click', function () {
        mode = button.dataset.mode;
        window.catalogPreferences.lasting.save(brand.modeKey, mode);
        applyMode(mode);
      });
    });
  }

  function inject() {
    var links = linksHtml(bodyAttribute('data-nav-current'));
    var nav = element('nav', 'site-nav', navHtml(links));
    nav.setAttribute('aria-label', brand.navLabel);
    document.body.insertBefore(nav, document.body.firstChild);
    var drawerParts = element('div', '', drawerHtml(links));
    document.body.appendChild(drawerParts.firstElementChild);
    document.body.appendChild(drawerParts.firstElementChild);
    new NavDrawer().listen();
    document.body.appendChild(element('footer', 'site-footer', footerHtml()));
    applyMode(mode);
    listenToModeButtons();
  }

  function handleScroll() {
    var nav = document.querySelector('.site-nav');
    if (nav) nav.classList.toggle('is-scrolled', window.scrollY > SCROLLED_AFTER_PX);
  }

  function boot() {
    inject();
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
  }

  pointStylesheetsAtPreview();
  applyInitialTheme();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
}());
