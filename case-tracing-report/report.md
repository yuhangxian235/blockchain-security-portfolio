# Suspicious Activity Investigation Report
## Illustrative On-Chain Case — Ethereum Mainnet (Educational / Portfolio Use)

| Field | Value |
|---|---|
| Case ID | OBC-2026-001 (internal, educational) |
| Chain | Ethereum Mainnet |
| Typology | ERC-20 approval-phishing → theft → DEX layering → peel-chain laundering |
| Date of incident | 2026-07-08 (UTC) |
| Date of analysis | 2026-09-17 |
| Risk rating | **HIGH** (proceeds of crime, organised laundering) |
| Analyst | *[your name]* |
| Sources | Etherscan, Alchemy node (real-time), MistTrack (SlowMist) |
| Status | Closed at peel-chain stage; final endpoint requires labelled intelligence DB |

> Confidentiality note: This is an education-grade reconstruction built from **public** on-chain data to demonstrate an investigation workflow. It is not an official STR/SAR and must not be treated as a binding attribution.

---

## 1. Executive Summary
On 8 July 2026, a newly activated Ethereum wallet (nonce 0) was compromised through a malicious **unlimited ERC-20 approval** phishing attack. Approximately **12 seconds** after the victim signed the approval, about **1,000,000 USDT** was removed from the wallet by an operator-controlled contract using `transferFrom`, with no further user signature. The proceeds were routed to a **shared collection wallet** that commingles multiple victims' funds, converted to ETH via a **1inch multi-hop DEX aggregation** (USDT→USDS→DAI→USDC→WETH→ETH), held for approximately **16 days**, then swept into a one-use EOA and dispersed through an **automated peel-chain** into sub-25 ETH increments across many fresh addresses. The pattern—unlimited-approval phishing, rapid drain, aggregation, DEX conversion, delayed bulk sweep, and systematic peeling—is consistent with an organised laundering operation. Funds had not reached a tagged exchange or mixer endpoint at the time of analysis; identifying the final destination requires a labelled intelligence database.

---

## 2. Subject Entities
| Address | Type | Role / Label |
|---|---|---|
| `0x8C949361B49320C48a51F4B1C6f9f83862530F89` | EOA | Victim wallet (newly activated, nonce 0) |
| `0x1178a87DB6dc5C010E39A325AF1F73BEc6470502` | Contract | Malicious approver / spender (Etherscan: Fake_Phishing4558420) |
| `0x6D8c070338eC3d297f1D0ECEEA296bd7E13a32b9` | EOA | Operator / tx broadcaster (Fake_Phishing4558116) |
| `0xf84c62572eEaFC90C0BCE3Fb6c85bCB573E68d93` | EOA | Shared collection / commingling hub (Fake_Phishing4592853) |
| `0xdAC17F958D2ee523a2206206994597C13D831ec7` | Contract | Tether USD (USDT, 6 decimals) |
| `0x111111125421cA6dc452d289314280a0f8842A65` | Contract | 1inch AggregationRouter v6 (legitimate infra) |
| `0xa58BdD0Ab5EBBb8dC425090feA8FD0bA969c1668` | Contract | 1inch executor / transient settlement (not an endpoint) |
| `0xc508a8c01bc3835be67e0e5554b7d91a1bb70da1` | EOA | Secondary collection point (received 639,999.50 USDT) |
| `0xB14225b5F75030743D50dC4F27F86D1331EF116a` | EOA | One-use mule; received 11.544 ETH, drained (nonce 2) |
| `0x6040E865152db6E833105D86d086fb7FA5b97534` | EOA | One-use mule; received ~370 ETH, split out (nonce 3, now empty) |
| `0x24698… / 0xc1695… / 0x33145… / 0x05aeb… / 0x9a35f… / 0xd6ebb… / 0xcb6f7…` | EOA | Peel-chain downstream nodes |
| `0x80D04079… / 0x1584a8EE… / 0x5565F176… / 0x161643f2…` | EOA | Operator batch EOAs (Fake_Phishing3348326 etc.) |

