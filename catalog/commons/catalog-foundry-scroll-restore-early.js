/* kanbanScroll restore — inlined in foundry page <head>; layout apply in skill-nav.js */
(function () {
  'use strict';
  try {
    if ('scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual';
    }
    var raw = new URLSearchParams(window.location.search).get('kanbanScroll');
    if (!raw) return;
    var scrollY = parseFloat(raw);
    if (isNaN(scrollY)) return;
    window.__foundryPendingScrollY = scrollY;
    document.documentElement.classList.add('foundry-scroll-pending');
  } catch (err) {}
})();
