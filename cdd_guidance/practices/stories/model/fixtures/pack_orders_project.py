"""The Pack Orders project the shared story-test behaviours read: one small story map, written once as story tests in
each language Stories writes them in (Python, TypeScript, JavaScript) and once as markdown scenarios, with the code the
story tests call. Every writing holds the same stories, scenarios, steps and examples, so one set of examples checks
the graph each of them gives."""

from __future__ import annotations

import functools
import re
import tempfile
from pathlib import Path

import cdd_guidance.practices  # noqa: F401 - registers the practices a graph holds
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryModel
from cdd_guidance.practices.stories.stories import Stories
from harness.graph.graph import Graph

TESTS_ROOT = "story_tests"
_STEP_TYPES = ("Given", "When", "Then", "Step")
_PRACTICES = ("stories", "clean_engineering")

_STORY_MAP = """\
# Story Map — Shop

# (E) Fulfil Order

## (E) Pack Orders

### (S) Shop Clerk --> Pack Order
### (S) Shop Clerk --> Cancel Order
"""

_ORDER_PYTHON = '''\
class OrderNotPaid(Exception):
    pass


class Order:
    def __init__(self, number: str, paid: bool) -> None:
        self.number = number
        self.paid = paid
        self.status = "submitted"

    def pack(self) -> None:
        if not self.paid:
            raise OrderNotPaid(f"order {self.number} is not paid")
        self.status = "packed"

    def cancel(self) -> None:
        self.status = "cancelled"


class OrderRepository:
    def __init__(self) -> None:
        self.orders = {}

    def create(self, order: Order) -> Order:
        self.orders[order.number] = order
        return order

    def load(self, number: str) -> Order:
        return self.orders[number]
'''

_EXAMPLES_PYTHON = '''\
"""Order examples the Pack Orders stories share. Seed state: orders the Shop already keeps."""

from src.shop.order import Order


def paid_order() -> Order:
    return Order("1001", True)


def unpaid_order() -> Order:
    return Order("1002", False)
'''

_STORY_TEST_PYTHON = '''\
from expects import equal, expect, raise_error

from story_test import and_, given, scenario, story, then, when
from src.shop.order import OrderNotPaid, OrderRepository
from src.shop.order_examples import paid_order, unpaid_order

# Epic: Fulfil Order

# Story: Pack Order
# Actor: Shop Clerk
with story("Pack Order"):
    with scenario("Pack a paid order"):
        with given("the Shop keeps Order paid order"):
            orders = OrderRepository()
            orders.create(paid_order())
        with when("the Shop Clerk packs the Order"):
            orders.load("1001").pack()
        with then("the Order paid order has status packed"):
            expect(orders.load("1001").status).to(equal("packed"))
    with scenario("Refuse to pack an unpaid order"):
        with given("the Shop keeps Order unpaid order"):
            orders = OrderRepository()
            orders.create(unpaid_order())
        with when("the Shop Clerk packs the Order"):
            packing = lambda: orders.load("1002").pack()
        with then("the Shop refuses with \\"order 1002 is not paid\\""):
            expect(packing).to(raise_error(OrderNotPaid, "order 1002 is not paid"))
        with and_("the Order unpaid order keeps status submitted"):
            expect(orders.load("1002").status).to(equal("submitted"))
'''

_SHARED_PYTHON = '''\
"""Pack Orders: the shared scenarios the Python tiers replay."""

from expects import equal, expect

from src.shop.order import OrderRepository
from src.shop.order_examples import paid_order
from story_tests.shared_stories import SharedStories

shared_stories = SharedStories("Pack Orders")


@shared_stories.scenario("Cancel Order", "Cancel a paid order")
def _(s):
    @s.given("the Shop keeps Order paid order")
    def _(world):
        world.orders = OrderRepository()
        world.orders.create(paid_order())

    @s.when("the Shop Clerk cancels the Order")
    def _(world):
        world.orders.load("1001").cancel()

    @s.then("the Order paid order has status cancelled")
    def _(world):
        expect(world.orders.load("1001").status).to(equal("cancelled"))
'''

_DOMAIN_TIER_PYTHON = '''\
"""Pack Orders at the domain tier: the shared scenarios on Order itself."""

from story_tests.shared_stories import DomainTier, load_shared, replay

globals().update(replay(load_shared(__file__, "pack-orders"), DomainTier()))
'''

