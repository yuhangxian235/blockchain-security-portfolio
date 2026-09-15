# 资料库与常用入口（第 1 天建好，全程复用）

> 用途：今天花约 1 小时把下面站点注册/收藏/逛一遍，之后每个案例都从这里取情报。
> 标注【今天必做】的是 Day1 就要打开的，其余先收藏。

## 一、案件 / 黑客事件库（选案、学手法）
| 站点 | 链接 | 用途 |
|---|---|---|
| Rekt News | https://rekt.news | 经典黑客事件深度复盘（英文，练阅读+学叙事） |
| DeFiHackLabs | https://github.com/SunWeb3Sec/DeFiHackLabs | 几乎所有重大攻击的可复现 PoC，第4周用 |
| 慢雾被黑档案 | https://hacked.slowmist.io | 中文被黑事件库，可按链/类型筛选 |
| ChainAbuse | https://www.chainabuse.com | 真实诈骗举报，能找到带举报的诈骗地址（选案来源） |
| BlockSec / Phalcon | https://phalcon.blocksec.com | 交易级可视化分析，看攻击交易内部调用 |

## 二、链上分析 / 取证工具（核心饭碗）
| 工具 | 链接 | Day1 动作 |
|---|---|---|
| MistTrack | https://misttrack.io | 【今天必做】登录，逐个功能点一遍：地址画像/资金溯源/溯源可视化/风险标签/监控 |
| Etherscan | https://etherscan.io | 【今天必做】注册账号，熟悉一个交易页全部字段（见 01 笔记） |
| Tronscan | https://tronscan.org | 【今天必做】注册，TRC-20 诈骗高发链，界面和 Etherscan 对照看 |
| BscScan | https://bscscan.com | 收藏，BSC 貔貅盘/土多 |
| Dune | https://dune.com | 确认能登录、找到你之前做的 dashboard（第3周升级它） |
| Tenderly | https://tenderly.co | 收藏，交易调试/内部调用trace |
| Etherscan 授权检查 | https://etherscan.io/tokenapprovalchecker | 【今天必做】输入任意地址看它给哪些合约授权了多少额度（理解 approve 风险） |

## 三、免费节点 / 数据接入（Python 取数要用）
| 服务 | 链接 | Day1 动作 |
|---|---|---|
| Alchemy | https://www.alchemy.com | 【今天必做】注册→建一个 Ethereum Mainnet App→复制 HTTPS URL 填到 .env |
| Infura | https://www.infura.io | 备选节点 |
| Chainlist | https://chainlist.org | 查各链 RPC、chainId |

## 四、免费权威认证（简历加分，本周内拿）
| 认证 | 入口 | 备注 |
|---|---|---|
| Chainalysis CCFC | Chainalysis Academy：https://academy.chainalysis.com（以官网实际入口为准） | 免费，约2小时，9/16 完成 |
| TRM Academy | TRM 官网 Trainings/Academy：https://www.trmlabs.com（以官网实际入口为准） | 免费入门认证，9/17 完成 |
| Dune SQL 教程 | https://docs.dune.com | 第3周前可当 SQL 复习 |

## 五、本地环境（今天落地）
- Python 3.14 已安装；Git 已安装（已检测到）。
- 依赖清单见 `../python-detection/requirements.txt`。
- 注意：Python 3.14 较新，若某个包 pip 安装失败，先告诉我报错，必要时装一个 3.12 并行环境，不要自己硬刚。
