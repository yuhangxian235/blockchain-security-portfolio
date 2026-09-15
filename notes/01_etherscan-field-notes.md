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

## C. 实操记录（已用真实案例填好，你的任务是到 Etherscan 逐项复核并随时提问）

**案例：USDT 无限授权钓鱼（公开报道损失约 99.9 万 USDT，发生于 2026-07-08）**
- 受害者 victim：`0x8C949361B49320C48a51F4B1C6f9f83862530F89`
- 恶意授权合约 spender：`0x1178a87DB6dc5C010E39A325AF1F73BEc6470502`
- 攻击者操控 EOA（盗币交易广播者）：`0x6D8c070338eC3d297f1D0ECEEA296bd7E13a32b9`
- 第一笔收款地址：`0xf84c62572eEaFC90C0BCE3Fb6c85bCB573E68d93`
- USDT 合约：`0xdAC17F958D2ee523a2206206994597C13D831ec7`

### 任务1：被盗交易（drain，主看这笔）
| 项目 | 内容 |
|---|---|
| Tx Hash | `0x19ddd4f515f71da24859992496c9b1424bb26a6a9d02075f76b7eb258270f37c` |
| 所在链 / 区块 / 时间 | Ethereum 主网 / block 25489460 / 2026-07-08 17:51:59 UTC（北京 07-09 01:51:59） |
| From / To（含合约名） | From = 攻击者 EOA `0x6D8c…32b9`；To = 恶意合约 `0x1178…0502`（即受害者之前授权的 spender） |
| Value（原生币） | **0 ETH**（钱不在主交易，而在 Logs） |
| 调用的方法 | MethodID `0xcaa5c23f`（恶意合约自定义“清扫”函数），内部调用 `USDT.transferFrom` |
| Tokens Transferred | **200,000 USDT**：受害者 `0x8C94…` → 收款地址 `0xf84c…`（原始值 200000000000，USDT=6 位小数） |
| 关键 Log | 1 条 `Transfer(USDT)`：from=受害者，to=收款地址，value=200000000000 |
| 有无 Internal Tx | 无原生 ETH 内部转账；代币转移全部体现在 Logs/Tokens Transferred |
| 一句话 | 受害者 12 秒前对恶意合约做了“无限 USDT 授权”，攻击者调用该合约用 transferFrom 在**无需受害者再次签名**的情况下转走 20 万 USDT |

### 配套：往前追一跳——那笔“埋雷”的 approve
| 项目 | 内容 |
|---|---|
| Tx Hash | `0x295549f3dabb8c02ed1910386bee51b6bcc6f2074887dba43d54806320b4bde2` |
| 区块 / 时间 | block 25489459（比被盗**早 1 个区块、约 12 秒**）/ 北京 01:51:47 |
| From / To | From = 受害者本人；To = USDT 合约 |
| 方法 | `approve(spender=0x1178…0502, amount=2^256-1)`，即**无限额** |
| Log | `Approval(owner=受害者, spender=0x1178…, value=max)` |
| 特别注意 | 该交易 **nonce=0**，是这个钱包的第一笔链上交易（新钱包刚启用即被钓鱼） |
| 后续损失 | block 25489463 又被转走 159,999.87 + 639,999.50 USDT，三笔合计约 **999,999.37 USDT** |

### 任务2：Token Approval Checker（输入受害者地址 `0x8C94…` 复核）
| 项目 | 内容（以你打开页面看到的“当前状态”为准） |
|---|---|
| 它给哪些合约授权了 | USDT 授权给恶意合约 `0x1178…0502` |
| 哪些是无限额度 | 该笔即为无限额（2^256-1） |
| 哪些授权看起来有风险 | 授权对象是不知名合约、且额度无限；授权在被盗后仍长期有效，不撤销就可能被反复转走（可用 revoke.cash / Etherscan 撤销） |

