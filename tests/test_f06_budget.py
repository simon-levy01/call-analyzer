from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import time

import pytest

from conversation_copilot.interpretation import (
    BudgetLimits, UsageLedger, UsageRecord, LUNA_MODEL, InterpretationBudgetExceeded,
    InterpretationUnavailable, cloud_work, conservative_request_cost, f06_structured_request,
)
from conversation_copilot.memory import SummaryOutput


def charge(ledger, amount):
    reservation = ledger.reserve(LUNA_MODEL, 1, max_output_tokens=1)
    ledger.complete(reservation, UsageRecord(LUNA_MODEL, "none", 0, 0, 0, 0, 0, amount))


def test_pre_dispatch_validation_exception_releases_reservation():
    import sqlite3
    ledger = UsageLedger()
    checks = []
    def current():
        checks.append(True)
        if len(checks) == 2:
            raise sqlite3.OperationalError("database is locked")
        return True
    with pytest.raises(sqlite3.OperationalError):
        f06_structured_request(SummaryOutput, {}, "test", ledger=ledger, client=object(),
            input_limit=2500, output_limit=600, is_current=current)
    assert ledger.committed_dollars == ledger.total_dollars == 0


def test_live_reservation_equality_stop_and_post_call_reserve():
    ledger = UsageLedger(BudgetLimits(warning_dollars=.15, hard_dollars=.35))
    maximum = conservative_request_cost(LUNA_MODEL, 3000, max_output_tokens=1200)
    charge(ledger, .27 - maximum)
    last = ledger.reserve(LUNA_MODEL, 3000, max_output_tokens=1200, live=True)
    assert ledger.committed_dollars == pytest.approx(.27)
    with pytest.raises(InterpretationBudgetExceeded):
        ledger.reserve(LUNA_MODEL, 1, max_output_tokens=1, live=True)
    ledger.release(last)
    ledger.stopped = True
    with pytest.raises(InterpretationBudgetExceeded):
        ledger.reserve(LUNA_MODEL, 1, max_output_tokens=1, live=True)
    post = ledger.reserve(LUNA_MODEL, 6000, max_output_tokens=1600)
    assert ledger.committed_dollars <= .35 and ledger.warning_reached
    ledger.release(post)


def test_uncertain_billing_and_stale_request_do_not_retry_or_escape_allowance():
    ledger = UsageLedger(BudgetLimits(warning_dollars=.10, hard_dollars=.13))
    calls = []
    def parse(**kwargs):
        calls.append(kwargs)
        raise TimeoutError("uncertain")
    client = SimpleNamespace(responses=SimpleNamespace(parse=parse))
    with pytest.raises(TimeoutError):
        f06_structured_request(SummaryOutput, {}, "test", ledger=ledger, client=client, input_limit=2500, output_limit=600, answer_limit=.04)
    assert len(calls) == 1 and ledger.total_dollars > 0
    charged = ledger.total_dollars
    with pytest.raises(InterpretationUnavailable):
        f06_structured_request(SummaryOutput, {}, "test", ledger=ledger, client=client, input_limit=2500, output_limit=600, is_current=lambda: False)
    assert len(calls) == 1 and ledger.total_dollars == charged
    charge(ledger, .13 - charged)
    with pytest.raises(InterpretationBudgetExceeded):
        f06_structured_request(SummaryOutput, {}, "test", ledger=ledger, client=client, input_limit=2500, output_limit=600, answer_limit=.04)
    assert len(calls) == 1


def test_explicit_cloud_work_precedes_waiting_background_work():
    order = []
    def work(priority):
        with cloud_work(priority):
            order.append(priority)
    with ThreadPoolExecutor(max_workers=2) as pool:
        with cloud_work(2):
            background = pool.submit(work, 3)
            explicit = pool.submit(work, 0)
            time.sleep(.05)
            assert not order
        background.result(timeout=2)
        explicit.result(timeout=2)
    assert order == [0, 3]
