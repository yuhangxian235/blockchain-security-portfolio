# Etherscan / Tronscan 交易字段精读笔记（Day1，约 1.5h）

> 用法：上半部分是"知识点讲义"（我已帮你写好，你边看真实交易边对照）；
> 下半部分"实操记录"用一起真实授权钓鱼案逐跳填好，你的任务是到 Etherscan 逐项复核并随时提问。

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
- 注意：**原生 ETH 的内部转账不产生 Log**；ERC-20 每一跳都有 Transfer 事件，ETH 没有。这是新手最容易断链的地方（见 E 节心法）。

### 5) approve 授权钓鱼（本岗位最高频，必须吃透）
- `approve(address spender, uint256 amount)`：你授权 spender 合约"以后能动你多少该代币"。
- 钓鱼站诱导你签一个**无限额度（Max / uint256 最大值）**授权，之后骗子用 `transferFrom` 在任意时间把币转走——
  **所以受害者往往是"很久以后才被盗"，盗币交易不需要受害者再次签名。**
- 自查工具：Etherscan 的 Token Approval Checker；撤销用 revoke.cash 类工具。
- 取证要点：先找"被盗转账"，再回溯历史里那笔 `approve`，定位受骗来源（哪个钓鱼站/签名）。

## B. Tronscan 对照（TRC-20）
- 结构同理：交易哈希、From/To、金额在 TRC-20 转账记录里；能量/带宽(Energy/Bandwidth)相当于 Gas。
- USDT-TRC20（合约 TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t）是诈骗洗钱最常见资产，重点熟悉。

---

## C. 实操记录：案件基本信息与被盗交易

**案例：USDT 无限授权钓鱼（公开报道损失约 99.9 万 USDT，发生于 2026-07-08）**
- 受害者 victim：`0x8C949361B49320C48a51F4B1C6f9f83862530F89`
- 恶意授权合约 spender：`0x1178a87DB6dc5C010E39A325AF1F73BEc6470502`（Etherscan: Fake_Phishing4558420）
- 攻击者操控 EOA（盗币交易广播者）：`0x6D8c070338eC3d297f1D0ECEEA296bd7E13a32b9`（Fake_Phishing4558116）
- 共用归集热钱包：`0xf84c62572eEaFC90C0BCE3Fb6c85bCB573E68d93`（Fake_Phishing4592853）
- USDT 合约：`0xdAC17F958D2ee523a2206206994597C13D831ec7`（6 位小数）

### 任务1：被盗交易（drain，主看这笔）
| 项目 | 内容 |
|---|---|
| Tx Hash | `0x19ddd4f515f71da24859992496c9b1424bb26a6a9d02075f76b7eb258270f37c` |
| 区块 / 时间 | block 25489460 / 2026-07-08 17:51:59 UTC（北京 07-09 01:51:59） |
| From / To | From = 攻击者 EOA `0x6D8c…32b9`；To = 恶意合约 `0x1178…0502`（受害者之前授权的 spender） |
| Value（原生币） | **0 ETH**（钱不在主交易，而在 Logs） |
| 调用方法 | MethodID `0xcaa5c23f`（恶意合约自定义"清扫"函数），内部调 `USDT.transferFrom` |
| Tokens Transferred | **200,000 USDT**：受害者 `0x8C94…` → 归集钱包 `0xf84c…`（原始值 200000000000） |
| 一句话 | 受害者 12 秒前对恶意合约做了"无限 USDT 授权"，攻击者用 transferFrom 在无需再次签名的情况下转走 20 万 USDT |

### 配套：往前追一跳——那笔"埋雷"的 approve
| 项目 | 内容 |
|---|---|
| Tx Hash | `0x295549f3dabb8c02ed1910386bee51b6bcc6f2074887dba43d54806320b4bde2` |
| 区块 / 时间 | block 25489459（比被盗**早 1 个区块、约 12 秒**）/ 北京 01:51:47 |
| From / To | From = 受害者本人；To = USDT 合约 |
| 方法 | `approve(spender=0x1178…0502, amount=2^256-1)`，即**无限额** |
| 特别注意 | 该交易 **nonce=0**，是这个钱包第一笔链上交易（新钱包刚启用即被钓鱼） |
| 后续损失 | block 25489463 又被转走 159,999.87 + 639,999.50 USDT，三笔合计约 **999,999.37 USDT** |

