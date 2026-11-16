"""Deterministic recovery verdicts and evidence-backed handovers."""

import json


def load_contract(text):
    data = json.loads(text)
    required = ("journey", "allowed_actions", "success_signal", "safety_signals", "protected_records")
    missing = [key for key in required if key not in data]
    if missing or not isinstance(data["allowed_actions"], list):
        raise ValueError("contract is missing required fields")
    return data


def evidence_value(evidence, key):
    for item in evidence:
        if item.get("signal") == key and "value" in item:
            return item["value"]
    return None


def evaluate(contract, evidence, action):
    """Return recovered, failed, incomplete, unsafe, or handover.

    Missing evidence is never recovered. An action outside the contract goes to
    the on-call owner rather than being guessed or executed.
    """
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a list")
    events = []
    if action not in contract["allowed_actions"]:
        events.append({"event": "handover", "reason": "action not allowlisted"})
        return _report("handover", contract, action, events)
    if any(evidence_value(evidence, key) is False for key in contract["safety_signals"]):
        events.append({"event": "unsafe", "reason": "safety signal failed"})
        return _report("unsafe", contract, action, events)
    protected = evidence_value(evidence, contract["protected_records"])
    if protected is False:
        events.append({"event": "failed", "reason": "protected records changed"})
        return _report("failed", contract, action, events)
    success = evidence_value(evidence, contract["success_signal"])
    if success is None or protected is None:
        events.append({"event": "incomplete", "reason": "required evidence missing"})
        return _report("incomplete", contract, action, events)
    if success is not True:
        events.append({"event": "failed", "reason": "journey did not recover"})
        return _report("failed", contract, action, events)
    events.append({"event": "recovered", "reason": "journey and protected records verified"})
    return _report("recovered", contract, action, events)


def _report(verdict, contract, action, events):
    return {
        "journey": contract["journey"],
        "action": action,
        "verdict": verdict,
        "owner": contract.get("owner", "oncall"),
        "events": events,
    }
