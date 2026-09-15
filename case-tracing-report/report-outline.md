# On-chain Investigation Report — Outline (FLAGSHIP, Week 1–2)

> Case: *[fill case name / hash]* · Chain: *[Ethereum / Tron / BSC]* · Type: *[approve-phishing / TRC-20 scam / ...]*
> Write in English. Every number must trace back to a tx hash or the address ledger.

## 1. Abstract (≤150 words, write last)
One paragraph: what happened, total loss, method, where funds ended, key conclusion.

## 2. Background
- What the project/victim is, date and context of the incident.
- Why this case is representative (how common this scam type is).

## 3. Timeline
| Time (UTC) | Block | Event | Tx Hash |
|---|---|---|---|

## 4. Methodology
Tools used (MistTrack / Etherscan / Tronscan), tracing direction (forward from victim / backward from CEX),
how labels and clusters were decided.

## 5. Incident Mechanics (how the scam/attack technically works)
- Step-by-step, with decoded calldata / approve evidence screenshots.

## 6. Fund-Flow Analysis (core)
### 6.1 Layer-by-layer path
For each hop: from → to, asset & amount, technique used (split / swap / bridge / mixer), tx hash, screenshot.
### 6.2 Fund-flow diagram
Insert the NetworkX/draw.io diagram; label nodes by role and edges by amount/technique.
### 6.3 Endpoints
CEX deposit addresses (which exchange if tagged), bridges used, mixers used, dormant wallets.

## 7. Address Labeling & Clustering
| Cluster | Shared heuristic (common gas funder / batch creation / fixed-split pattern / nonce continuity) | Addresses |
|---|---|---|

## 8. Current Status of Funds
How much remains, where it sits, last movement time.

## 9. Findings & Recommendations
- Triage / freezing requests: which CEX/issuer to contact and with which deposit addresses.
- Detection rules a monitor could deploy to catch this pattern early.
- User-protection advice (e.g. revoke unlimited approvals).

## 10. Appendix
- Full address ledger (link)
- Key tx hashes and decoded data
- Tool queries / SQL used
- Limitations (labels that could not be confirmed)
