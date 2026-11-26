"""Heavy mamba spec: a small project's production view bundled for the canvas with esbuild, for real, then run in Node
the way the canvas runs it. Its stylesheet is scoped to the screen's frame, a request the view makes is answered by
the project's canvas route from the objects the scenario bound, a page it leaves to moves the explorer to that page's
story, and the canvas walk draws the mounted screen with what the scenario bound. Heavy: runs esbuild and Node."""

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.practices.ux.model.claude_design.mounted_view import MountedViewBundle, MountedViewMarkup
from cdd_guidance.practices.ux.model.claude_design.story_screen import StoryScreen

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[4]
# An esbuild the repository already installs for one of its apps; the throwaway project borrows its node_modules.
_NODE_MODULES = next(path for path in (_REPO / "harness" / "graph" / "app" / "node_modules",
                                       _REPO / "cdd_guidance" / "practices" / "stories" / "app" / "node_modules")
                     if (path / "esbuild").is_dir())

ORDER_VIEW = """
import { useEffect, useState } from 'react';
import './order.css';

export async function loadOrder(): Promise<{ plan: string }> {
  return (await fetch('/api/order')).json();
}

export function OrderView({ order }: { order: { plan: string } }) {
  const [shown, setShown] = useState(order);
  useEffect(() => { void loadOrder().then(setShown); }, [order]);
  return (
    <main className="plan">
      <p>Plan {shown.plan}</p>
      <button type="button" onClick={() => window.location.assign('/sign-up')}>Continue</button>
    </main>
  );
}
"""

ORDER_CSS = """
:root { --brand: #f00; }
body { margin: 0; }
.plan { width: 50vw; }
@media (min-width: 600px) { .plan { color: red; } }
@media (prefers-reduced-motion: reduce) { .plan { transition: none; } }
@font-face { font-family: Shop; src: url("fonts/missing.woff2"); }
"""

CANVAS_VIEWS = """
import { OrderView } from '@src/order/order-view';

type Bound = { order?: { plan: string } };

export function OrderScreen({ bound }: { bound: Bound }) {
  return <OrderView order={bound.order ?? { plan: 'none' }} />;
}

export const canvasRoutes = {
  'GET /api/order': ({ bound }: { bound: Bound }) => ({ plan: bound.order?.plan }),
  'POST /api/order/cancel': () => { throw Object.assign(new Error('The order is placed.'), { status: 400 }); },
};

export const canvasNavigation = { '/sign-up/': 'Create Credentials' };
"""

# The canvas's React for the run: elements as plain objects, enough to mount one screen.
RUN = """
const fs = require('fs');
const vm = require('vm');
const window = { React: { createElement: (type, props, ...children) => ({ type, props: Object.assign({}, props, { children }) }), Fragment: 'fragment' }, console, URL };
window.window = window; window.globalThis = window;
vm.createContext(window);
vm.runInContext(fs.readFileSync(BUNDLE, 'utf8'), window);
const moves = [];
const mounted = window.Paradise.CanvasMount({ view: 'OrderScreen', bound: { order: { plan: 'Ace' } }, position: {}, go: (story) => moves.push(story) });
(async () => {
  const order = await (await vm.runInContext('__canvasFetch', window)('/api/order')).json();
  const refused = await vm.runInContext('__canvasFetch', window)('/api/order/cancel', { method: 'POST', body: '{}' });
  const missing = await vm.runInContext('__canvasFetch', window)('/api/nothing');
  vm.runInContext('__canvasLocation', window).assign('/sign-up');
  vm.runInContext('__canvasLocation', window).assign('/nowhere');
  const unknown = window.Paradise.CanvasMount({ view: 'NoSuchScreen', bound: { order: { plan: 'Ace' } } });
  const waiting = window.Paradise.CanvasMount({ view: 'OrderScreen', bound: {}, repositories: {} });
  console.log(JSON.stringify({ mountedType: mounted.type.name, mountedBound: mounted.props.bound, order,
    refused: [refused.status, await refused.json()], missing: missing.status, moves, unknown: unknown.props.children,
    waiting: [typeof waiting.type === 'string' ? waiting.type : waiting.type.name, waiting.props.children] }));
})();
"""

FIXTURES = """
var CanvasFixtures = {
  scenarios: function () { return ['Order the Ace plan']; },
  actions: function () { return 0; },
  examples: {},
  pasteFor: function () { return null; },
  bindings: function () { return { order: { plan: 'Ace' } }; },
  load: function () { return Promise.resolve({ planRepository: {} }); }
};
"""


def link_folder(link: Path, target: Path) -> None:
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


def write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


def node(code: str, cwd: Path) -> str:
    return subprocess.run([shutil.which("node") or "node", "-e", code], cwd=cwd, capture_output=True, text=True, check=True,
                          encoding="utf-8").stdout


