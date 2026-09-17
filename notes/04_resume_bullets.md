# Resume Bullets — Blockchain Security / KYT Analyst (English primary, Chinese gloss)

> 使用方法：把 GitHub 仓库链接放在简历顶部或 Projects 下方。
> 数字均为本仓库真实案件的链上可复现结果，不要改。

## Projects

**On-Chain Fraud & AML Investigation — Self-directed, Public Portfolio** · 2026
- Traced a real ~1.0M USDT ERC-20 approval-phishing incident end-to-end on Ethereum (victim → commingling collection hub → 1inch multi-hop swap → delayed bulk sweep → automated peel chain), and produced a bilingual (EN/中文) suspicious-activity report with risk rating, red-flag indicators, and disposition recommendations.
  - 独立完成一起约 100 万 USDT 授权钓鱼案的端到端链上追踪，并产出中英文双版可疑活动报告（含风险评级、红线指标、处置建议）。
- Reverse-engineered the laundering typology (placement / layering / integration) and identified counter-forensics (homoglyph mirror tokens + 1e-9 address poisoning); documented limitations honestly (no unit-level attribution, final endpoint needs a labelled DB).
  - 反推洗钱类型学（放置/分层/整合），识别反取证手法，并如实标注不确定性边界。

**KYT Detection Tooling — Python / web3 / Alchemy** · 2026
- Built a phishing-drain alert generator (R1 fresh-wallet unlimited approval → R2 rapid transferFrom drain); validated it against the ground-truth incident (correctly flagged a 200k USDT drain 12s after approval) and measured 0 false positives over ~2 hours of live mainnet traffic.
  - 编写"新钱包无限授权→极速盗刷"告警生成器，用真实案件回归通过，实时流量 0 误报。
- Built a peel-chain / layering detector that scores fresh-EOA splitting and recursion (nonce freshness, chunk similarity, fan-out); given a root address it auto-rebuilt the real fund-flow tree across two hops.
  - 编写剥皮链/分层检测器（按 nonce、拆分近似度、递归打分），输入根地址即自动重建两层资金树。

**KYT Monitoring Dashboard — Dune SQL** · 2026
- Wrote DuneSQL queries for a monitoring dashboard (unlimited-approval volume, approve→drain candidates, high fan-out layering nodes), converting the report's detection rules into live, shareable metrics.
  - 用 DuneSQL 写监控看板查询（无限授权量、授权→盗刷候选、高扇出分层节点），把报告里的规则变成可复用指标。

## Skills
- **Languages/Tools**: Python (web3.py), SQL / Dune, JavaScript basics, Excel (advanced); Etherscan, MistTrack (SlowMist), Alchemy RPC.
- **Domains**: ERC-20/approval mechanics, transaction forensics, AML/KYT concepts (placement-layering-integration, SAR/STR, OFAC sanctions screening), DeEX/DEX layering.
- **Languages**: Chinese (native), English (professional working proficiency).

## 面试一句话总结（elevator pitch）
"I traced a real ~$1M crypto theft case by hand, then turned its patterns into monitoring rules—an alert generator that passed on the known incident, a peel-chain detector, and a Dune dashboard. I'm not just learning forensics; I can operationalize it."
（我手动追了一起约百万美元的真实盗币案，并把其中的手法做成了监控规则和看板；不只是学取证，而是能落地成监测能力。）
