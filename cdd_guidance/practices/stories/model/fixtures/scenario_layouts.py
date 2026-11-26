"""Two stories, Pay For Order and Cancel Order of the sub-epic Pay, written in every layout a project keeps its
scenarios in: one markdown file per story, a sub-epic's markdown file holding both, the story map alone, story tests in
Python or TypeScript alone, and markdown beside a story test in Python or TypeScript, which writes Pay by card again and
Pay with a voucher only. Each layout is a map of file paths, from the project's root, to their text."""

# The story tests in code, in the sub-epic's folder of story_tests.
PYTHON_STORY_TEST = "story_tests/check-out/pay/pay_story.test.py"
TYPESCRIPT_STORY_TEST = "story_tests/check-out/pay/pay.story.shared.ts"

MAP = ".context/story-map.md"
MAP_TEXT = "# Story Map\n\n# (E) Check Out\n## (E) Pay\n### (S) Shopper --> Pay For Order\n### (S) Shopper --> Cancel Order\n"
# A story map written as headings and bullets lists each story's scenarios under it.
MAP_LISTING_SCENARIOS = "# Check Out\n\n## Pay\n\n- Pay For Order\n  - Pay by card\n- Cancel Order\n  - Cancel an open order\n"

PAY_SCENARIO = "#### Scenario: Pay by card\n\n*Given* a cart\n*When* the Shopper pays by card\n*Then* the order is paid\n"
CANCEL_SCENARIO = "#### Scenario: Cancel an open order\n\n*Given* an open order\n*When* the Shopper cancels it\n*Then* the order is cancelled\n"

PAY_FILE = "story_tests/check-out/pay/pay-for-order/pay_for_order_story.test.md"
CANCEL_FILE = "story_tests/check-out/pay/cancel-order/cancel_order_story.test.md"
ONE_STORY_PER_FILE = {
    MAP: MAP_TEXT,
    PAY_FILE: f"# Story: Pay For Order\n\n{PAY_SCENARIO}",
    CANCEL_FILE: f"# Story: Cancel Order\n\n{CANCEL_SCENARIO}",
}

SUB_EPIC_FILE = "story_tests/check-out/pay/pay_story.test.md"
SUB_EPIC_FILE_HOLDING_BOTH = {
    MAP: MAP_TEXT,
    SUB_EPIC_FILE: f"# Sub-epic: Pay\n\n## Story: Pay For Order\n\n{PAY_SCENARIO}\n## Story: Cancel Order\n\n{CANCEL_SCENARIO}",
}

PYTHON_PAY = '''\
from story_test import given, scenario, story, then, when

with story("Pay For Order"):
    with scenario("Pay by card"):
        with given("a cart"):
            cart = Cart()
        with when("the Shopper pays by card"):
            cart.pay_by_card()
        with then("the order is paid"):
            assert cart.paid
'''
PYTHON_VOUCHER = '''
    with scenario("Pay with a voucher"):
        with given("a cart"):
            cart = Cart()
        with when("the Shopper pays with a voucher"):
            cart.pay_with_voucher()
        with then("the order is paid"):
            assert cart.paid
'''
PYTHON_CANCEL = '''
with story("Cancel Order"):
    with scenario("Cancel an open order"):
        with given("an open order"):
            order = Order()
        with when("the Shopper cancels it"):
            order.cancel()
        with then("the order is cancelled"):
            assert order.cancelled
'''

TYPESCRIPT_PAY = """\
import { scenario, shareStory } from 'test-utils/story-test/story-test';

shareStory('Pay For Order', () => {
  scenario('Pay by card', ({ given, when, then }) => {
    given('a cart', () => { cart = new Cart(); });
    when('the Shopper pays by card', () => { cart.payByCard(); });
    then('the order is paid', () => { expect(cart.paid).toBe(true); });
  });
"""
TYPESCRIPT_VOUCHER = """
  scenario('Pay with a voucher', ({ given, when, then }) => {
    given('a cart', () => { cart = new Cart(); });
    when('the Shopper pays with a voucher', () => { cart.payWithVoucher(); });
    then('the order is paid', () => { expect(cart.paid).toBe(true); });
  });
"""
TYPESCRIPT_CANCEL = """
shareStory('Cancel Order', () => {
  scenario('Cancel an open order', ({ given, when, then }) => {
    given('an open order', () => { order = new Order(); });
    when('the Shopper cancels it', () => { order.cancel(); });
    then('the order is cancelled', () => { expect(order.cancelled).toBe(true); });
  });
});
"""

PYTHON_ONLY = {PYTHON_STORY_TEST: PYTHON_PAY + PYTHON_CANCEL}
TYPESCRIPT_ONLY = {TYPESCRIPT_STORY_TEST: TYPESCRIPT_PAY + "});\n" + TYPESCRIPT_CANCEL}
MARKDOWN_BESIDE_PYTHON = {**SUB_EPIC_FILE_HOLDING_BOTH, PYTHON_STORY_TEST: PYTHON_PAY + PYTHON_VOUCHER}
MARKDOWN_BESIDE_TYPESCRIPT = {**ONE_STORY_PER_FILE, TYPESCRIPT_STORY_TEST: TYPESCRIPT_PAY + TYPESCRIPT_VOUCHER + "});\n"}

STORIES = [
    ("Pay For Order", "Pay by card", ["given a cart", "when the Shopper pays by card", "then the order is paid"]),
    ("Cancel Order", "Cancel an open order", ["given an open order", "when the Shopper cancels it", "then the order is cancelled"]),
]
ONLY_IN_CODE = ("Pay For Order", "Pay with a voucher", ["given a cart", "when the Shopper pays with a voucher", "then the order is paid"])

# Each layout where markdown, one file per story or a sub-epic's file, and a story test in code both write Pay For Order.
ONE_STORY_PER_FILE_BESIDE_PYTHON = {**ONE_STORY_PER_FILE, PYTHON_STORY_TEST: PYTHON_PAY + PYTHON_VOUCHER}
SUB_EPIC_FILE_BESIDE_TYPESCRIPT = {**SUB_EPIC_FILE_HOLDING_BOTH, TYPESCRIPT_STORY_TEST: TYPESCRIPT_PAY + TYPESCRIPT_VOUCHER + "});\n"}