with description("a production view mounted on the canvas, for real") as self:
    with before.all:
        self.folder = tempfile.mkdtemp(prefix="cdd-mounted-view-")
        root = Path(self.folder)
        link_folder(root / "node_modules", _NODE_MODULES)
        write(root, "tsconfig.json", json.dumps({"compilerOptions": {"jsx": "react-jsx", "baseUrl": ".", "paths": {"@src/*": ["src/*"]}}}))
        write(root, "src/order/order-view.tsx", ORDER_VIEW)
        write(root, "src/order/order.css", ORDER_CSS)
        write(root, "packages/shop/canvas-views.tsx", CANVAS_VIEWS)
        self.project = root / "canvas" / "project"
        self.bundle = MountedViewBundle(project_root=root, entry="packages/shop/canvas-views.tsx", folder="shop", namespace="Paradise")
        screen = StoryScreen(title="Order Plan", story="Order Plan", markup=MountedViewMarkup("OrderScreen", self.bundle),
                             positions={"Order the Ace plan": [{}]})
        self.files = screen.markup.copy_files(self.project)
        write(self.project, "screens/order-plan.dc.html", screen.html)
        write(self.project, "fixtures/canvas-fixtures.js", FIXTURES)
        self.script = (self.project / "ds" / "shop" / "shop.js").read_text(encoding="utf-8")
        # The stylesheet as esbuild writes it, its spacing taken out, so the checks read the rules alone.
        self.css = re.sub(r"\s+", "", (self.project / "ds" / "shop" / "shop.css").read_text(encoding="utf-8"))
        run = RUN.replace("BUNDLE", json.dumps(str(self.project / "ds" / "shop" / "shop.js")))
        self.run = json.loads(node(run, root))

    with after.all:
        # Remove the link first, so the cleanup never reaches into the repository's own node_modules.
        link = Path(self.folder) / "node_modules"
        if os.name == "nt":
            os.rmdir(link)
        else:
            os.unlink(link)
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("bundling the project's view entry"):
        with it("should write the bundle into the version's design-system folder"):
            expect(sorted(path.name for path in self.files)).to(equal(["shop.css", "shop.js"]))

        with it("should declare CanvasMount as the bundle's one component"):
            expect(self.script).to(contain('/* @ds-bundle: {"format":4,"namespace":"Paradise","components":[{"name":"CanvasMount"}]} */'))

        with it("should point the views' fetch and window.location at the canvas's stand-ins"):
            expect((self.script.count("globalThis.__canvasFetch)(\"/api/order\")"), self.script.count("globalThis.__canvasLocation.assign"))).to(equal((1, 1)))

    with context("scoping the product's stylesheet to the mounted view"):
        with it("should put the page's tokens and base rules on the mounted view's own wrapper, not on every frame"):
            expect((self.css.count(".canvas-mount{--brand:#f00;"), self.css.count(".canvas-mount{margin:0;"))).to(equal((1, 1)))

        with it("should turn a width query into a container query on the frame"):
            expect(self.css).to(contain("@containercanvas-screen(min-width:600px)"))

        with it("should keep a media query that asks about anything but size"):
            expect(self.css).to(contain("@media(prefers-reduced-motion:reduce)"))

        with it("should measure the window's width as the frame's"):
            expect(self.css).to(contain(".canvas-mount.plan{width:50cqw;"))

        with it("should keep the frame's fixed children inside it"):
            expect(self.css).to(contain(".canvas-screen{container:canvas-screen/inline-size;contain:layoutpaint;"))

        with it("should draw without a font the project does not have"):
            expect(self.css).to(contain("src:url(fonts/missing.woff2)"))

    with context("running on the canvas"):
        with it("should mount the project's view by name with the objects the scenario bound"):
            expect((self.run["mountedType"], self.run["mountedBound"])).to(equal(("OrderScreen", {"order": {"plan": "Ace"}})))

        with it("should answer the view's request from the bound objects through the project's canvas route"):
            expect(self.run["order"]).to(equal({"plan": "Ace"}))

        with it("should answer a refusal with its status and the domain's message"):
            expect(self.run["refused"]).to(equal([400, {"message": "The order is placed."}]))

        with it("should answer a request no canvas route names with 404"):
            expect(self.run["missing"]).to(equal(404))

        with it("should move the explorer to the story of the page the view leaves to, and nowhere for a page it does not know"):
            expect(self.run["moves"]).to(equal(["Create Credentials"]))

        with it("should wait for the scenario's fixture before mounting the view, so the view's first request finds the repositories filled"):
            expect(self.run["waiting"]).to(equal(["p", ["Loading the scenario…"]]))

        with it("should say so when the screen names a view the bundle does not have"):
            expect(self.run["unknown"]).to(equal(["The canvas bundle has no view NoSuchScreen."]))

    with context("walked at the scenario's step group"):
        with it("should draw the mounted view with what the scenario bound"):
            job = {"jobs": [{"artboard": str(self.project / "screens" / "order-plan.dc.html"),
                             "props": {"story": "Order Plan", "scenario": "Order the Ace plan", "stepIndex": 0, "step": ""}}]}
            walked = subprocess.run([shutil.which("node") or "node", str(_HERE / "screen_render.cjs")], input=json.dumps(job),
                                    capture_output=True, text=True, check=True, encoding="utf-8")
            expect(json.loads(walked.stdout)[0].get("text", "")).to(contain("Plan Ace"))
