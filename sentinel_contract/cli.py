"""Read one contract and one evidence file, then print a verdict."""

import argparse
import json
import sys

from .core import evaluate, load_contract


def main(argv=None):
    parser = argparse.ArgumentParser(prog="sentinel")
    parser.add_argument("contract")
    parser.add_argument("evidence")
    parser.add_argument("--action", required=True)
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    try:
        contract = load_contract(open(args.contract, encoding="utf-8").read())
        evidence = json.load(open(args.evidence, encoding="utf-8"))
        report = evaluate(contract, evidence, args.action)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2)
    if args.report:
        open(args.report, "w", encoding="utf-8").write(text + "\n")
    print(report["verdict"])
    return 0 if report["verdict"] == "recovered" else 1


if __name__ == "__main__":
    raise SystemExit(main())
