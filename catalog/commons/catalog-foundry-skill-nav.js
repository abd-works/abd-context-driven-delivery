/* Foundry kanban — unified filter for hub + skill pages. No behavioural differences. */
(function () {
  'use strict';

  var FILTER_KEY = 'abd-foundry-skill-nav-filter';
  var STAGE_FILTER_KEY = 'abd-foundry-skill-nav-stage-filter';
  var SKILLS_EXPANDED_KEY_SKILL = 'abd-foundry-skill-page-skills-expanded';
  var SKILLS_EXPANDED_KEY_HUB = 'abd-foundry-hub-skills-expanded';
  var CROSSCUT_KEY = 'abd-foundry-skill-nav-crosscut';
  var KANBAN_SCROLL_PARAM = 'kanbanScroll';
  var COLLAPSED_COLS_KEY = 'abd-foundry-skill-nav-col-collapsed';
  var COLLAPSED_COL_WIDTH = '28px';
  var PRACTICE_COL_WIDTH = '220px';

  function stripScrollRestoreFromUrl() {
    try {
      if (!window.history || !window.history.replaceState) return;
      var params = new URLSearchParams(window.location.search);
      if (!params.has(KANBAN_SCROLL_PARAM)) return;
      params.delete(KANBAN_SCROLL_PARAM);
      var q = params.toString();
      var page = pageBasename();
      window.history.replaceState({}, '', q ? page + '?' + q : page);
    } catch (err) {}
  }

  function appendScrollRestoreToHref(href) {
    if (!href) return href;
    var hashIdx = href.indexOf('#');
    var hash = hashIdx >= 0 ? href.slice(hashIdx) : '';
    if (hashIdx >= 0) href = href.slice(0, hashIdx);
    var qIdx = href.indexOf('?');
    var pathPart = qIdx >= 0 ? href.slice(0, qIdx) : href;
    var query = qIdx >= 0 ? href.slice(qIdx + 1) : '';
    var params = new URLSearchParams(query);
    params.set(KANBAN_SCROLL_PARAM, String(Math.round(window.scrollY)));
    var qs = params.toString();
    return pathPart + (qs ? '?' + qs : '') + hash;
  }

  function maxScrollY() {
    return Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
  }

  function pendingScrollY() {
    var y = window.__foundryPendingScrollY;
    if (y != null && !isNaN(y)) return y;
    try {
      var raw = new URLSearchParams(window.location.search).get(KANBAN_SCROLL_PARAM);
      if (!raw) return null;
      y = parseFloat(raw);
      return isNaN(y) ? null : y;
    } catch (err) { return null; }
  }

  function applyPendingScrollRestore() {
    var y = pendingScrollY();
    if (y == null) {
      document.documentElement.classList.remove('foundry-scroll-pending');
      return;
    }
    window.scrollTo(0, Math.min(y, maxScrollY()));
    document.documentElement.classList.remove('foundry-scroll-pending');
  }

  function clearPendingScrollRestore() {
    document.documentElement.classList.remove('foundry-scroll-pending');
    if (window.location.search.indexOf(KANBAN_SCROLL_PARAM + '=') >= 0) {
      stripScrollRestoreFromUrl();
    }
    try { delete window.__foundryPendingScrollY; } catch (err) { window.__foundryPendingScrollY = undefined; }
  }

  function readSavedFilter() {
    try {
      var raw = window.sessionStorage.getItem(FILTER_KEY);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      var families = Array.isArray(parsed.families) ? parsed.families : [];
      if (parsed.other && families.indexOf('other') === -1) families.push('other');
      return { families: families };
    } catch (err) { return null; }
  }

  function saveFilter(families) {
    try {
      window.sessionStorage.setItem(FILTER_KEY, JSON.stringify({ families: families }));
    } catch (err) {}
  }

  function readSavedStageFilter() {
    try {
      var raw = window.sessionStorage.getItem(STAGE_FILTER_KEY);
      if (!raw) return [];
      if (raw.charAt(0) === '[') {
        var parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [];
      }
      return raw ? [raw] : [];
    } catch (err) { return []; }
  }

  function saveStageFilter(stageIds) {
    try {
      if (stageIds && stageIds.length) {
        window.sessionStorage.setItem(STAGE_FILTER_KEY, JSON.stringify(stageIds));
      } else {
        window.sessionStorage.removeItem(STAGE_FILTER_KEY);
      }
    } catch (err) {}
  }

  function isHubKanban() {
    return !surface.getAttribute('data-initial-family');
  }

  function skillsExpandedStorageKey() {
    return isHubKanban() ? SKILLS_EXPANDED_KEY_HUB : SKILLS_EXPANDED_KEY_SKILL;
  }

  function readSkillsExpandedPref() {
    try { return window.sessionStorage.getItem(skillsExpandedStorageKey()) === '1'; }
    catch (err) { return false; }
  }

  function saveSkillsExpandedPref(expanded) {
    try { window.sessionStorage.setItem(skillsExpandedStorageKey(), expanded ? '1' : '0'); }
    catch (err) {}
  }

  function readCrosscutPref() {
    try {
      var raw = window.sessionStorage.getItem(CROSSCUT_KEY);
      if (!raw) return [];
      var parsed = JSON.parse(raw);
      return Array.isArray(parsed.groups) ? parsed.groups : [];
    } catch (err) { return []; }
  }

  function saveCrosscutPref(groups) {
    try {
      window.sessionStorage.setItem(CROSSCUT_KEY, JSON.stringify({ groups: groups }));
    } catch (err) {}
  }

  function readCollapsedColsPref() {
    try {
      var raw = window.sessionStorage.getItem(COLLAPSED_COLS_KEY);
      if (!raw) return [];
      var parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch (err) { return []; }
  }

  function saveCollapsedColsPref(cols) {
    try {
      if (cols && cols.length) {
        window.sessionStorage.setItem(COLLAPSED_COLS_KEY, JSON.stringify(cols));
      } else {
        window.sessionStorage.removeItem(COLLAPSED_COLS_KEY);
      }
    } catch (err) {}
  }

  function familyFromTicket(link) {
    var row = link.closest('.aad-skill-row[data-family]');
    return row ? row.getAttribute('data-family') : null;
  }

  function collectSelectedFamilies(surface) {
    var out = [];
    surface.querySelectorAll('.foundry-family-toggle.is-selected').forEach(function (btn) {
      var f = btn.getAttribute('data-family');
      if (f && out.indexOf(f) === -1) out.push(f);
    });
    return out;
  }

  function pageBasename() {
    var path = window.location.pathname || '';
    var parts = path.split('/');
    var base = parts[parts.length - 1].split('?')[0] || '';
    // Directory URL (http://host/catalog/) has an empty final segment — treat as index.
    return base || 'index.html';
  }

  function stageFromUrl() {
    try { return new URLSearchParams(window.location.search).get('stage') || ''; }
    catch (err) { return ''; }
  }

  function parseSkillHref(href) {
    if (!href) return { base: '', stage: '' };
    var hashIdx = href.indexOf('#');
    if (hashIdx >= 0) href = href.slice(0, hashIdx);
    var q = href.indexOf('?');
    var base = q >= 0 ? href.slice(0, q) : href;
    var stage = '';
    if (q >= 0) {
      try { stage = new URLSearchParams(href.slice(q)).get('stage') || ''; } catch (err) {}
    }
    return { base: base, stage: stage };
  }

  function buildStageUrl(stageIds) {
    var page = pageBasename();
    if (!stageIds || !stageIds.length) return page;
    if (stageIds.length === 1) {
      return page + '?stage=' + encodeURIComponent(stageIds[0]);
    }
    return page + '?stage=' + stageIds.map(encodeURIComponent).join(',');
  }

  /* Save scroll position before navigating — do NOT apply family filter from
     fidelity/action ticket clicks (only row/column headers filter). */
  document.querySelectorAll('.foundry-kanban-surface').forEach(function (surf) {
    surf.querySelectorAll('a.kb-ticket.aad-skill[href]').forEach(function (link) {
      if (link.classList.contains('foundry-practice-col__card')) return;
      if (link.classList.contains('aad-crosscut-row-title')) return;
      link.addEventListener('click', function () {
        var parsed = parseSkillHref(link.getAttribute('href') || '');
        if (parsed.base && parsed.base !== pageBasename()) {
          link.setAttribute('href', appendScrollRestoreToHref(link.getAttribute('href') || ''));
        }
      });
    });
  });

  /* ── Filter logic — identical for hub and skill pages ── */
  var surface = document.querySelector('.foundry-kanban-surface');
  if (!surface) {
    /* Action/utility/grid pages have no board — still clear scroll-hide. */
    applyPendingScrollRestore();
    clearPendingScrollRestore();
    return;
  }

  surface.classList.add('foundry-skill-nav-settling');

  var supportingOnly = surface.classList.contains('foundry-kanban-surface--supporting-only');
  var familyButtons = Array.prototype.slice.call(surface.querySelectorAll('.foundry-family-toggle'));
  var skillsToggle = supportingOnly ? null : document.getElementById('foundry-skills-toggle');
  var skillsExpanded = supportingOnly;
  var cddAlwaysExpanded = surface.classList.contains('foundry-kanban-surface--cdd-always-expanded')
    || surface.getAttribute('data-cdd-always-expanded') === '1';
  var cddNoStageFilter = cddAlwaysExpanded
    || surface.getAttribute('data-cdd-no-stage-filter') === '1';
  if (cddAlwaysExpanded) PRACTICE_COL_WIDTH = '200px';
  /* Stage-filter toggles only — CDD uses plain <a class="kb-col-head"> links. */
  var colHeads = Array.prototype.slice.call(surface.querySelectorAll('.kb-col-head[data-stage]'));
  var rows = Array.prototype.slice.call(surface.querySelectorAll('.kb-col > .aad-skill-row[data-family]'));
  var stageSkillRows = Array.prototype.slice.call(surface.querySelectorAll('.foundry-stage-skills'));
  var crosscutPracticeRows = Array.prototype.slice.call(
    surface.querySelectorAll('.aad-delivery-crosscut-section--supporting .aad-delivery-crosscut-row')
  );
  var crosscutOtherRows = Array.prototype.slice.call(
    surface.querySelectorAll('.aad-delivery-crosscut-section--foundational .aad-delivery-crosscut-row')
  );
  var crosscutToggles = Array.prototype.slice.call(surface.querySelectorAll('.aad-crosscut-row-toggle'));
  var supportingSection = surface.querySelector('.aad-delivery-crosscut-section--supporting');
  var foundationalSection = surface.querySelector('.aad-delivery-crosscut-section--foundational');

  var FAMILY_ROW_ORDER = [
    'stories',
    'clean_engineering',
    'ux',
    'bdd',
    'ddd'
  ];
  var ROW_H = 'var(--foundry-skill-row-h)';
  var ZERO_ROW = '0px';

  var collapsedCols = new Set();
  var boardGrid = surface.querySelector('.foundry-board-grid');
  var stageColOrder = [];
  if (boardGrid) {
    boardGrid.querySelectorAll(':scope > .kb-col[data-stage]').forEach(function (col) {
      stageColOrder.push(col.getAttribute('data-stage'));
    });
  }

  function updateGridColumns() {
    if (!boardGrid || !stageColOrder.length) return;
    var tracks = stageColOrder.map(function (stage) {
      return collapsedCols.has(stage) ? COLLAPSED_COL_WIDTH : 'minmax(0,1fr)';
    });
    boardGrid.style.gridTemplateColumns = PRACTICE_COL_WIDTH + ' ' + tracks.join(' ');
  }

  function setColCollapsed(stage, collapsed) {
    if (collapsed) { collapsedCols.add(stage); } else { collapsedCols.delete(stage); }
    if (!boardGrid) return;
    boardGrid.querySelectorAll(':scope > .kb-col[data-stage="' + stage + '"]').forEach(function (col) {
      col.classList.toggle('kb-col--collapsed', collapsed);
      var btn = col.querySelector('.kb-col-collapse-btn');
      if (btn) {
        btn.setAttribute('aria-label', collapsed ? 'Expand column' : 'Collapse column');
        btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
      }
    });
    updateGridColumns();
    saveCollapsedColsPref(Array.from(collapsedCols));
  }

  function toggleColCollapse(stage) {
    setColCollapsed(stage, !collapsedCols.has(stage));
  }

  var selectedFamilies = new Set();
  var selectedCrosscutGroups = new Set();
  var selectedStages = new Set();
  var highlightedStage = '';

  function syncIdleState() {
    var idle = selectedFamilies.size === 0;
    surface.classList.toggle('foundry-skill-filter-idle', idle);
    surface.classList.toggle('foundry-skill-filter-active', !idle);
    surface.classList.toggle('foundry-skill-filter-single', !idle && selectedFamilies.size === 1);
    surface.classList.toggle('foundry-skill-filter-multi', selectedFamilies.size > 1);
    surface.classList.toggle('foundry-skill-filter-other', selectedFamilies.has('other'));
    surface.classList.toggle('foundry-other-rows-collapsed', !otherVisible());
  }

  /* Board rows: practice families show when idle or ticked; other rows only when other is ticked */
  function rowVisible(row) {
    if (selectedStages.size > 0) {
      var col = row.closest('.kb-col[data-stage]');
      if (!col || !selectedStages.has(col.getAttribute('data-stage'))) return false;
    }
    var family = row.getAttribute('data-family');
    if (family === 'other') {
      return selectedFamilies.has('other');
    }
    if (selectedFamilies.size === 0) return true;
    if (!family || !selectedFamilies.has(family)) return false;
    if (row.classList.contains('aad-skill-row--empty')) return false;
    return true;
  }

  function otherVisible() {
    return selectedFamilies.has('other');
  }

  function updateCrosscutRowSkills(row, expanded) {
    var skills = row.querySelector('.aad-delivery-crosscut-skills');
    if (!skills) return;
    if (expanded) {
      skills.classList.add('is-skills-visible');
      skills.classList.remove('aad-delivery-crosscut-skills--collapsed');
    } else {
      skills.classList.remove('is-skills-visible');
      skills.classList.add('aad-delivery-crosscut-skills--collapsed');
    }
  }

  var KANBAN_SUPPORTING_GROUP = 'kanban';

  /* Supporting section: filter by family; kanban row is always visible (supporting-only practice). */
  function crosscutRowVisible(row) {
    var group = row.getAttribute('data-crosscut-group');
    if (group === KANBAN_SUPPORTING_GROUP) return true;
    if (selectedFamilies.size === 0) return true;
    var family = row.getAttribute('data-family');
    return Boolean(family && selectedFamilies.has(family));
  }

  function updateCrosscutSections() {
    var showSupporting = skillsExpanded || supportingOnly || cddAlwaysExpanded;
    var showFoundations = cddAlwaysExpanded
      ? true
      : ((skillsExpanded && otherVisible()) || supportingOnly);

    crosscutPracticeRows.forEach(function (row) {
      var vis = (skillsExpanded || supportingOnly || cddAlwaysExpanded) && crosscutRowVisible(row);
      row.classList.toggle('is-filter-visible', vis);
      updateCrosscutRowSkills(row, vis);
    });
    if (supportingSection) {
      supportingSection.classList.toggle('is-filter-visible', showSupporting);
      supportingSection.hidden = !showSupporting;
    }

    crosscutOtherRows.forEach(function (row) {
      var vis = showFoundations;
      row.classList.toggle('is-filter-visible', vis);
      updateCrosscutRowSkills(row, vis);
    });
    if (foundationalSection) {
      foundationalSection.classList.toggle('is-filter-visible', showFoundations);
      foundationalSection.hidden = !showFoundations;
    }

    stageSkillRows.forEach(function (row) {
      row.classList.toggle('is-filter-visible', skillsExpanded && otherVisible());
    });
  }

  function syncSkillsExpandClasses(expanded) {
    surface.classList.toggle('foundry-skills-collapsed', !expanded && !supportingOnly);
    surface.classList.toggle('foundry-skills-expanded', expanded || supportingOnly);
  }

  function syncBoardGridRows() {
    var board = surface.querySelector('.foundry-board-grid');
    if (!board) return;
    var famRows = FAMILY_ROW_ORDER.map(function (family) {
      if (skillsExpanded || cddAlwaysExpanded) return ROW_H;
      if (selectedFamilies.size === 0) return ROW_H;
      return selectedFamilies.has(family) ? ROW_H : ZERO_ROW;
    });
    // CDD: six tool rows only — no other-practices tracks.
    if (cddAlwaysExpanded) {
      board.style.gridTemplateRows = [
        'auto',
        famRows[0], famRows[1], famRows[2], famRows[3], famRows[4], famRows[5]
      ].join(' ');
      return;
    }
    var stageGap = ZERO_ROW;
    var otherTracks = [ZERO_ROW, ZERO_ROW, ZERO_ROW];
    if (skillsExpanded) {
      if (otherVisible()) {
        stageGap = 'var(--foundry-stage-skills-gap-h)';
        otherTracks = [ROW_H, ROW_H, ROW_H];
      } else {
        otherTracks = [ROW_H, ZERO_ROW, ZERO_ROW];
      }
    } else if (selectedFamilies.has('other')) {
      otherTracks = [ROW_H, ZERO_ROW, ZERO_ROW];
    }
    board.style.gridTemplateRows = [
      'auto',
      famRows[0],
      famRows[1],
      famRows[2],
      famRows[3],
      famRows[4],
      famRows[5],
      stageGap,
      otherTracks[0],
      otherTracks[1],
      otherTracks[2]
    ].join(' ');
  }

  function toggleCrosscutGroup(btn) {
    var group = btn.getAttribute('data-crosscut-group');
    if (!group) return;
    enableRowAnimations();
    if (selectedCrosscutGroups.has(group)) {
      selectedCrosscutGroups.delete(group);
    } else {
      selectedCrosscutGroups.add(group);
    }
    saveCrosscutPref(Array.from(selectedCrosscutGroups));
    updateCrosscutSections();
  }

  function setSkillsExpanded(expanded, source) {
    if (supportingOnly) {
      skillsExpanded = true;
      syncSkillsExpandClasses(true);
      updateCrosscutSections();
      return;
    }
    skillsExpanded = expanded;
    syncSkillsExpandClasses(expanded);
    if (skillsToggle) {
      skillsToggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      skillsToggle.classList.toggle('is-expanded', expanded);
      skillsToggle.setAttribute('aria-label',
        expanded ? 'Collapse fidelities across columns' : 'Expand fidelities across columns');
    }
    if (source === 'user') saveSkillsExpandedPref(expanded);
    updateCrosscutSections();
    applyFilter();
  }

  function applyFilter() {
    rows.forEach(function (row) {
      row.classList.toggle('is-filter-visible', rowVisible(row));
    });
    saveFilter(Array.from(selectedFamilies));
    updateCrosscutSections();
    syncIdleState();
    syncBoardGridRows();
  }

  function enableRowAnimations() {
    surface.classList.add('foundry-skill-nav-animated');
  }

  function setFamilySelected(btn, selected) {
    var family = btn.getAttribute('data-family');
    if (!family) return;
    if (selected) {
      selectedFamilies.add(family);
      btn.classList.add('is-selected');
      btn.setAttribute('aria-pressed', 'true');
    } else {
      selectedFamilies.delete(family);
      btn.classList.remove('is-selected');
      btn.setAttribute('aria-pressed', 'false');
    }
  }

  function toggleFamily(btn) {
    var family = btn.getAttribute('data-family');
    if (!family) return;
    enableRowAnimations();
    var nowSelected = !selectedFamilies.has(family);
    setFamilySelected(btn, nowSelected);
    applyFilter();
  }

  function syncStageIdleState() {
    var idle = selectedStages.size === 0;
    surface.classList.toggle('foundry-stage-filter-idle', idle);
    surface.classList.toggle('foundry-stage-filter-active', !idle);
    surface.classList.toggle('foundry-stage-filter-single', selectedStages.size === 1);
    surface.classList.toggle('foundry-stage-filter-multi', selectedStages.size > 1);
  }

  function stageHeadFiltered(stage) {
    return selectedStages.has(stage);
  }

  function stageHeadHighlighted(stage) {
    return selectedStages.size === 0 && stage === highlightedStage && Boolean(highlightedStage);
  }

  function applyStageColumnFilter() {
    var pageName = pageBasename();
    surface.querySelectorAll('.foundry-board-grid > .kb-col[data-stage]').forEach(function (col) {
      col.classList.add('is-stage-filter-visible');
    });
    surface.querySelectorAll('.kanban-stage-questions__cell[data-stage]').forEach(function (cell) {
      var stage = cell.getAttribute('data-stage');
      cell.classList.add('is-stage-filter-visible');
      cell.classList.toggle('is-active', stageHeadFiltered(stage) || stageHeadHighlighted(stage));
    });
    surface.querySelectorAll('.kb-ticket.aad-skill[data-stage]').forEach(function (el) {
      if (el.classList.contains('foundry-family-toggle')) return;
      var skillHref = (el.getAttribute('data-skill-href') || el.getAttribute('href') || '').split('?')[0];
      var onPage = skillHref === pageName;
      var inStage = el.getAttribute('data-stage') === highlightedStage;
      el.classList.toggle('kb-ticket--current', onPage && inStage && Boolean(highlightedStage));
      if (onPage && inStage && highlightedStage) el.setAttribute('aria-current', 'page');
      else el.removeAttribute('aria-current');
    });
    colHeads.forEach(function (head) {
      var stage = head.getAttribute('data-stage');
      var filtered = stageHeadFiltered(stage);
      var highlighted = stageHeadHighlighted(stage);
      head.classList.toggle('is-selected', filtered);
      head.classList.toggle('kb-col-head--current', filtered || highlighted);
      head.setAttribute('aria-pressed', filtered ? 'true' : 'false');
    });
    applyFilter();
    syncStageIdleState();
  }

  function toggleStage(stageId) {
    if (cddNoStageFilter) return;
    if (!stageId) return;
    enableRowAnimations();
    if (selectedStages.has(stageId)) {
      selectedStages.delete(stageId);
      if (highlightedStage === stageId) highlightedStage = '';
    } else {
      selectedStages.add(stageId);
    }
    var stageList = Array.from(selectedStages);
    saveStageFilter(stageList);
    if (window.history && window.history.pushState) {
      window.history.pushState({ foundryStage: stageList }, '', buildStageUrl(stageList));
    }
    applyStageColumnFilter();
  }

  window.__foundryApplyStage = function (stageId) {
    highlightedStage = stageId || '';
    if (window.history && window.history.pushState) {
      window.history.pushState({ foundryHighlight: stageId || '' }, '', buildStageUrl(stageId || ''));
    }
    applyStageColumnFilter();
  };
  window.__foundrySetSkillsExpanded = setSkillsExpanded;

  crosscutToggles.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      toggleCrosscutGroup(btn);
    });
  });

  familyButtons.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      toggleFamily(btn);
    });
  });

  if (skillsToggle) {
    skillsToggle.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      enableRowAnimations();
      setSkillsExpanded(!skillsExpanded, 'user');
    });
  }

  if (!cddNoStageFilter) {
    colHeads.forEach(function (head) {
      head.addEventListener('click', function (e) {
        var stage = head.getAttribute('data-stage');
        if (!stage) return;
        e.preventDefault();
        toggleStage(stage);
      });
    });

    surface.querySelectorAll('.kanban-stage-questions__cell[data-stage]').forEach(function (cell) {
      cell.addEventListener('click', function () {
        var stage = cell.getAttribute('data-stage');
        if (stage) toggleStage(stage);
      });
    });
  }

  /* ── Collapse buttons ── */
  surface.querySelectorAll('.kb-col-collapse-btn').forEach(function (btn) {
    var col = btn.closest('.kb-col[data-stage]');
    if (!col) return;
    var stage = col.getAttribute('data-stage');
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      toggleColCollapse(stage);
    });
  });

  /* ── Initialise state ── */
  readCollapsedColsPref().forEach(function (stage) { setColCollapsed(stage, true); });
  if (cddNoStageFilter) {
    /* Never restore stage filters on the CDD board — column heads navigate. */
    selectedStages.clear();
    highlightedStage = surface.getAttribute('data-initial-stage') || '';
    saveStageFilter([]);
  } else {
    var urlStage = stageFromUrl();
    highlightedStage = urlStage || surface.getAttribute('data-initial-stage') || '';
    readSavedStageFilter().forEach(function (stage) { selectedStages.add(stage); });
  }

  var saved = readSavedFilter();
  if (saved && saved.families.length) {
    saved.families.forEach(function (family) {
      familyButtons.forEach(function (btn) {
        if (btn.getAttribute('data-family') === family) setFamilySelected(btn, true);
      });
      selectedCrosscutGroups.add(family);
    });
  }

  var initialFamily = surface.getAttribute('data-initial-family');
  if (initialFamily) {
    familyButtons.forEach(function (btn) {
      if (btn.getAttribute('data-family') === initialFamily) setFamilySelected(btn, true);
    });
    selectedCrosscutGroups.add(initialFamily);
  }

  readCrosscutPref().forEach(function (group) { selectedCrosscutGroups.add(group); });

  applyFilter();
  if (cddAlwaysExpanded) {
    setSkillsExpanded(true, 'restore');
  } else if (supportingOnly) {
    setSkillsExpanded(true, 'restore');
  } else {
    setSkillsExpanded(readSkillsExpandedPref(), 'restore');
  }
  applyStageColumnFilter();

  window.addEventListener('popstate', function (e) {
    var poppedStage = stageFromUrl();
    highlightedStage = poppedStage || surface.getAttribute('data-initial-stage') || '';
    if (e.state && Object.prototype.hasOwnProperty.call(e.state, 'foundryStage')) {
      selectedStages = new Set();
      var restored = e.state.foundryStage;
      if (Array.isArray(restored)) {
        restored.forEach(function (stage) { if (stage) selectedStages.add(stage); });
      } else if (restored) {
        selectedStages.add(restored);
      }
      saveStageFilter(Array.from(selectedStages));
    }
    applyStageColumnFilter();
  });

  applyPendingScrollRestore();
  clearPendingScrollRestore();

  window.requestAnimationFrame(function () {
    surface.classList.remove('foundry-skill-nav-settling');
  });
})();