### 任务2：Token Approval Checker（输入受害者地址复核）
- 它把 USDT 授权给了恶意合约 `0x1178…0502`，且为无限额；授权在被盗后仍长期有效，不撤销可被反复转走（revoke.cash / Etherscan 可撤销）。

---

## D. 地址台账列结构（正式追踪时用 Excel 维护，你精通 Excel，先建好表头）
建议列：`地址 | EOA/合约 | 标签(受害者/骗子/归集/马甲/CEX/桥/混币) | 层级 | 父地址 | 转入金额 | 转出金额 | 币种 | 时间 | 证据TxHash | 判定依据 | 备注`
> 这份台账是后面报告和 Python 聚类脚本的共同数据源，务必每跳都记、可回溯。

---

## E. 任务3：资金向下追踪（已用 Python 逐笔链上核验，数字可复现）

> 工具（均在 `python-detection/`）：`trace_address.py` 拉地址全部流水；`hop1_usdt.py` 锁头几跳大额 USDT；
> `inspect_tx.py` 解码单笔交易日志；`decode_1inch_swap.py` 解 1inch 交易的最终收款人；
> `weth_unwrap.py` 解 WETH 换 ETH；`hop2_eth.py` 追原生 ETH 出金；`profile_address.py` 给地址画像。

### E0. 追踪心法（每一跳都按这 8 步走，思路就不会乱）
1. **这一跳是什么资产？** ERC-20 看 **Logs 的 Transfer**；原生 ETH 看交易 **Value / Internal Txns**——**ETH 转账没有 Log**。
2. **谁签名（tx.From）？对手方是谁（tx.To 或 Transfer.to）？** 二者经常不是同一个，别混。
3. **对手方是 EOA 还是合约？** 是合约就去解 calldata / 查部署者，**不能只看它"发出的交易"（合约没有私钥、不会签名）**。
4. **经过 DEX / 聚合器时，最终收款人不在 Logs 里，而在 calldata 的 `dstReceiver` 字段**；再用"收款地址在该区块前后的 ETH 余额变化"二次验证。
5. **每跳只跟"真腿"**：金额对得上、签名者是当前地址、是原生币或真实代币。
6. **剔除干扰**：1e-9 的粉尘、同形字假币（符号里是特殊字母如 `ĖTḨ`、且签名者是别的地址）一律不算资金。
7. **资金混同后追的是"资金池"不是某一枚币**：归集钱包混了很多受害者的钱，用"金额匹配 + 时间相邻（必要时 FIFO）"归因，并在报告写明口径与不确定性。
8. **终点判型**：CEX 充值（成百上千人打款、带交易所标签）、混币器（Tornado 常见固定面额 0.1/1/10/100 ETH）、跨链桥、OTC；到这一层即可下结论并建议冻结/举报。

### E1. 第一跳：USDT 进入共用归集钱包
- 收款地址 `0xf84c…` 是团伙**共用归集热钱包**，案发后混入大量其他受害者资产，并有 1e-9 粉尘、同形字假币，**不能把它全部流水算到本案**。
- 头几分钟大额 USDT 动向：

| 时间(UTC) | 区块 | 方向 | 金额 | 对手方 | 方式 / Tx |
|---|---|---|---|---|---|
| 17:51:59 | 25489460 | 入 | 200,000 USDT | 受害者→`0xf84c` | transferFrom，tx `0x19ddd4f5…` |
| 17:52:35 | 25489463 | 入 | 159,999.87 USDT | 受害者→`0xf84c` | tx `0x6e882fd8…` |
| 17:54:35 | 25489473 | 出 A | 159,999 USDT | →`0xc508a8c01bc3835be67e0e5554b7d91a1bb70da1`（第二归集点，另收过 639,999.50） | 普通 transfer，tx `0x003e6fa56a3f42ee05c641431cba43012329297124047760d21aa6c81403fbaa` |
| 17:56:23 | 25489482 | 出 B | 200,000.87 USDT | →1inch 换 ETH，**最终 ETH 又回到 `0xf84c` 自己** | tx `0x721aee9f5f203dfe42d646e8467d7a4787817aa1657c931d527d3bbdc1ef1a52` |

