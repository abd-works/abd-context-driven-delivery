function bindFlowZoom(pane, surface) {
  if (!pane || !surface) return;
  const readout = pane.querySelector('[data-flow-zoom="reset"]');
  let zoom = 1;
  const min = 0.25;
  const max = 3;
  function apply(next, point) {
    next = Math.min(max, Math.max(min, Math.round(next * 100) / 100));
    const previous = zoom;
    const rect = pane.getBoundingClientRect();
    const localX = point ? point.x - rect.left : pane.clientWidth / 2;
    const localY = point ? point.y - rect.top : pane.clientHeight / 2;
    const contentX = pane.scrollLeft + localX;
    const contentY = pane.scrollTop + localY;
    zoom = next;
    surface.style.zoom = String(zoom);
    if (previous) {
      pane.scrollLeft = contentX * (zoom / previous) - localX;
      pane.scrollTop = contentY * (zoom / previous) - localY;
    }
    if (readout) readout.textContent = `${Math.round(zoom * 100)}%`;
  }
  pane.querySelector('[data-flow-zoom="in"]')?.addEventListener("click", () => apply(zoom * 1.1));
  pane.querySelector('[data-flow-zoom="out"]')?.addEventListener("click", () => apply(zoom / 1.1));
  readout?.addEventListener("click", () => apply(1));
  pane.addEventListener(
    "wheel",
    (event) => {
      if (!event.ctrlKey && !event.metaKey) return;
      event.preventDefault();
      apply(zoom * (event.deltaY < 0 ? 1.1 : 1 / 1.1), { x: event.clientX, y: event.clientY });
    },
    { passive: false },
  );
  document.querySelector("#explorer-frame")?.addEventListener(
    "wheel",
    (event) => {
      if (event.ctrlKey || event.metaKey) event.preventDefault();
    },
    { passive: false },
  );
  document.addEventListener("keydown", (event) => {
    if (!(event.ctrlKey || event.metaKey) || event.altKey) return;
    const zoomIn = event.key === "+" || event.key === "=";
    const zoomOut = event.key === "-" || event.key === "_";
    const reset = event.key === "0";
    if (!zoomIn && !zoomOut && !reset) return;
    event.preventDefault();
    if (event.target.closest?.("#explorer-frame")) return;
    if (zoomIn) apply(zoom * 1.1);
    else if (zoomOut) apply(zoom / 1.1);
    else apply(1);
  });
}
