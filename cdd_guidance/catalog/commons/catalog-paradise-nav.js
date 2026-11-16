/**
 * The Paradise Mobile brand for the catalog's navigation. A Paradise page loads this, then catalog-nav.js, which reads
 * window.catalogNavBrand and draws the same header, drawer, footer, and display modes in Paradise's colours.
 */
(function () {
  'use strict';

  var SITE = 'https://paradisemobile.bm/';

  window.catalogNavBrand = {
    modeKey: 'paradise-mode',
    defaultMode: 'executive',
    marksAbdTheme: false,
    rootClass: 'paradise-brand',
    navLabel: 'Paradise Mobile catalog',
    homeLabel: 'Paradise Mobile',
    logoAlt: 'Paradise Mobile',
    logoSize: { width: 215, height: 32 },
    footerLogoStyle: 'display:block;height:20px;width:auto',
    talkLabel: 'Plans',
    footerTagline: 'Context-Driven Delivery — AI generates from executable context.',
    previewCommons: '',
    homeHref: function () {
      return SITE;
    },
    logo: function () {
      return 'brand/paradise-logo.svg';
    },
    links: function (prefix) {
      return [
        { id: 'hub', label: 'catalog', href: prefix + 'paradise.html' },
        { id: 'workflow', label: 'workflow', href: prefix + 'paradise-workflow.html' },
      ];
    },
  };
}());
