# Etherscan / Tronscan 交易字段精读笔记（Day1，约 1.5h）

> 用法：上半部分是"知识点讲义"（我已帮你写好，你边看真实交易边对照）；
> 下半部分"实操记录"必须你自己找一笔真实交易填完——这才是今天的产出。

## A. 一笔交易页必须秒懂的字段

### 1) 交易概览
- **Transaction Hash**：交易唯一哈希，取证里的"证据编号"。
- **Status**：Success / Failed；失败也要看（攻击未遂、gas 耗尽）。
- **Block / Timestamp**：所在区块与时间，做时间线用。
- **From**：外部发起地址（EOA，私钥签名者）。
- **To / Interacted With (To)**：接收方；若是合约会显示合约名与图标——**钓鱼常伪装成同名假合约**。
- **Value**：转出的原生币（ETH/BNB/TRX）数量。注意：转 USDT 时 Value 通常是 0，钱在 Logs 里。

### 2) 费用与 Nonce
- **Transaction Fee = Gas Used × Gas Price**；EIP-1559 下分 Base Fee（烧毁）+ Priority Fee（给矿工）。
- **Nonce**：该发出地址的第几笔交易，**同一控制人批量转账时 Nonce 连续，是聚类线索**。

### 3) 真正的钱在哪：Tokens Transferred / Logs（重点）
- **Tokens Transferred**：ERC-20/721 的转账，来自事件日志 Logs。
- **Logs** 里每条含：address（触发合约）、Topics（Topic0=事件签名，如 Transfer；Topic1/2=from/to）、Data（金额等）。
- 看不懂原始 Data 就点 **"Decode Input Data" / 用 ABI 解码**，能还原成 `transfer(address,uint256)` 这种人话。

### 4) 资金怎么分叉：Internal Transactions（内部交易 / trace）
- 合约调用合约产生的链上价值转移，不在主交易里，**追踪资金必须切到这个 Tab**，否则会漏钱。

### 5) approve 授权钓鱼（本岗位最高频，必须吃透）
- `approve(address spender, uint256 amount)`：你授权 spender 合约"以后能动你多少该代币"。
- 钓鱼站诱导你签一个**无限额度（Max / uint256 最大值）**授权，之后骗子用 `transferFrom` 在任意时间把币转走——
  **所以受害者往往是"很久以后才被盗"，盗币交易的 From 是受害者、To 是骗子，且不需要受害者再次签名。**
- 自查工具：Etherscan 的 Token Approval Checker；撤销用 revoke.cash 类工具。
- 取证要点：先找"被盗转账"，再回溯历史里那笔 `approve`，定位受骗来源（哪个钓鱼站/签名）。

## B. Tronscan 对照（TRC-20）
- 结构同理：交易哈希、From/To、金额在 TRC-20 转账记录里；能量/带宽(Energy/Bandwidth)相当于 Gas。
- USDT-TRC20（合约 TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t）是诈骗洗钱最常见资产，重点熟悉。

---

## C. 实操记录（自己动手，必填）
### 任务1：找一笔真实的 approve 授权/被盗交易（可从 ChainAbuse 或 Etherscan 任意知名钓鱼案例取）
| 项目 | 内容 |
|---|---|
| Tx Hash |  |
| 所在链 / 区块 / 时间 |  |
| From / To（含合约名） |  |
| Value（原生币） |  |
| 调用的方法（Method，如 approve/transferFrom） |  |
| Tokens Transferred（币种+金额） |  |
| 关键 Log（事件名 + from/to） |  |
| 有无 Internal Tx，去了哪 |  |
| 一句话：这笔交易干了什么、为什么可疑 |  |

### 任务2：在 Token Approval Checker 输入一个地址，记下
| 项目 | 内容 |
|---|---|
| 它给哪些合约授权了 |  |
| 哪些是无限额度 |  |
| 哪些授权看起来有风险 |  |

---

## D. 地址台账列结构（9/19 正式追踪时用 Excel 维护，你精通 Excel，先建好表头）
建议列：`地址 | 标签(受害者/骗子/拆分点/CEX/桥/混币) | 层级 | 父地址 | 转入金额 | 转出金额 | 币种/链 | 证据TxHash | 判定依据 | 备注`
> 这份台账是后面报告和 Python 聚类脚本的共同数据源，务必每跳都记、可回溯。
