# sentinel-contract

A self-healing action is not recovered until its observability contract says so. Otherwise, hand it to on-call.

**TLDR.** This small Python tool reads one recovery contract and the evidence collected after an action. `restart-payment` can be recovered only when checkout succeeds, invalid input is still refused, and protected records are unchanged. Missing evidence stays incomplete. An action outside the allowlist is handed to the named on-call owner instead of being guessed.

This is a local decision tool. It does not restart infrastructure, call a model, or claim production recovery.

## Try it

```sh
python3 -m sentinel_contract.cli examples/checkout.json examples/recovered.json --action restart-payment
```

The command prints `recovered` and exits 0. These evidence files return the other verdicts:

```sh
printf '[]\n' > /tmp/none.json
python3 -m sentinel_contract.cli examples/checkout.json /tmp/none.json --action restart-payment
python3 -m sentinel_contract.cli examples/checkout.json /tmp/none.json --action scale-database
```

The first is `incomplete`; the second is `handover`.

## Verdicts

| Verdict | Meaning | Exit |
|---|---|---|
| `recovered` | Every required signal passed | 0 |
| `failed` | The journey or protected records failed | 1 |
| `incomplete` | Required evidence is missing | 1 |
| `unsafe` | A safety signal failed | 1 |
| `handover` | The action is outside the allowlist | 1 |

## Tests

```sh
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

## What it will not do

It does not execute a repair, page a person, or infer a verdict from logs. A caller supplies evidence. The contract decides what that evidence is allowed to prove.
