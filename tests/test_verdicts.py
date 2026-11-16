import json
import unittest
from pathlib import Path

from sentinel_contract.core import evaluate, load_contract


ROOT = Path(__file__).parents[1]


class VerdictTests(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract((ROOT / "examples/checkout.json").read_text())

    def test_recovered_requires_every_promise(self):
        evidence = json.loads((ROOT / "examples/recovered.json").read_text())
        self.assertEqual(evaluate(self.contract, evidence, "restart-payment")["verdict"], "recovered")

    def test_missing_evidence_is_not_recovery(self):
        report = evaluate(self.contract, [], "restart-payment")
        self.assertEqual(report["verdict"], "incomplete")
        self.assertEqual(report["owner"], "payments-oncall")

    def test_unknown_action_hands_over(self):
        self.assertEqual(evaluate(self.contract, [], "scale-database")["verdict"], "handover")

    def test_safety_failure_is_unsafe(self):
        evidence = [{"signal": "payment.invalid_rejected", "value": False}]
        self.assertEqual(evaluate(self.contract, evidence, "restart-payment")["verdict"], "unsafe")

    def test_changed_records_fail(self):
        evidence = [{"signal": "checkout.completed", "value": True}, {"signal": "ledger.unchanged", "value": False}]
        self.assertEqual(evaluate(self.contract, evidence, "restart-payment")["verdict"], "failed")

    def test_failed_journey_is_not_recovery(self):
        evidence = [
            {"signal": "checkout.completed", "value": False},
            {"signal": "payment.invalid_rejected", "value": True},
            {"signal": "ledger.unchanged", "value": True},
        ]
        report = evaluate(self.contract, evidence, "restart-payment")
        self.assertEqual(report["verdict"], "failed")
        self.assertEqual(report["events"][0]["reason"], "journey did not recover")


if __name__ == "__main__":
    unittest.main()