---

## 3. Narrative (Incident Description)
The victim's wallet made its **very first on-chain transaction (nonce 0)** at 17:51:47 UTC: an `approve(spender=0x1178…, amount=2^256-1)` granting **unlimited** USDT allowance to an unlabelled contract. Thirteen seconds later, the operator EOA `0x6D8c…` invoked the malicious spender contract, which used `transferFrom` to move **200,000 USDT** to collection hub `0xf84c…`. A second drain 36 seconds later removed a further 159,999.87 USDT (to the hub) and 639,999.50 USDT (to a secondary collector), totalling ~1.0M USDT. Because the approval was unlimited, the victim had no further interaction and was not required to sign again.

---

## 4. Timeline (UTC)
| Time (UTC) | Block | Event | Amount | Tx Hash (prefix) |
|---|---|---|---|---|
| 07-08 17:51:47 | 25489459 | Victim approves unlimited USDT to malicious spender | USDT max | `0x295549f3…` |
| 07-08 17:51:59 | 25489460 | `transferFrom` drain #1 | 200,000 USDT | `0x19ddd4f5…` |
| 07-08 17:52:35 | 25489463 | Drain #2 (two destinations) | 159,999.87 + 639,999.50 USDT | `0x6e882fd8…` |
| 07-08 17:54:35 | 25489473 | USDT transfer to secondary collector | 159,999 USDT | `0x003e6fa5…` |
| 07-08 17:56:23 | 25489482 | 1inch multi-hop swap → ETH | 200,000.87 USDT → 115.139676 ETH | `0x721aee9f…` |
| 07-09 04:08:11 | 25492533 | First small peel | 11.544 ETH → mule `0xb142…` | `0x86f4b2f6…` |
| 07-24 06:51:59 | 25600921 | Bulk sweep (after ~16 days) | 235.7137 ETH → `0x6040…` | `0x7ddd251e…` |
| 07-24 09:19:23 | 25601656 | Bulk sweep | 131.1000 ETH → `0x6040…` | `0x5a0a36ce…` |
| 07-24 10:18:35 | 25601951 | Sweep remainder | 3.6000 ETH → `0x6040…` | `0x3e0e66e8…` |
| 07-24 17:24–18:54 | 25604079–25604425 | Mule splits to fresh addresses | 103.77 + 17.64 ETH | `0x03e72d64…`, `0x33dcb646…` |
| 07-25 07:44:59 | 25608370 | Mule splits largest tranche | 282.39 ETH → `0x33145…` | `0xbf870bac…` |

Total ETH moved out of the commingling hub post-swap: **~381.96 ETH**; hub balance now **0.0997 ETH** (effectively emptied).

---

## 5. Fund-Flow Analysis
### 5.1 The chain
```
Victim (new wallet, nonce 0)
   │  approve unlimited (17:51:47)
   ▼
transferFrom drains ~1.0M USDT (17:51–17:52)
   ▼
Commingling hub 0xf84c… (many victims' funds mixed)
   │  1inch multi-hop swap: USDT→USDS→DAI→USDC→WETH→ETH
   │  (executor 0xa58bdd0 is transient; dstReceiver = hub itself)
   ▼
Hub holds ETH; waits ~10h (peels 11.5 ETH), then ~16 days
   │  bulk sweep 235.7 + 131.1 + 3.6 ETH
   ▼
One-use mule 0x6040… (nonce 3, now empty)
   │  splits: 282 / 106 / 103.77 / 17.64 ETH
   ▼
Peel chain: each hop halves/splits into ~15–23 ETH chunks
   ▼
Final endpoint not tagged on free tier (requires labelled DB)
```
### 5.2 Visuals (see `case-tracing-report/assets/`)
- `misttrack_mule_0x6040_flow.png` — hub → mule inflows/outflows.
- `misttrack_layer1_0x05aeb_split.png`, `misttrack_layer2_*.png` — peeling layers.

