# Blockchain Security & AML / KYT Portfolio

> Blockchain Engineering undergraduate (Chengdu University of Information Technology)
> focused on **on-chain investigation, fund-flow tracing, and turning theft/laundering
> patterns into monitoring rules**. English working proficiency — reports are written
> in English.

## TL;DR (read me in 30 seconds)
I traced a **real ~1.0M USDT approval-phishing theft** on Ethereum from victim wallet
to the peel-chain, then — instead of stopping at a writeup — I built the detection
tooling that a KYT team would use:
- a **phishing-drain alert generator** that passed on the known incident (0 false positives on live traffic),
- a **peel-chain / layering detector** that auto-rebuilds the fund-flow tree, and
- **Dune SQL queries** for a live monitoring dashboard.

Everything below is reproducible from on-chain data; every amount traces to a tx hash.

## Featured Work

### 1. Suspicious Activity Investigation — ~1.0M USDT approval-phishing (FLAGSHIP)
- End-to-end trace: new wallet (nonce 0) → malicious unlimited `approve` → `transferFrom`
  drain in **12 seconds** → commingling collection hub → 1inch multi-hop swap to ETH →
  16-day hold → bulk sweep → automated peel chain into ~15–25 ETH chunks.
- Deliverable: bilingual suspicious-activity report (risk rating, red-flag indicators,
  R1–R5 detection rules, disposition, and honest limitations).
- Files:
  - English report: [`case-tracing-report/report.md`](case-tracing-report/report.md)
  - Chinese report: [`case-tracing-report/report_cn.md`](case-tracing-report/report_cn.md)
  - Chinese fact sheet & address ledger: [`case-tracing-report/case-facts-cn.md`](case-tracing-report/case-facts-cn.md)
  - MistTrack fund-flow diagrams: [`case-tracing-report/assets/`](case-tracing-report/assets/)

### 2. Detection tooling (Python / web3.py / Alchemy)
- **Phishing-drain scanner** (`detect_phishing_drain.py`): flags "fresh-wallet unlimited
  approval → rapid `transferFrom` drain". Validated against the ground-truth case;
  0 false positives over ~2h of live mainnet traffic. See [`detector_evidence.md`](case-tracing-report/assets/detector_evidence.md).
- **Peel-chain / layering detector** (`detect_peel_chain.py`): scores fresh-EOA splits and
  recursion; given the root mule it auto-rebuilt the real two-hop fund tree.
  See [`peel_chain_evidence.md`](case-tracing-report/assets/peel_chain_evidence.md).
- Supporting tools: tx decoder, address tracer, 1inch swap decoder, WETH unwrapper.

### 3. KYT monitoring dashboard (Dune SQL)
- Queries for unlimited-approval volume, approve→drain candidates, and high-fan-out
  layering nodes — the R1–R5 rules made live and shareable.
- Files: [`dune/`](dune/)

## Field & Compliance Notes
- Etherscan field notes & case walkthrough: [`notes/01_etherscan-field-notes.md`](notes/01_etherscan-field-notes.md)
- AML / KYT crash course: [`notes/03_aml-training.md`](notes/03_aml-training.md)
- Resume bullets (EN+中文): [`notes/04_resume_bullets.md`](notes/04_resume_bullets.md)

## Toolbox
`Python (web3.py)` `SQL / Dune` `Etherscan` `MistTrack (SlowMist)` `Alchemy RPC` `Git` `Excel`

## Certifications (in progress)
- Chainalysis Cryptocurrency Fundamentals Certification (CCFC)
- TRM Academy (crypto crime typologies)

## Contact
- Email: *[your email]* · GitHub: [yuhangxian235](https://github.com/yuhangxian235)
