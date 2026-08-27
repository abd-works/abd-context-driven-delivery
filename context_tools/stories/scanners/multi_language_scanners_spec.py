"""Cross-language Stories scanners - same rules across py / ts / js / java channels.

Architecture (mirrors Clean Engineering):
  language channel parses file -> canonical model fields
  scanner reads model only - never language syntax
"""

import tempfile
from pathlib import Path

from expects import be_above, equal, expect
from mamba import context, description, it

from scan import ScannerCollection

_STORIES_DIR = Path(__file__).resolve().parents[1]
_DISCOVERED = ScannerCollection(_STORIES_DIR, _STORIES_DIR / "scanners").discover()

_STORY_MAP = """\
(E) Manage Orders
    (E) Place Order
        (S) Customer --> Submit Order
"""

# Tier file stubs - channels must flag unimplemented_steps / has_unimplemented_body
_TIER_FAULT = {
    "python": (
        "tests/manage-orders/place-order/submit-order/test_submit_order_server.py",
        '''
class TestSubmitOrder:
    def given_cart_ready(self):
        pass

    def test_order_accepted(self):
        # TODO implement
        raise NotImplementedError
''',
    ),
    "typescript": (
        "tests/manage-orders/place-order/submit-order/submit-order-server.test.ts",
        '''
describe('Submit Order', () => {
  const tier = {
    given: {
      'a Cart is ready': () => { /* TODO */ },
    },
    when: {
      'the Customer submits': () => { throw new Error('not implemented'); },
    },
    then: {
      'an Order is created': () => {},
    },
  };
  it('order accepted', () => {
    tier.given['a Cart is ready']();
  });
});
''',
    ),
    "javascript": (
        "tests/manage-orders/place-order/submit-order/submit-order-server.test.js",
        '''
describe('Submit Order', () => {
  const tier = {
    given: {
      'a Cart is ready': () => { /* TODO */ },
    },
    when: {
      'the Customer submits': () => { throw new Error('not implemented'); },
    },
    then: {
      'an Order is created': () => {},
    },
  };
  it('order accepted', () => {
    tier.given['a Cart is ready']();
  });
});
''',
    ),
    "java": (
        "tests/manage-orders/place-order/submit-order/SubmitOrderServerTest.java",
        '''
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class SubmitOrderServerTest {
    Map<String, Runnable> given = new HashMap<>();
    {
        given.put("a Cart is ready", () -> { /* TODO */ });
    }

    @Test
    void orderAccepted() {
        given.get("a Cart is ready").run();
    }
}
''',
    ),
}

_TIER_CLEAN = {
    "python": (
        "tests/manage-orders/place-order/submit-order/test_submit_order_server.py",
        '''
class TestSubmitOrder:
    def given_cart_ready(self):
        self.cart = {"items": 1}

    def test_order_accepted(self):
        self.given_cart_ready()
        assert self.cart["items"] == 1
''',
    ),
    "typescript": (
        "tests/manage-orders/place-order/submit-order/submit-order-server.test.ts",
        '''
describe('Submit Order', () => {
  const tier = {
    given: {
      'a Cart is ready': () => { globalThis.cart = { items: 1 }; },
    },
    when: {
      'the Customer submits': () => { globalThis.order = { status: 'placed' }; },
    },
    then: {
      'an Order is created': () => { expect(globalThis.order.status).toBe('placed'); },
    },
  };
  it('order accepted', () => {
    tier.given['a Cart is ready']();
    tier.when['the Customer submits']();
    tier.then['an Order is created']();
  });
});
''',
    ),
    "javascript": (
        "tests/manage-orders/place-order/submit-order/submit-order-server.test.js",
        '''
describe('Submit Order', () => {
  const tier = {
    given: {
      'a Cart is ready': () => { global.cart = { items: 1 }; },
    },
    when: {
      'the Customer submits': () => { global.order = { status: 'placed' }; },
    },
    then: {
      'an Order is created': () => { expect(global.order.status).toBe('placed'); },
    },
  };
  it('order accepted', () => {
    tier.given['a Cart is ready']();
    tier.when['the Customer submits']();
    tier.then['an Order is created']();
  });
});
''',
    ),
    "java": (
        "tests/manage-orders/place-order/submit-order/SubmitOrderServerTest.java",
        '''
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class SubmitOrderServerTest {
    int items = 0;
    Map<String, Runnable> given = new HashMap<>();
    {
        given.put("a Cart is ready", () -> { items = 1; });
    }

    @Test
    void orderAccepted() {
        given.get("a Cart is ready").run();
        assertEquals(1, items);
    }
}
''',
    ),
}


_KEEP_ALIVE: list = []


def _write_workspace(files: dict) -> Path:
    temp = tempfile.TemporaryDirectory()
    _KEEP_ALIVE.append(temp)
    root = Path(temp.name)
    (root / "story-map.md").write_text(_STORY_MAP, encoding="utf-8")
    for rel, body in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body.strip() + "\n", encoding="utf-8")
    return root


def _scan(rule: str, root: Path):
    scanner_class = _DISCOVERED[rule]
    return scanner_class(rule).scan(root, list(root.rglob("*")))


def _assert_tier_pair(lang: str):
    fault_path, fault_body = _TIER_FAULT[lang]
    clean_path, clean_body = _TIER_CLEAN[lang]
    fail_root = _write_workspace({fault_path: fault_body})
    pass_root = _write_workspace({clean_path: clean_body})
    fail = _scan("tier-bodies-implemented", fail_root)
    pass_ = _scan("tier-bodies-implemented", pass_root)
    expect(len(fail)).to(be_above(0))
    expect(len(pass_)).to(equal(0))
    for v in fail:
        expect(v.rule).to(equal("tier-bodies-implemented"))


with description("Multi-language Stories scanners"):
    with context("tier-bodies-implemented across language channels"):
        with it("should flag stubs and accept real bodies for python"):
            _assert_tier_pair("python")

        with it("should flag stubs and accept real bodies for typescript"):
            _assert_tier_pair("typescript")

        with it("should flag stubs and accept real bodies for javascript"):
            _assert_tier_pair("javascript")

        with it("should flag stubs and accept real bodies for java"):
            _assert_tier_pair("java")

    with context("verb-noun-format on the markdown channel"):
        with it("should accept verb-noun story names from any workspace"):
            root = _write_workspace({})
            violations = [
                v for v in _scan("verb-noun-format", root)
                if v.severity in ("error", "warning")
            ]
            expect(violations).to(equal([]))

        with it("should flag actor-led story names"):
            root = _write_workspace({})
            (root / "story-map.md").write_text(
                "(E) Manage Orders\n"
                "    (E) Place Order\n"
                "        (S) Customer --> Customer Submit Order\n",
                encoding="utf-8",
            )
            fail = [
                v for v in _scan("verb-noun-format", root)
                if "actor" in v.message.lower() or "Customer Submit" in v.message
            ]
            expect(len(fail)).to(be_above(0))