# The script languages write one text; TypeScript adds its types where {types} stands, and each names the modules it
# imports with its own extension where {module} stands.
_ORDER_SCRIPT = """\
export class OrderNotPaid extends Error {}

export class Order {
  status = "submitted";

  constructor(number, paid) {
    this.number = number;
    this.paid = paid;
  }

  pack() {
    if (!this.paid) {
      throw new OrderNotPaid(`order ${this.number} is not paid`);
    }
    this.status = "packed";
  }

  cancel() {
    this.status = "cancelled";
  }
}

export class OrderRepository {
  orders = new Map();

  create(order) {
    this.orders.set(order.number, order);
    return order;
  }

  load(number) {
    return this.orders.get(number);
  }
}
"""

_EXAMPLES_SCRIPT = """\
/** Order examples the Pack Orders stories share. Seed state: orders the Shop already keeps. */

import { Order } from "../../../src/shop/order{module}";

export const paidOrder = new Order("1001", true);
export const unpaidOrder = new Order("1002", false);
"""

_STORY_TEST_SCRIPT = """\
/**
 * Epic: Fulfil Order
 */

import { expect } from "vitest";
import { scenario, story } from "../../../story-test{module}";
import { OrderNotPaid, OrderRepository } from "../../../../src/shop/order{module}";
import { paidOrder, unpaidOrder } from "../../examples/order.examples{module}";

/**
 * Story: Pack Order
 * Actor: Shop Clerk
 */
story("Pack Order", () => {
  scenario("Pack a paid order", ({ given, when, then }) => {
    const orders = new OrderRepository();
    given("the Shop keeps Order paid order", () => {
      orders.create(paidOrder);
    });
    when("the Shop Clerk packs the Order", () => {
      orders.load("1001").pack();
    });
    then("the Order paid order has status packed", () => {
      expect(orders.load("1001").status).toBe("packed");
    });
  });

  scenario("Refuse to pack an unpaid order", ({ given, when, then }) => {
    const orders = new OrderRepository();
    let packing;
    given("the Shop keeps Order unpaid order", () => {
      orders.create(unpaidOrder);
    });
    when("the Shop Clerk packs the Order", () => {
      packing = () => orders.load("1002").pack();
    });
    then("the Shop refuses with \\"order 1002 is not paid\\"", () => {
      expect(packing).toThrow(OrderNotPaid);
    }).and("the Order unpaid order keeps status submitted", () => {
      expect(orders.load("1002").status).toBe("submitted");
    });
  });
});
"""

_SHARED_SCRIPT = """\
/** Pack Orders: the shared scenarios the tiers replay. */

import { expect } from "vitest";
import { scenario, story } from "../../story-test{module}";
import { OrderRepository } from "../../../src/shop/order{module}";
import { paidOrder } from "../examples/order.examples{module}";

export function packOrdersStories(orders) {
  story("Cancel Order", () => {
    scenario("Cancel a paid order", ({ given, when, then }) => {
      given("the Shop keeps Order paid order", () => {
        orders.create(paidOrder);
      });
      when("the Shop Clerk cancels the Order", () => {
        orders.load("1001").cancel();
      });
      then("the Order paid order has status cancelled", () => {
        expect(orders.load("1001").status).toBe("cancelled");
      });
    });
  });
}
"""

_DOMAIN_TIER_SCRIPT = """\
/** Pack Orders at the domain tier: the shared scenarios on Order itself. */

import { OrderRepository } from "../../../src/shop/order{module}";
import { packOrdersStories } from "./pack-orders.story.shared{module}";

packOrdersStories(new OrderRepository());
"""

_SCREEN_SPEC_SCRIPT = """\
/** Pack Orders in the browser: what the Shop Clerk sees on the order page. */

import { expect, test } from "@playwright/test";

test.describe("Pack Order", () => {
  test("Show a packed order", async ({ page }) => {
    await seedOrder(page, "1001");
    await page.goto("/orders/1001");
    await page.getByRole("button", { name: "Pack order" }).click();
    await expect(page.getByText("Status packed")).toBeVisible();
  });
});

async function seedOrder(page, orderNumber) {
  await page.request.post("/test/orders", { data: { orderNumber } });
}
"""

_PACK_ORDER_MARKDOWN = """\
---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Pack Order

### Examples

#### order

| order | example | number | paid |
| --- | --- | --- | --- |
| order | paid order | 1001 | yes |
| order | unpaid order | 1002 | no |

### Behaviors

#### Scenario: Pack a paid order

*Given* the Shop keeps Order paid order
*When* the Shop Clerk packs the Order
*Then* the Order paid order has status packed

#### Scenario: Refuse to pack an unpaid order

*Given* the Shop keeps Order unpaid order
*When* the Shop Clerk packs the Order
*Then* the Shop refuses with "order 1002 is not paid"
  *And* the Order unpaid order keeps status submitted
"""