### 到 Etherscan 点哪里逐项核对
1. 被盗交易：https://etherscan.io/tx/0x19ddd4f515f71da24859992496c9b1424bb26a6a9d02075f76b7eb258270f37c —— Overview 看 From/To/**Value=0**；下拉看 **Tokens Transferred** 的 200,000 USDT；切 **Logs** 看 Transfer；点 **Input Data → Decode** 看方法。
2. 授权交易：https://etherscan.io/tx/0x295549f3dabb8c02ed1910386bee51b6bcc6f2074887dba43d54806320b4bde2 —— Input Data 里看 `approve` 的 spender 和那个超大金额。
3. 受害者地址：https://etherscan.io/address/0x8C949361B49320C48a51F4B1C6f9f83862530F89 —— 看交易历史、Token Holdings，以及 **Token Approvals** 标签页。
4. 点 To 合约 `0x1178…` 和攻击者 EOA `0x6D8c…`，观察 Etherscan 给的公开标签/风险提示。

---

## D. 地址台账列结构（9/19 正式追踪时用 Excel 维护，你精通 Excel，先建好表头）
建议列：`地址 | 标签(受害者/骗子/拆分点/CEX/桥/混币) | 层级 | 父地址 | 转入金额 | 转出金额 | 币种/链 | 证据TxHash | 判定依据 | 备注`
> 这份台账是后面报告和 Python 聚类脚本的共同数据源，务必每跳都记、可回溯。

---

## E. 任务3：资金向下追踪（第一跳，已用脚本逐笔链上核验，数字可复现）

> 工具：`python-detection/trace_address.py`（拉某地址全部资金流水）、`hop1_usdt.py`（锁定头几跳大额 USDT）、`inspect_tx.py`（解码单笔交易日志）、`weth_unwrap.py`（解 WETH 换 ETH）。

### 关键认知：收款地址 `0xf84c…` 是团伙“共用归集热钱包”，不是个人钱包
- 它在案发后几小时内**混入了大量其他受害者**的资产（PEPE/SHIB/XEN/USDC/各种山寨币），还有大量 **1e-9 ETH 投毒粉尘**和**同形字假币**（符号显示为 `ÚЅDТ`、`ĖTḨ`，用来污染你在钱包/浏览器里的地址本）。
- ⚠️ 取证纪律：**不能把这个地址的全部流水都算到本案受害者头上**。资金已混同，要按“金额对应 + 时间相邻（必要时 FIFO 先进先出）”逐跳锁定本案那笔钱。

### 本案 20 万 USDT 的第一跳（被盗后 5 分钟内）
| 时间(UTC) | 区块 | 方向 | 金额 | 对手方 | 方式 / 证据 Tx |
|---|---|---|---|---|---|
| 17:51:59 | 25489460 | 流入归集 | 200,000 USDT | 受害者 → `0xf84c…` | 盗币 transferFrom，tx `0x19ddd4f5…`（任务1） |
| 17:52:35 | 25489463 | 流入归集 | 159,999.87 USDT | 受害者 → `0xf84c…` | 第二笔盗币，tx `0x6e882fd8…` |
| 17:54:35 | 25489473 | **流出 A** | 159,999 USDT | `0xf84c…` → `0xc508a8c01bc3835be67e0e5554b7d91a1bb70da1` | 普通 `transfer`(0xa9059cbb)，tx `0x003e6fa56a3f42ee05c641431cba43012329297124047760d21aa6c81403fbaa` |
| 17:56:23 | 25489482 | **流出 B** | 200,000.87 USDT | `0xf84c…` → 1inch 路由 → 最终 **115.139676 ETH** 到 `0xa58BdD0Ab5EBBb8dC425090feA8FD0bA969c1668` | 1inch 换币(0x07ed2379)，tx `0x721aee9f5f203dfe42d646e8467d7a4787817aa1657c931d527d3bbdc1ef1a52` |

- **流出 A 的 `0xc508…` 是第二个归集点**：它在第二笔盗币 tx 里还直接收过 639,999.50 USDT，资金在这里再次汇聚，待继续下追。
- 金额对应关系：200,000.87 那笔≈本案第一笔 20 万（多出的 0.87 是别人的粉尘）；159,999 那笔≈第二笔 159,999.87。混同场景下这是“金额+时间”启发式，严格 FIFO 可能不同，报告里要写明口径。

