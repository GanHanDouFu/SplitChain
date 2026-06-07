# SplitChain — AI Agent 链上自动分账系统

> 山东省计算中心 · 区块链技术课程 · 研究生 26 上
>
> AI × Web3 Agentic Builders Hackathon 参赛项目

## 项目简介

传统多方分账（小组 AA、外包付款、DAO 赏金）依赖中心化平台，存在**中间方抽成、结算慢、不透明**三大痛点。

SplitChain 用 **AI Agent + 以太坊智能合约** 解决：用户自然语言描述分账规则 → AI 自主推理 → 调用链上合约执行 → Etherscan 可查。

## 技术架构

```
┌──────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│ 用户自然语言│──→│ AI Agent (ReAct 模式)   │──→│ SplitPayment 合约     │
│ 中文/英文  │    │ DeepSeek V4 Pro       │    │ Ethereum Sepolia      │
└──────────┘    │ 思考→调工具→观察→重复    │    └─────────────────────┘
                └──────────────────────┘              │
                        │              ┌──────────────┴──────────┐
                        │              │  Etherscan 链上可查       │
                        │              └─────────────────────────┘
                        │
                ┌───────┴────────┐
                │ Agent 可用工具:  │
                │ · 查询合约状态   │
                │ · 查看分账记录   │
                │ · 查看分账详情   │
                │ · 执行链上分账   │
                └────────────────┘
```

**没有传统后端。** 智能合约就是后端。前端是纯静态 HTML，Agent 是本地 Python 脚本。

| 层 | 技术 | 说明 |
|---|---|---|
| 智能合约 | Solidity 0.8.20 + Hardhat | 分账逻辑在链上，不可篡改 |
| AI Agent (CLI) | Python + Web3.py + DeepSeek API | ReAct + Function Calling，自主推理调用工具 |
| Web 前端 | 纯 HTML/CSS/JS + Web3.js | 无框架，无服务器，MetaMask 直连合约 |
| 网络 | Sepolia 测试网 | 公共 RPC，Etherscan 可查 |

## Agent 工作模式

Agent 使用 **ReAct (Reasoning + Acting)** 模式，通过 Function Calling 实现：

1. 用户输入自然语言指令
2. Agent 自主判断需要调用哪个工具
3. 调用工具获取链上数据
4. 观察结果，决定下一步（继续调工具 or 回复用户）
5. 最多推理 5 步，自主完成复杂任务

**可用工具：**
- `get_contract_info` — 查询合约余额、钱包状态、gas 价格
- `list_splits` — 查看所有分账记录
- `get_split` — 查看指定分账详情
- `execute_split` — 创建并执行链上分账

## 项目结构

```
split-payment-agent/
├── contracts/
│   └── SplitPayment.sol          # 分账智能合约
├── scripts/
│   └── deploy.js                 # Sepolia 部署脚本
├── test/
│   └── SplitPayment.test.js      # 合约测试（3个用例）
├── agent/
│   ├── agent.py                  # ReAct AI Agent CLI
│   └── requirements.txt          # Python 依赖
├── demo/
│   ├── index.html                # Web 前端 dApp
│   ├── architecture.png          # 系统架构图
│   └── flowchart.png             # 分账流程图
├── .env.example                  # 环境变量模板
├── hardhat.config.js             # Hardhat 配置
└── README.md
```

## 环境搭建

### 1. 安装依赖

```bash
git clone <repo-url>
cd split-payment-agent
npm install
pip install -r agent/requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`：
```
SEPOLIA_RPC_URL=https://sepolia.drpc.org    # 公共 RPC
PRIVATE_KEY=你的测试网钱包私钥
CONTRACT_ADDRESS=0x...                       # 部署后填入
DEEPSEEK_API_KEY=sk-...                      # DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 3. 编译合约

```bash
npx hardhat compile
npx hardhat test
```

## 部署

```bash
npm run deploy:sepolia
```

部署成功后把合约地址填入 `.env` 和 `demo/index.html` 的 `CONTRACT_ADDRESS`。

**已部署合约：** `0x9EB460236A381081606FE5Bf43F076f47Fa223Bb`

[Etherscan 查看](https://sepolia.etherscan.io/address/0x9EB460236A381081606FE5Bf43F076f47Fa223Bb)

## 使用

### Web 前端

浏览器打开 `demo/index.html` → 连接 MetaMask → 输入自然语言或手动填写 → 执行分账。

前端顶部集成了 AI 智能解析功能（由 DeepSeek V4 Pro 驱动），用自然语言描述分账规则即可自动填充表单。

### AI Agent CLI

```bash
python agent/agent.py
```

```
你> 现在合约什么状态？
Agent> [调用 get_contract_info] → 合约余额 0 ETH，共 0 笔分账，钱包余额 1.35 ETH

你> 帮我给 0xA... 和 0xB... 平分 0.01 ETH
Agent> [调用 execute_split] → 交易成功，查看 Etherscan: https://...

你> 刚才那笔分账的详情是什么？
Agent> [调用 get_split] → #0 分账: 0.01 ETH, 已执行, A:50% B:50%
```

Agent 会自主决定调用哪些工具、先查什么后做什么，不需要手动指定命令。

## 合约功能

`SplitPayment.sol`：
- `createSplit(address[], uint256[])` — 创建分账计划，转入 ETH
- `executeSplit(uint256)` — 执行分账，按比例发送 ETH
- `getSplit(uint256)` — 查询分账详情
- `splitCount()` — 分账总数
- 事件：`SplitCreated`, `SplitExecuted`
- 权限控制：仅创建者可执行，不可重复执行

## 链上证据

- 每笔分账有创建 + 执行两笔交易
- 合约地址公开，Etherscan 可查
- 所有分账记录可通过 `getSplit()` 查询
- 交易哈希、gas 用量、时间戳全部可追溯

## License

MIT
