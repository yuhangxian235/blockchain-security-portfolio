# R1+R2 Detector — Evidence of Operation

Tool: `python-detection/detect_phishing_drain.py` (live scanner) +
      `python-detection/selftest_known_drain.py` (regression test on the real incident).

## A. Live scan (low false-positive check)
Window: blocks 25995036 .. 25995636 (~2 hours of mainnet traffic).

```
Raw Approval events in window: 23161
Unlimited approvals (excluding known routers): 1613
Done. Candidates flagged: 0.
```

Interpretation: across ~2h of normal traffic the rule produced **0** alerts after
the three filters (fresh-wallet pre-approval nonce ≤5, contract spender, immediate
token outflow). Phishing drains are rare; 0 false positives on normal DeFi/DEX
traffic is the expected, desirable behavior.

## B. Regression test against the known July-2026 incident (ground truth)
The rule is replayed against the case we traced by hand (~1,000,000 USDT).

```
[R1] spender is contract?      True
[R1] owner pre-approval nonce:0   (fresh=True)
[R2] token outflows from owner in 20 blocks: 10
     -> 0xf84c6257...  200,000.00 USDT   blk=25489460  (12s after approval)
     -> 0xf84c6257...  159,999.87 USDT   blk=25489463  (48s)
     -> 0xc508a8c0...  639,999.50 USDT   blk=25489463  (48s)
VERDICT: detector would RAISE ALERT (PASS)
```

This matches the real incident: a brand-new wallet approved an unlimited USDT
allowance to an unlabelled contract, and 12 seconds later ~1.0M USDT was removed
via transferFrom. The detector flags exactly that pattern.

## Why this matters for the role
It shows the analyst does not just trace one wallet by hand — they can turn the
behaviour into an automated monitoring rule, validate it against ground truth, and
report its precision on live traffic.