_CANCEL_ORDER_MARKDOWN = """\
---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Cancel Order

### Examples

#### order

| order | example | number | paid |
| --- | --- | --- | --- |
| order | paid order | 1001 | yes |

### Behaviors

#### Scenario: Cancel a paid order

*Given* the Shop keeps Order paid order
*When* the Shop Clerk cancels the Order
*Then* the Order paid order has status cancelled
"""

_SUB_EPIC = f"{TESTS_ROOT}/fulfil-order/pack-orders"


def _script_files(extension: str, module: str) -> dict[str, str]:
    """The project's files in a script language: its file extension, and how it ends the modules it imports."""
    texts = {
        f"src/shop/order.{extension}": _ORDER_SCRIPT,
        f"{TESTS_ROOT}/fulfil-order/examples/order.examples.{extension}": _EXAMPLES_SCRIPT,
        f"{_SUB_EPIC}/pack-order/pack_order_story.test.{extension}": _STORY_TEST_SCRIPT,
        f"{_SUB_EPIC}/pack-orders.story.shared.{extension}": _SHARED_SCRIPT,
        f"{_SUB_EPIC}/pack-orders.story.domain.spec.{extension}": _DOMAIN_TIER_SCRIPT,
        f"{_SUB_EPIC}/pack-orders.story.ui.spec.{extension}": _SCREEN_SPEC_SCRIPT,
    }
    return {path: text.replace("{module}", module) for path, text in texts.items()}


_FILES = {
    "python": {
        "src/shop/order.py": _ORDER_PYTHON,
        # A Python story test imports its examples from a package Python can import, beside the code under test.
        "src/shop/order_examples.py": _EXAMPLES_PYTHON,
        f"{_SUB_EPIC}/pack-order/pack_order_story.test.py": _STORY_TEST_PYTHON,
        f"{_SUB_EPIC}/pack-orders.story.shared.py": _SHARED_PYTHON,
        f"{_SUB_EPIC}/pack-orders.story.domain.spec.py": _DOMAIN_TIER_PYTHON,
    },
    "typescript": _script_files("ts", ""),
    "javascript": _script_files("js", ".js"),
    "markdown": {
        f"{_SUB_EPIC}/pack_order_story.test.md": _PACK_ORDER_MARKDOWN,
        f"{_SUB_EPIC}/cancel_order_story.test.md": _CANCEL_ORDER_MARKDOWN,
    },
}


