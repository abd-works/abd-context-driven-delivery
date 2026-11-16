/** Zooms the mockup surface inside its pane, from the zoom buttons, ctrl/cmd + wheel, and ctrl/cmd + keys. */
class FlowZoom {
  static SMALLEST = 0.25;
  static LARGEST = 3;
  /** Each zoom in or out scales by this much. */
  static STEP = 1.1;
  static PERCENT = 100;

  constructor(pane, surface) {
    this.pane = pane;
    this.surface = surface;
    this.readout = pane.querySelector('[data-flow-zoom="reset"]');
    this.zoom = 1;
  }

  listen() {
    this.pane.querySelector('[data-flow-zoom="in"]')?.addEventListener("click", () => this.zoomIn());
    this.pane.querySelector('[data-flow-zoom="out"]')?.addEventListener("click", () => this.zoomOut());
    this.readout?.addEventListener("click", () => this.apply(1));
    this.pane.addEventListener("wheel", (event) => this.onWheel(event), { passive: false });
    document.querySelector("#explorer-frame")?.addEventListener(
      "wheel",
      (event) => {
        if (event.ctrlKey || event.metaKey) event.preventDefault();
      },
      { passive: false },
    );
    document.addEventListener("keydown", (event) => this.onKey(event));
    return this;
  }

  zoomIn() {
    this.apply(this.zoom * FlowZoom.STEP);
  }

  zoomOut() {
    this.apply(this.zoom / FlowZoom.STEP);
  }

  onWheel(event) {
    if (!event.ctrlKey && !event.metaKey) return;
    event.preventDefault();
    const factor = event.deltaY < 0 ? FlowZoom.STEP : 1 / FlowZoom.STEP;
    this.apply(this.zoom * factor, { x: event.clientX, y: event.clientY });
  }

  onKey(event) {
    if (!(event.ctrlKey || event.metaKey) || event.altKey) return;
    const zoomIn = event.key === "+" || event.key === "=";
    const zoomOut = event.key === "-" || event.key === "_";
    const reset = event.key === "0";
    if (!zoomIn && !zoomOut && !reset) return;
    event.preventDefault();
    if (event.target.closest?.("#explorer-frame")) return;
    if (zoomIn) this.zoomIn();
    else if (zoomOut) this.zoomOut();
    else this.apply(1);
  }

  /** Zoom to `next`, keeping the content under `point` (or the pane's centre) where it was. */
  apply(next, point) {
    const previous = this.zoom;
    const rect = this.pane.getBoundingClientRect();
    const localX = point ? point.x - rect.left : this.pane.clientWidth / 2;
    const localY = point ? point.y - rect.top : this.pane.clientHeight / 2;
    const contentX = this.pane.scrollLeft + localX;
    const contentY = this.pane.scrollTop + localY;
    this.zoom = this.clamped(next);
    this.surface.style.zoom = String(this.zoom);
    if (previous) {
      this.pane.scrollLeft = contentX * (this.zoom / previous) - localX;
      this.pane.scrollTop = contentY * (this.zoom / previous) - localY;
    }
    if (this.readout) this.readout.textContent = `${Math.round(this.zoom * FlowZoom.PERCENT)}%`;
  }

  /** Keep the zoom between the smallest and largest, rounded to a whole percent. */
  clamped(zoom) {
    const rounded = Math.round(zoom * FlowZoom.PERCENT) / FlowZoom.PERCENT;
    return Math.min(FlowZoom.LARGEST, Math.max(FlowZoom.SMALLEST, rounded));
  }
}

function bindFlowZoom(pane, surface) {
  if (!pane || !surface) return;
  new FlowZoom(pane, surface).listen();
}