### 流出 B：1inch 多跳换币路径（同一笔 tx 内，看 Logs 从下往上/按顺序读）
```
200,000.87 USDT  (归集钱包 0xf84c → 结算合约 0xa58bdd0)
   ├─ 500 USDT            → 0xcD6b9800…（小额分流）
   └─ 199,500.87 USDT     → PSM 0x000…4444 换成
        199,373.75 USDS   → 0xA188… 销毁并铸出
        199,373.75 DAI    → PSM 0xf6e72Db… 换成
        199,373.75 USDC   → 交易池 0xd315a9… 换成
        115.139676 WETH   → 结算合约 0xa58bdd0
                            → WETH.withdraw() 解封装
        115.139676 原生 ETH → 0xa58BdD0…（合约，code 长度 21567）
```
> 判定依据：最后两条 WETH 日志——`Transfer` 115.139676 WETH 入金，紧接 `Withdrawal(src=0xa58bdd0, wad=115.139676)`。WETH9 合约在 `withdraw()` 中**必然**把等额原生 ETH 转给 src，所以无需内部 trace 也能铁证 ETH 落点。

### 这一步看到的洗钱手法（术语，报告里直接用）
1. **Aggregation hub（资金归集）**：多个受害者钱先汇到同一热钱包，混同资金。
2. **DEX-aggregator swap / chain-hopping（换币断链）**：用 1inch 在一笔交易里连环换 USDT→USDS→DAI→USDC→WETH，拉断 ERC-20 转账轨迹。
3. **WETH unwrap（解封装）**：WETH→原生 ETH，进入更难追的 ETH 原生转账/内部交易世界。
4. **Peeling chain（剥皮链）/ 批量拆分**：之后 ETH 被切成 11.544 / 131 / 235 ETH 等块，经批量分发 EOA（如 `0x80D04079…`，Etherscan 标 Fake_Phishing3348326）一层层剥出（下一步追）。
5. **Address poisoning（地址投毒干扰）**：1e-9 粉尘 + 同形字假币 `ÚЅDТ/ĖTḨ`，制造假地址、污染分析，**不要把它们当真实资金**。

### 到 Etherscan 点哪里核对（任务3）
1. 1inch 换币交易：https://etherscan.io/tx/0x721aee9f5f203dfe42d646e8467d7a4787817aa1657c931d527d3bbdc1ef1a52 —— 看 **To = 1inch: Router**（`0x1111111254…`）；下拉 **Logs/Event Logs** 按顺序看 USDT→USDS→DAI→USDC→WETH 一串 Transfer；最底部两条是 WETH 的 `Transfer` + `Withdrawal`。
2. 流出 A 普通转账：https://etherscan.io/tx/0x003e6fa56a3f42ee05c641431cba43012329297124047760d21aa6c81403fbaa —— Method 显示 `Transfer`，To=Tether USD，Tokens Transferred 里 159,999 USDT 到 `0xc508…`。
3. ETH 落点合约：https://etherscan.io/address/0xa58BdD0Ab5EBBb8dC425090feA8FD0bA969c1668 —— 确认它是 **Contract** 不是普通地址；看它随后怎么把 ETH 转走（下一跳）。
4. 第二归集点：https://etherscan.io/address/0xc508a8c01bc3835be67e0e5554b7d91a1bb70da1 —— 看 ERC-20 转账历史，能同时看到 639,999.50 和这笔 159,999。
5. 归集热钱包全貌：https://etherscan.io/address/0xf84c62572eEaFC90C0BCE3Fb6c85bCB573E68d93 —— 感受“多受害者混同 + 粉尘/假币”的噪声。

> 下一步（第二跳）：分别追 `0xa58bdd0`（115.14 ETH 之后流向，重点看是否进混币器/跨链桥/CEX）和 `0xc508…`（USDT 归集后去向）；并用 MistTrack 打开这两个地址做可视化交叉验证。