### E2. 出 B 正确读法：1inch 换币，最终收款人要用 calldata 确认（重点纠错）
- 这笔交易 To = **1inch AggregationRouter v6** `0x111111125421cA6dc452d289314280a0f8842A65`，selector `0x07ed2379`。
- Logs 里看到的换币路径：`USDT → USDS → DAI → USDC → WETH → 解封装`，其中资金反复经过合约
  `0xa58BdD0Ab5EBBb8dC425090feA8FD0bA969c1668`——它是 1inch 的 **executor（结算合约，临时中转，21,567 字节）**，**不是收款终点**。
- ⚠️ 易错点：最后一条 WETH `Withdrawal` 显示 ETH 提到了 executor `0xa58bdd0`，新手会在这里停下误判终点。
  其实那之后 executor 还会把 ETH 通过**没有 Log 的内部调用**转给真正收款人。
- ✅ 正确做法（`decode_1inch_swap.py` 解 calldata 的 `SwapDescription`）：
  - `executor = 0xa58bdd0…`（中转）
  - `dstToken = 0xEeeE…EEeE`（1inch 用这个特殊地址表示**原生 ETH**）
  - **`dstReceiver = 0xf84c…`（就是发起换币的归集钱包自己）**
  - 投入 200,000.873962 USDT，minReturn 114.085 ETH，实际换得 **115.139676 ETH**。
- ✅ 余额二次验证：归集钱包 ETH 余额在该区块 **105.900108 → 221.039446，净增 +115.139338 ETH**（差额为 gas），与换币结果吻合。
- 结论：骗子把 20 万 USDT **原地换成 ETH、提回自己的归集钱包**，和其他受害者的 ETH 混在一起。

### E3. 第二跳：归集钱包的原生 ETH 出金（先小额剥皮，攒 16 天后大额清空）
| 时间(UTC) | 区块 | 金额(ETH) | 收款马甲 | 性质 | Tx |
|---|---|---|---|---|---|
| 07-09 04:08 | 25492533 | 11.5440 | `0xB14225b5F75030743D50dC4F27F86D1331EF116a`（EOA，nonce=2，现余额 0） | 先剥一小块 | `0x86f4b2f66226112c2247133f21722b45feb3dbef577948beffe049834e75fee8` |
| 07-24 06:51 | 25600921 | 235.7137 | `0x6040E865152db6E833105D86d086fb7FA5b97534`（EOA，nonce=3，现余额 0） | 大额清空 | `0x7ddd251eeaedd3194a79062f53b6f8a4c8fdd5296ebcb4ea339f152f2568a727` |
| 07-24 09:19 | 25601656 | 131.1000 | 同上 `0x6040…` | 大额清空 | `0x5a0a36ce4f792c73d6fdfaeab6e25e27a920e359de03d719ff9838dd276e7cb5` |
| 07-24 10:18 | 25601951 | 3.6000 | 同上 `0x6040…` | 零钱 | `0x3e0e66e87ae593980e714997d3792c5aa49fdc443a6d8f6d5260342278c2d99e` |

- 合计自换币后转出 **381.96 ETH**，归集钱包**当前余额 0.0997 ETH（基本清空）**。
- 行为特征（可写进报告的 IOC）：**换币后先等约 10 小时剥一小块试探，再囤积约 16 天攒到 ~380 ETH，然后分 3 笔大额扫给一次性马甲**——典型"剥皮链 + 定期归集"节奏。

### E4. 第三跳：马甲 fan-out 剥皮 + 同形字/粉尘反追踪（学会只认真腿）
以马甲 `0x6040…` 为例，它收到钱后自动切成多块剥给下一层全新 EOA（**这些才是真腿，由 0x6040 自己签名、转原生 ETH**）：
- 07-24 17:24　**103.774050687 ETH** → `0x24698a72b4…`
- 07-24 18:54　**17.64158861679 ETH** → `0xc16954db74…`
- 07-25 07:44　**282.39027612578417 ETH** → `0x33145d625e…`（另有多笔同类 fan-out）

马甲 `0xb142…` 同理：11.544 进 → 07-09 06:18 出 6.8747 ETH 到 `0xf5db8df1db…`，07-11 再出 4.669 ETH 到 `0xdaa39f179d…`，随后归零。

