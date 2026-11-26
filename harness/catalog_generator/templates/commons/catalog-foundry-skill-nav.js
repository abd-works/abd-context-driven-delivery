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

  // The reader's board choices for this browser tab, kept by catalog-nav.js, which every catalog page loads first.
  var preferences = window.catalogPreferences.session;

  /** Change the address bar without reloading. A page opened from disk has no origin to rewrite its URL in, and the
   * browser refuses with a SecurityError; the board still works, only the address does not follow it. */
  function rewriteUrl(method, state, url) {
    if (!window.history || !window.history[method]) return;
    try {
      window.history[method](state, '', url);
    } catch (err) {
      if (!(err instanceof DOMException && err.name === 'SecurityError')) throw err;
    }
  }

  function stripScrollRestoreFromUrl() {
    var params = new URLSearchParams(window.location.search);
    if (!params.has(KANBAN_SCROLL_PARAM)) return;
    params.delete(KANBAN_SCROLL_PARAM);
    var query = params.toString();
    var page = pageBasename();
    rewriteUrl('replaceState', {}, query ? page + '?' + query : page);
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

  /** The scroll position the page head read from the kanbanScroll parameter, or the parameter itself. */
  function pendingScrollY() {
    var y = window.foundryPendingScrollY;
    if (y != null && !isNaN(y)) return y;
    var raw = new URLSearchParams(window.location.search).get(KANBAN_SCROLL_PARAM);
    y = raw ? parseFloat(raw) : NaN;
    return isNaN(y) ? null : y;
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
    window.foundryPendingScrollY = undefined;
  }

  /** The families a reader filtered the board to; an older page saved "other" as its own flag. */
  function readSavedFilter() {
    var saved = preferences.readJson(FILTER_KEY, null);
    if (!saved) return null;
    var families = Array.isArray(saved.families) ? saved.families : [];
    if (saved.other && families.indexOf('other') === -1) families.push('other');
    return { families: families };
  }

  function saveFilter(families) {
    preferences.save(FILTER_KEY, JSON.stringify({ families: families }));
  }

  /** A list saved as JSON, or forgotten when it is empty. */
  function saveList(key, list) {
    if (list && list.length) preferences.save(key, JSON.stringify(list));
    else preferences.forget(key);
  }

  function readSavedList(key) {
    var saved = preferences.readJson(key, []);
    return Array.isArray(saved) ? saved : [];
  }

  /** The stages a reader filtered the board to; an older page saved a single stage as plain text. */
  function readSavedStageFilter() {
    var raw = preferences.read(STAGE_FILTER_KEY);
    if (!raw) return [];
    return raw.charAt(0) === '[' ? readSavedList(STAGE_FILTER_KEY) : [raw];
  }

  function saveStageFilter(stageIds) {
    saveList(STAGE_FILTER_KEY, stageIds);
  }

  function isHubKanban() {
    return !surface.getAttribute('data-initial-family');
  }

  function skillsExpandedStorageKey() {
    return isHubKanban() ? SKILLS_EXPANDED_KEY_HUB : SKILLS_EXPANDED_KEY_SKILL;
  }

  function readSkillsExpandedPref() {
    return preferences.read(skillsExpandedStorageKey()) === '1';
  }

  function saveSkillsExpandedPref(expanded) {
    preferences.save(skillsExpandedStorageKey(), expanded ? '1' : '0');
  }

  function readCrosscutPref() {
    var saved = preferences.readJson(CROSSCUT_KEY, {});
    return saved && Array.isArray(saved.groups) ? saved.groups : [];
  }

  function saveCrosscutPref(groups) {
    preferences.save(CROSSCUT_KEY, JSON.stringify({ groups: groups }));
  }

  function readCollapsedColsPref() {
    return readSavedList(COLLAPSED_COLS_KEY);
  }

  function saveCollapsedColsPref(cols) {
    saveList(COLLAPSED_COLS_KEY, cols);
  }

  function pageBasename() {
    var path = window.location.pathname || '';
    var parts = path.split('/');
    var base = parts[parts.length - 1].split('?')[0] || '';
    // Directory URL (http://host/catalog/) has an empty final segment — treat as index.
    return base || 'index.html';
  }

  function stageFromUrl() {
    return new URLSearchParams(window.location.search).get('stage') || '';
  }

  function parseSkillHref(href) {
    if (!href) return { base: '', stage: '' };
    var hashIdx = href.indexOf('#');
    if (hashIdx >= 0) href = href.slice(0, hashIdx);
    var q = href.indexOf('?');
    var base = q >= 0 ? href.slice(0, q) : href;
    var stage = q >= 0 ? new URLSearchParams(href.slice(q)).get('stage') || '' : '';
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

  /* Board rows stay visible. A practice chip links to that practice page. */
  function rowVisible(row) {
    if (cddAlwaysExpanded) return true;
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
    if (cddAlwaysExpanded) return true;
    var group = row.getAttribute('data-crosscut-group');
    if (group === KANBAN_SUPPORTING_GROUP) return true;
    if (selectedFamilies.size === 0) return true;
    var family = row.getAttribute('data-family');
    return Boolean(family && selectedFamilies.has(family));
  }

  /** Show or hide each crosscut row, opening the skills of a shown one. */
  function showCrosscutRows(crosscutRows, rowShown) {
    crosscutRows.forEach(function (row) {
      var shown = rowShown(row);
      row.classList.toggle('is-filter-visible', shown);
      updateCrosscutRowSkills(row, shown);
    });
  }

  function showSection(section, shown) {
    if (!section) return;
    section.classList.toggle('is-filter-visible', shown);
    section.hidden = !shown;
  }

  function updateCrosscutSections() {
    var showSupporting = skillsExpanded || supportingOnly || cddAlwaysExpanded;
    var showFoundations = cddAlwaysExpanded || (skillsExpanded && otherVisible()) || supportingOnly;
    showCrosscutRows(crosscutPracticeRows, function (row) { return showSupporting && crosscutRowVisible(row); });
    showSection(supportingSection, showSupporting);
    showCrosscutRows(crosscutOtherRows, function () { return showFoundations; });
    showSection(foundationalSection, showFoundations);
    stageSkillRows.forEach(function (row) {
      row.classList.toggle('is-filter-visible', skillsExpanded && otherVisible());
    });
  }

  function syncSkillsExpandClasses(expanded) {
    surface.classList.toggle('foundry-skills-collapsed', !expanded && !supportingOnly);
    surface.classList.toggle('foundry-skills-expanded', expanded || supportingOnly);
  }

  /** The tracks below the practice rows: the gap before the stage skills and the three other-practice rows. */
  function otherPracticeTracks() {
    if (skillsExpanded && otherVisible()) return ['var(--foundry-stage-skills-gap-h)', ROW_H, ROW_H, ROW_H];
    if (skillsExpanded || selectedFamilies.has('other')) return [ZERO_ROW, ROW_H, ZERO_ROW, ZERO_ROW];
    return [ZERO_ROW, ZERO_ROW, ZERO_ROW, ZERO_ROW];
  }

  /** Size the board's rows: a practice row the family filter hides closes to nothing. */
  function syncBoardGridRows() {
    var board = surface.querySelector('.foundry-board-grid');
    if (!board) return;
    var familyTracks = FAMILY_ROW_ORDER.map(function (family) {
      var shown = skillsExpanded || cddAlwaysExpanded || selectedFamilies.size === 0 || selectedFamilies.has(family);
      return shown ? ROW_H : ZERO_ROW;
    });
    // The CDD board has only its practice rows, no other-practice tracks.
    var tracks = ['auto'].concat(familyTracks, cddAlwaysExpanded ? [] : otherPracticeTracks());
    board.style.gridTemplateRows = tracks.join(' ');
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

  /** Mark the ticket for this page in the highlighted stage as the current one. */
  function markCurrentTickets() {
    var pageName = pageBasename();
    surface.querySelectorAll('.kb-ticket.aad-skill[data-stage]').forEach(function (ticket) {
      if (ticket.classList.contains('foundry-family-toggle')) return;
      var skillHref = (ticket.getAttribute('data-skill-href') || ticket.getAttribute('href') || '').split('?')[0];
      var current = Boolean(highlightedStage) && skillHref === pageName && ticket.getAttribute('data-stage') === highlightedStage;
      ticket.classList.toggle('kb-ticket--current', current);
      if (current) ticket.setAttribute('aria-current', 'page');
      else ticket.removeAttribute('aria-current');
    });
  }

  function markStageHeads() {
    surface.querySelectorAll('.kanban-stage-questions__cell[data-stage]').forEach(function (cell) {
      var stage = cell.getAttribute('data-stage');
      cell.classList.add('is-stage-filter-visible');
      cell.classList.toggle('is-active', stageHeadFiltered(stage) || stageHeadHighlighted(stage));
    });
    colHeads.forEach(function (head) {
      var stage = head.getAttribute('data-stage');
      var filtered = stageHeadFiltered(stage);
      head.classList.toggle('is-selected', filtered);
      head.classList.toggle('kb-col-head--current', filtered || stageHeadHighlighted(stage));
      head.setAttribute('aria-pressed', filtered ? 'true' : 'false');
    });
  }

  function applyStageColumnFilter() {
    surface.querySelectorAll('.foundry-board-grid > .kb-col[data-stage]').forEach(function (col) {
      col.classList.add('is-stage-filter-visible');
    });
    markStageHeads();
    markCurrentTickets();
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
    rewriteUrl('pushState', { foundryStage: stageList }, buildStageUrl(stageList));
    applyStageColumnFilter();
  }

  // The tour (catalog-foundry-tour.js) opens and closes the skill rows as it walks the board.
  window.catalogBoardSetSkillsExpanded = function (expanded) {
    setSkillsExpanded(expanded);
  };

  crosscutToggles.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      toggleCrosscutGroup(btn);
    });
  });

  familyButtons.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      if (btn.getAttribute('href')) return;
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

  var saved = cddAlwaysExpanded ? null : readSavedFilter();
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

  document.querySelectorAll('.kanban-stage-questions--cdd').forEach(function (row) {
    var btn = row.querySelector('.policy-boxes-toggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var collapsed = row.classList.toggle('is-collapsed');
      btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
      btn.setAttribute('aria-label', collapsed ? 'Show stage policies' : 'Hide stage policies');
    });
  });

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