def _words(name: str) -> str:
    """An example's name as words, however its language spells it: paid_order, paidOrder and paid order are one."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|_", " ", name).lower()


class StoryTestProject:
    """A project of story files in a folder of its own, and the graph that read its whole working copy for Stories
    and Clean Engineering. What it answers is named as the story map names it, never as a language spells it, so the
    same questions are asked of a project written in any language. A project is made with the story map its story
    files sit under, or with none, where the story tests are the map themselves. The folder goes when the project
    does."""

    def __init__(self, format_name: str, files: dict[str, str], story_map: str = _STORY_MAP) -> None:
        self.format_name = format_name
        self.files = {**({".context/story-map.md": story_map} if story_map else {}), **files}
        self._folder = tempfile.TemporaryDirectory()
        self.root = Path(self._folder.name).resolve()
        for file, text in self.files.items():
            path = self.root / file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.graph = Graph()
        self.graph.load_working_copy(str(self.root), {key: str(self.root) for key in _PRACTICES}, force=True)
        self.stories = self.graph.practice("stories").reading.in_graph

    ## the story map the graph holds

    def story_names(self, epic: str) -> list[str]:
        """The stories directly under the epic or sub-epic called epic, in the map's order."""
        return [edge.child.name for edge in self._edges("decomposedInto", self._one(("Epic", "SubEpic"), epic)) if edge.child.type == "Story"]

    def every_story_name(self) -> list[str]:
        """Each story the graph holds, once, by name."""
        return sorted({node.name for node in self.stories.nodes("Story")})

    def scenario_names(self, story: str) -> list[str]:
        return [edge.child.name for edge in self._edges("scenarios", self._one(("Story",), story))]

    def steps(self, scenario: str) -> list[tuple]:
        """The scenario's steps in order, each as its kind, its words, and the words of the steps chained onto it."""
        steps = [edge.child for edge in self._edges("steps", self._one(("Scenario",), scenario))]
        return [(step.type, step.name, [edge.child.name for edge in self._edges("ands", step)]) for step in steps]

    def phases(self, scenario: str) -> list[str]:
        """The phase each step of the scenario saves, its chained steps after it."""
        steps = [edge.child for edge in self._edges("steps", self._one(("Scenario",), scenario))]
        return [each.get_fact("phase") for step in steps for each in (step, *(edge.child for edge in self._edges("ands", step)))]

    def example_names(self) -> list[str]:
        """Each example the graph holds, as words, once."""
        return sorted({_words(node.name) for node in self.stories.nodes("Example")})

    def observed_by(self, scenario: str, step: str) -> list[str]:
        """The examples the step of the scenario observes, as words."""
        return sorted({_words(edge.child.name) for edge in self._edges("observes", self._step(scenario, step))})

    ## the code the graph joins the story map to

    def invoked_by(self, scenario: str, step: str) -> list[str]:
        """Each operation the step of the scenario invokes, as its class and its name."""
        return sorted(f"{edge.child.get_fact('owner')}.{edge.child.name}" for edge in self._edges("invokes", self._step(scenario, step)))

    def fact(self, scenario: str, step: str, fact: str):
        return self._step(scenario, step).get_fact(fact)

    def demonstrated_by(self, example: str) -> list[str]:
        """The classes the example called example, in words, demonstrates."""
        examples = [node for node in self.stories.nodes("Example") if _words(node.name) == example]
        return sorted({edge.child.name for node in examples for edge in self._edges("demonstrates", node)})

    ## the trip to another format and back

    def taken_to(self, other: str) -> "StoryTestProject":
        """The project read back from this one's story files after they were written in the format called other and
        written again in this one's: the story map as its files give it, with no code, since no other format holds it."""
        practice = Stories()
        there = _written(practice, other, _read(practice, self.format_name, self.files))
        back = _written(practice, self.format_name, _read(practice, other, {".context/story-map.md": _STORY_MAP, **there}))
        return StoryTestProject(self.format_name, back)

    def _step(self, scenario: str, step: str):
        held = [edge.child for edge in self._edges("steps", self._one(("Scenario",), scenario))]
        held += [edge.child for each in list(held) for edge in self._edges("ands", each)]
        return next(each for each in held if each.name == step)

    def _one(self, types: tuple, name: str):
        return next(node for node in self.stories.nodes() if node.type in types and node.name == name)

    def _edges(self, kind: str, parent) -> list:
        return self.graph.edges.from_parent(kind, parent)


def _read(practice: Stories, format_name: str, files: dict[str, str]):
    """The story model the files give when read in the format called format_name."""
    if format_name == "markdown":
        folder = tempfile.TemporaryDirectory()
        for file, text in files.items():
            path = Path(folder.name) / file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return MarkdownStoryModel.from_workspace(Path(folder.name))
    adapter = practice.formats.adapter_class(format_name)(TESTS_ROOT)
    return adapter.load({file: text for file, text in files.items() if file.startswith(TESTS_ROOT)})


def _written(practice: Stories, format_name: str, model) -> dict[str, str]:
    """The files the format called format_name writes the story model as, under the project's story tests."""
    if format_name == "markdown":
        return _markdown_files(MarkdownStoryModel(model))
    return practice.formats.adapter_class(format_name)(model, tests_root=TESTS_ROOT).save()


def _markdown_files(model: MarkdownStoryModel) -> dict[str, str]:
    """One scenarios file for each story with scenarios, in its sub-epic's folder, as the scenarios fidelity saves."""
    files: dict[str, str] = {}

    def visit(epic, folder: str) -> None:
        for story in epic.stories:
            if story.scenarios:
                files[f"{folder}/{story.slug.replace('-', '_')}_story.test.md"] = story.scenarios_text()
        for child in epic.epics:
            visit(child, f"{folder}/{child.slug}")

    for epic in model.epics:
        visit(epic, f"{TESTS_ROOT}/{epic.slug}")
    return files


@functools.cache
def pack_orders_in(format_name: str) -> StoryTestProject:
    """The Pack Orders project written in the format called format_name, read once however many specs ask."""
    return StoryTestProject(format_name, _FILES[format_name])


@functools.cache
def pack_orders_without_a_map(format_name: str) -> StoryTestProject:
    """The Pack Orders project written in format_name with no story map, its story tests under the project's tests
    folder: the story tests are the map."""
    files = {file.replace(f"{TESTS_ROOT}/", "tests/", 1): text for file, text in _FILES[format_name].items()}
    return StoryTestProject(format_name, files, story_map="")


@functools.cache
def pack_orders_taken(format_name: str, other: str) -> StoryTestProject:
    """The Pack Orders project written in format_name, after the trip to the format called other and back."""
    return pack_orders_in(format_name).taken_to(other)