**流水里的反追踪干扰（一律剔除，不要当钱追）：**
- 每笔真 ETH 转出后，立刻出现一笔**金额完全相同、但代币是同形字假币 `ĖTḨ` / `E឵Τ឵H`** 的"镜像转账"，签名者是另外几个 EOA
  （`0x5565F17657…`、`0x1584a8EE67…`、`0x161643f280…`）和批量合约（`0x80D04079…` 调 `0x8aaa8f3b`）。目的：在浏览器/追踪工具里以假乱真，让你跟错。
- 随后多个与收款地址前缀相似的地址打入 **1e-9 ETH 粉尘**（地址投毒），污染地址本与自动聚类。
- **辨别规则**：真腿 = 原生 ETH（或真实代币）+ 签名者就是当前马甲 + 金额为大额；假腿 = 同形字符号的代币 + 签名者不同；粉尘 = 1e-9。

### E5. 到 Etherscan 点哪里核对
1. 1inch 换币：https://etherscan.io/tx/0x721aee9f5f203dfe42d646e8467d7a4787817aa1657c931d527d3bbdc1ef1a52 —— To=1inch Router；Logs 看 USDT→…→WETH→Withdrawal；**Input Data 解码后找 `dstReceiver = 0xf84c…`**。
2. executor 中转合约（确认是 Contract、不是终点）：https://etherscan.io/address/0xa58BdD0Ab5EBBb8dC425090feA8FD0bA969c1668
3. 归集钱包 ETH 余额/出金：https://etherscan.io/address/0xf84c62572eEaFC90C0BCE3Fb6c85bCB573E68d93 —— 看 **ETH 余额历史**和 Transactions 里的大额 ETH 转账。
4. 两个空壳马甲（看 nonce 极小、余额 0）：https://etherscan.io/address/0x6040E865152db6E833105D86d086fb7FA5b97534 和 /0xB14225b5F75030743D50dC4F27F86D1331EF116a。

### E6. 下一步（M1 里程碑）
- 用 **MistTrack** 打开 `0x6040…`、`0x24698a72…` 等地址，让它自动沿"真腿"画图并标注 CEX/混币器/桥，与脚本结果交叉验证。
- 手动沿一条真腿继续（建议先跟 282.39 ETH 那条），直到命中**带标签的终点**（交易所充值 / Tornado / 跨链桥），记录命中点 TxHash 与标签。
- 把第二归集点 `0xc508…`（USDT 线）也追完，形成"USDT 线 + ETH 线"两条完整资金流，喂给 W2 的英文追踪报告。

### E7. MistTrack 可视化交叉验证（截图存档，作为报告配图）
用 MistTrack（慢雾）打开马甲 `0x6040…5b97534`，自动画出的资金流向与脚本完全一致，确认这是一条**自动剥皮链（peel chain）**：
- 配图1 `case-tracing-report/assets/misttrack_mule_0x6040_flow.png`：归集钱包 `0xf84c…` 打进来 **370.41 ETH**，马甲再向外分（282.39 / 17.64 / 103.77 ETH）。
- 配图2 `…/misttrack_layer1_0x05aeb_split.png`：282 ETH → `0x05aeb…0a441cd`，再拆成 67.58 / 106.0 / 108.81 ETH。
- 配图3 `…/misttrack_layer2_0x9a35f_fanout.png`：108.81 ETH → `0x9a35f…`，再拆成 7 块（15~18 ETH）。
- 配图4 `…/misttrack_layer2_0xcb6f7_fanout.png`：106 ETH → `0xd6ebb…`→`0xcb6f7…`，再拆成 5 块（~19~23 ETH）。

**结论（M1 结案口径）**：资金经"归集 → 1inch 换 ETH → 攒 16 天大额扫给空壳马甲 → 每跳切半/切块、越拆越小"的自动剥皮网络，散为 ~20 ETH 级碎块继续向下游；精确终点（交易所/OTC/桥）需借助带标签的链上情报库进一步定位。免费层无需、也不应逐分支追到底。
> 取证纪律：MistTrack 图里金额很小、带红标的节点（如仅 1 ETH 的 `0xade9d…`）与本案主线无关，不追；同形字假币/粉尘在 Etherscan 流水里也忽略。