---

## 6. Risk Indicators / Red Flags (Typology Assessment)
The following indicators, taken together, support a **HIGH** rating for organised theft-and-laundering:
1. **Unlimited approval to an unlabelled contract** from a brand-new wallet (nonce 0) — hallmark of approval phishing.
2. **Drain within seconds** of approval via `transferFrom` by a third-party operator EOA — automated, not user-initiated.
3. **Commingling**: proceeds routed to a hub receiving funds from many unrelated victims.
4. **DEX layering**: same-transaction multi-hop stablecoin hopping (USDT→USDS→DAI→USDC→WETH) specifically to break the ERC-20 trace; final asset native ETH.
5. **Delayed bulk sweep**: funds held ~16 days, then moved in large tranches to one-use EOAs (nonce 2–3, drained to zero).
6. **Peel chain**: systematic splitting into ~15–25 ETH chunks across fresh addresses.
7. **Active counter-forensics**: each genuine ETH transfer is immediately "mirrored" by an identical-amount homoglyph token (`ĖTḨ` / `E឵Τ឵H`, signed by a different EOA), plus 1e-9 address-poisoning dust — characteristic of a known offender cluster.

---

## 7. Detection & Monitoring Recommendations (operational rules)
These are the rules a transaction-monitoring / KYT engine could deploy:
- **R1 — Unlimited-approval watch**: alert on `approve(spender, 2^256-1)` to an unverified/unlabelled contract when the wallet has very low tenure (e.g. nonce ≤ 2 or age < 7 days).
- **R2 — Rapid drain**: within ≤ 15 min of such approval, flag any `transferFrom` that moves > USD threshold out of the owner to an address with no prior history.
- **R3 — Aggregation + DEX layering**: an address receiving from ≥ N victims that then swaps via a major aggregator with multi-hop stablecoin routing.
- **R4 — Cold bulk sweep + peeling**: after a long dormancy, a large ETH outflow to a fresh EOA (nonce ≤ 5) that immediately splits funds into M chunks of similar size (e.g. 10–30 ETH) to brand-new addresses.
- **R5 — Counter-forensics cluster**: group and block the operator EOAs that issue homoglyph mirror tokens / batch calls (`0x8aaa8f3b`, `0x827f9F24Ca`, `0x77EB52E44d…` etc.); treat associated 1e-9 dust as poisoning, not funds.

---

## 8. Disposition
- **Disposition**: Escalate as suspicious activity (proceeds of theft / potential money laundering). Retain full evidence.
- **Action**: (a) add the identified subject EOAs/contracts to the internal blocklist with the labels above; (b) where any downstream node resolves to a custody venue/issuer via the labelled DB, prepare a freeze/hold request; (c) recommend the victim revoke remaining approvals (revoke.cash).
- **Confidentiality**: handle per SAR/STR rules; do not notify the subject.

---

## 9. Limitations
- The commingling hub mixes many victims' funds; downstream ETH cannot be attributed to a single victim at coin-level precision. Attribution here is by amount/time adjacency and is stated as a pool-level, not unit-level, conclusion.
- The final destination (exchange / mixer / bridge) was not reached on the free MistTrack tier and requires a labelled intelligence database; this report does not speculate beyond the peel-chain stage.
- The secondary collector `0xc508…` USDT line is not yet fully traced (follow-up).

## Appendix
- Chinese factsheet (full ledger & methodology): `../case-facts-cn.md`
- Tooling: `python-detection/` (`inspect_tx.py`, `trace_address.py`, `decode_1inch_swap.py`, `weth_unwrap.py`, `profile_address.py`)
- All amounts reproduced live from an Alchemy Ethereum mainnet node; every amount traces to a tx hash in the timeline.
