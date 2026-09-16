# 合规 / 风控（KYT·AML）知识补课路线
> 目标岗位：区块链安全分析 / KYT / 交易监测 / 反洗钱风控（Web3 交易所、链上情报与风控厂商、支付合规科技）。
> 你的现状：链上追踪技术已超过多数纯合规候选人；缺的是"规则、流程、术语、监管框架"这套合规语言。
> 节奏：每天 4 小时里，拿 30–45 分钟学合规，其余继续做作品集；4 周内拿下一个免费证书。

## 0. 先想清楚：这个岗到底做什么
- 不是"抓黑客、写 PoC"，而是：**告警进来 → 查地址 → 判风险等级 → 决定继续监控/冻结/上报 → 写工单/调查报告**。
- 核心能力 = 链上分析（你已在练）+ 犯罪类型学 + 风控判断 + 清晰报告（你已有英文报告初稿）。
- 招聘方看你作品集，看的是：**你能不能独立完成一次"告警调查 → 定性 → 处置建议"闭环**。

## 1. 必懂核心概念（Week 1–2，优先级最高）
| 概念 | 一句话理解 | 怎么和你的案子对照 |
|---|---|---|
| AML / KYC / CDD / EDD | 反洗钱；客户身份识别；简化/强化尽职调查 | 新用户入金要 KYC；高风险客户走 EDD |
| 风险为本（Risk-based approach） | 不是一刀切，按风险高低分配资源 | 我们这起案子判 HIGH 的理由 |
| 洗钱三阶段 | placement（放置）→ layering（分层）→ integration（整合/变现） | 放置=归集钱包混同；分层=1inch换币+剥皮链；整合=进 CEX/混币器变现 |
| KYT（Know Your Transaction） | 对每笔交易/地址做风险筛查、打分 | 就是报告里 R1–R5 规则背后的引擎 |
| 制裁筛查（Sanctions / OFAC SDN） | 命中被制裁名单/地址必须冻结并上报 | 如 Tornado Cash、Blender.io、Garantex、Sinbad 等已被制裁 |
| Travel Rule / FATF R.15 | 虚拟资产服务商(VASP)之间转账要带双方身份信息 | 交易所提币/收款要做可追溯 |
| SAR / STR | 可疑活动/交易报告；分析师只调查上报，不通知嫌疑人，严格保密 | 你写的 report.md 就是它的模拟件 |
| 暴露度（Exposure） | 你的资金与已知赃款/制裁地址的关联距离 | MistTrack/Chainalysis 标红就是在算这个 |

> 记忆钩子：**你这起案子 = placement（归集）→ layering（换币+剥皮）→ integration（未达终点）**。把这三段背熟，面试随便问。

## 2. 加密货币犯罪类型学（Week 2，边学边在 Etherscan 认特征）
- 盗币类：授权钓鱼（**就是我们这起**）、私钥泄露、恶意授权/签名（如 Permit、签名重放）。
- 骗局类：Rug pull（项目方抽走流动性）、Exit scam（跑盘）、杀猪盘/ romance scam、虚假投资。
- 勒索类：Ransomware 收款（如 Lazarus、暗网市场），常有固定收款地址、要求换成匿名币。
- 混币/洗白：Tornado（固定面额 0.1/1/10/100 ETH）、Blender、链上换币断链、跨链桥洗白、PEEL CHAIN（剥皮链，你已识别）。
- **每种都记一句"链上特征"**，面试能直接举例。

## 3. 监管地图（Week 3，高层即可，不背法条）
- 美国：BSA/AML、FinCEN 指引、OFAC 制裁名单；
- 欧盟：MiCA（加密资产市场监管）、AMLD5/6；
- 亚洲：香港 VASP 发牌、新加坡 MAS 指引；
- 中国：境内对虚拟货币交易炒作的监管态度（了解边界即可）。
- 你大概率投递的雇主类型：交易所海外合规/风控岗、链上情报/风控厂商（慢雾 MistTrack、派盾 PeckShield、Chainalysis、TRM 类）、支付与合规科技公司。

## 4. 免费学习资源 / 证书（按这个顺序）
1. **Chainalysis Cryptocurrency Fundamentals Certification（CCFC）**——最对口，两周内拿下，写进简历。
2. **TRM Academy（免费）**——犯罪类型学与 KYT 课程，和 CCFC 互补。
3. **公开案例库**：OFAC 制裁公告（Tornado / Blender / Garantex）、Chainalysis 年度加密犯罪报告、慢雾/派盾年度报告——读，熟悉术语与典型数字。
4. **Etherscan / MistTrack 标签天天看**：看到 Fake_Phishing / sanctioned / exploit 标签就点进去学。

## 5. 和作品集怎么并轨
- 把学到的类型学，每 2–3 天用你会的方法在 Etherscan 上验证一个真实案例；
- 每种类型总结成 1 页"**类型学 + 链上特征 + 检测规则**"，攒 3–4 个，是报告之外的加分项；
- 报告中英文双版；代码必讲思路。

## 6. 今天就做（第 1 步，2–3 小时）
1. 注册 Chainalysis CCFC，学 "AML fundamentals / crypto crime basics" 前两章；
2. 边学边对照我们这起案子：哪一步是 placement、哪一步是 layering、为什么判 HIGH；
3. 不背法条，先把"三阶段 + KYT + 制裁筛查 + SAR"四个词的含义用自己的话讲出来。
