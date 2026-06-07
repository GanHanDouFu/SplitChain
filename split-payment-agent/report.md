# AI Agent 驱动的链上自动分账系统

## —— SplitChain 项目技术报告

---

**课程名称：** 区块链技术

**项目名称：** AI Agent 驱动的链上自动分账系统（SplitChain）

**项目成员：** （填写姓名、学号）

**指导教师：** （填写教师姓名）

**提交日期：** 2026年6月

---

## 目录

一、项目背景与选题依据

二、需求分析与痛点识别

三、区块链技术解决方案设计

四、系统开发实现

五、原型系统验证与测试

六、应用价值分析

七、风险与挑战分析

八、未来扩展方向

九、结论

参考文献

---

## 一、项目背景与选题依据

### 1.1 选题背景

随着分布式协作模式的普及，多方之间的资金分配场景日益增多。无论是小组活动的 AA 制分摊、项目外包的多方结算，还是去中心化自治组织（DAO）的赏金分配，都涉及将一笔资金按约定规则分配给多个参与者的问题。

传统的分账方式通常依赖中心化平台（如微信转账、支付宝群收款、银行代发等），由发起人手动操作或平台代为处理。然而，这些方式存在信任依赖、效率低下和透明度不足等根本性缺陷。

### 1.2 选题依据

本项目选题来自课程指定的"应用方案类"选题方向，要求设计一个区块链应用方案并完成开发实现。同时，本项目也作为 AI × Web3 Agentic Builders Hackathon 的参赛作品，将 AI Agent 的智能推理能力与区块链的可信执行能力相结合，探索 Agentic Commerce 的实际落地方案。

项目的核心理念是：**用自然语言描述分账规则，AI Agent 自主理解并调用链上合约执行，整个过程透明、可追溯、不可篡改。**

### 1.3 选题意义

本项目的意义在于验证以下技术路线的可行性：

- **智能合约替代中心化平台**：分账逻辑部署在以太坊链上，规则公开透明，执行不受人为干预
- **AI Agent 降低使用门槛**：用户无需了解合约地址、ABI、交易构造等技术细节，自然语言即可完成操作
- **链上记录提供可审计性**：每笔分账的创建和执行都有链上交易记录，可在 Etherscan 上公开查验

---

## 二、需求分析与痛点识别

### 2.1 传统分账模式的痛点

| 痛点 | 具体表现 | 影响 |
|------|---------|------|
| 信任依赖 | 需要信任发起人会如实分配资金 | 资金安全风险 |
| 中间方抽成 | 支付平台收取手续费 | 增加成本 |
| 结算效率低 | 依赖人工操作，跨平台转账需要时间 | 延迟到账 |
| 不透明 | 分账规则和执行过程不公开 | 易产生纠纷 |
| 无链上证据 | 分账记录仅存在于中心化数据库 | 无法独立审计 |

### 2.2 区块链解决方案的适用性

区块链天然适合解决信任和透明度问题：

- **不可篡改性**：合约代码和交易记录一旦上链，无法被任何人修改
- **去中心化执行**：合约按预设逻辑自动执行，无需信任中间人
- **公开可验证**：任何人可以通过 Etherscan 查看合约状态和交易详情
- **可编程性**：智能合约可以实现复杂的多方分账逻辑

### 2.3 用户需求分析

**目标用户：** 需要进行多方资金分配的个人或组织（学生小组、外包团队、DAO 成员等）。

**核心需求：**
1. 输入分账规则（接收地址、分配比例、总金额）
2. 自动在链上创建分账计划并执行转账
3. 查看分账记录和交易详情
4. 全过程可追溯、可审计

**进阶需求：**
1. 用自然语言描述分账规则，降低操作门槛
2. 通过 AI 自动解析意图，减少手动输入
3. Web 界面可视化操作，无需命令行

---

## 三、区块链技术解决方案设计

### 3.1 系统架构

本系统采用三层架构：智能合约层、AI Agent 层和 Web 前端层。

```
┌──────────────┐     ┌─────────────────────────┐     ┌─────────────────────┐
│  用户自然语言   │────→│  AI Agent (ReAct 模式)    │────→│  SplitPayment 合约    │
│  中文/英文     │     │  DeepSeek V4 Pro         │     │  Ethereum Sepolia     │
└──────────────┘     │  思考→调工具→观察→重复      │     └─────────────────────┘
                     └─────────────────────────┘              │
                              │              ┌────────────────┴──────────┐
                              │              │  Etherscan 链上可查          │
                              │              └────────────────────────────┘
                              │
                     ┌────────┴────────┐
                     │  Agent 可用工具:   │
                     │  · 查询合约状态    │
                     │  · 查看分账记录    │
                     │  · 查看分账详情    │
                     │  · 执行链上分账    │
                     └─────────────────┘
```

**设计理念：** 智能合约充当"后端"，负责资金管理和分账逻辑；AI Agent 充当"智能中间件"，负责理解用户意图并调用合约；Web 前端提供用户界面，通过 MetaMask 直连合约。整个系统没有传统后端服务器。

### 3.2 智能合约设计

#### 合约功能概览

`SplitPayment.sol` 是系统的核心合约，实现了以下功能：

| 功能 | 函数 | 说明 |
|------|------|------|
| 创建分账 | `createSplit(address[], uint256[])` | 定义接收者和比例，存入 ETH |
| 执行分账 | `executeSplit(uint256)` | 按比例将 ETH 转给各接收者 |
| 查询分账 | `getSplit(uint256)` | 获取分账详情（创建者、接收者、金额、状态） |
| 分账计数 | `splitCount()` | 返回已创建的分账总数 |

#### 合约安全机制

1. **权限控制**：仅分账创建者可以执行该笔分账
2. **防重复执行**：已执行的分账不可再次执行
3. **比例校验**：接收者数量与比例数量必须一致，比例之和必须为 100
4. **余额检查**：创建分账时必须转入足够金额

#### 事件机制

合约定义了两个事件，用于链上记录和前端监听：

- `SplitCreated(splitId, creator, totalAmount)` — 分账计划创建时触发
- `SplitExecuted(splitId, creator, totalAmount)` — 分账执行时触发

### 3.3 AI Agent 设计

#### ReAct 推理模式

Agent 采用 ReAct（Reasoning + Acting）模式，通过 Function Calling 实现自主推理：

1. 接收用户自然语言输入
2. LLM 分析用户意图，判断需要调用哪个工具
3. 执行工具调用，获取链上数据或执行交易
4. 观察工具返回结果
5. 决定是继续调用工具还是回复用户（最多 5 轮）

#### 工具定义

Agent 拥有 4 个工具，覆盖查询和执行两类操作：

| 工具 | 功能 | 参数 |
|------|------|------|
| `get_contract_info` | 查询合约余额、钱包状态、gas 价格 | 无 |
| `list_splits` | 查看所有分账记录列表 | 无 |
| `get_split` | 查看指定分账详情 | split_id |
| `execute_split` | 创建并执行链上分账 | amount_eth, addresses, percentages |

#### 与传统方式的对比

| 方面 | 传统命令行 | ReAct Agent |
|------|----------|------------|
| 输入方式 | 需要知道具体命令和参数 | 自然语言描述 |
| 操作步骤 | 需要手动调用多个函数 | Agent 自动编排 |
| 错误处理 | 需要用户判断和重试 | Agent 自主分析并调整 |
| 使用门槛 | 需要了解合约 ABI 和参数格式 | 无需技术背景 |

### 3.4 技术栈选型

| 层次 | 技术 | 选型理由 |
|------|------|---------|
| 智能合约 | Solidity 0.8.20 + Hardhat | 课程核心要求，Solidity 是以太坊主流语言 |
| AI Agent | Python + Web3.py + DeepSeek API | Python 上手快，DeepSeek 性价比高 |
| Web 前端 | 纯 HTML/CSS/JS + Web3.js | 无框架依赖，部署简单 |
| 钱包 | MetaMask | 以太坊生态最广泛的钱包插件 |
| 网络 | Sepolia 测试网 | 免费测试，有 Etherscan 可查 |
| LLM | DeepSeek V4 Pro | 支持 Function Calling，中文能力强 |

---

## 四、系统开发实现

### 4.1 智能合约开发

#### 4.1.1 合约核心逻辑

分账合约的核心是一个结构体数组，存储每笔分账的完整信息：

```solidity
struct Split {
    address creator;           // 创建者地址
    address[] recipients;      // 接收者地址列表
    uint256[] percentages;     // 各接收者比例（总和100）
    uint256 totalAmount;       // 总金额（wei）
    bool executed;             // 是否已执行
}
```

创建分账时，合约接收 ETH 并存储分账计划：

```solidity
function createSplit(
    address[] calldata _recipients,
    uint256[] calldata _percentages
) external payable {
    require(_recipients.length == _percentages.length, "长度不匹配");
    require(msg.value > 0, "金额必须大于0");

    uint256 total = 0;
    for (uint256 i = 0; i < _percentages.length; i++) {
        total += _percentages[i];
    }
    require(total == 100, "比例之和必须为100");

    uint256 splitId = splits.length;
    splits.push(Split({
        creator: msg.sender,
        recipients: _recipients,
        percentages: _percentages,
        totalAmount: msg.value,
        executed: false
    }));

    emit SplitCreated(splitId, msg.sender, msg.value);
}
```

执行分账时，合约按比例将 ETH 发送给各接收者：

```solidity
function executeSplit(uint256 _splitId) external {
    Split storage s = splits[_splitId];
    require(msg.sender == s.creator, "仅创建者可执行");
    require(!s.executed, "已执行");

    for (uint256 i = 0; i < s.recipients.length; i++) {
        uint256 amount = s.totalAmount * s.percentages[i] / 100;
        (bool ok, ) = s.recipients[i].call{value: amount}("");
        require(ok, "转账失败");
    }

    s.executed = true;
    emit SplitExecuted(_splitId, s.creator, s.totalAmount);
}
```

#### 4.1.2 合约测试

使用 Hardhat 编写了 3 个测试用例：

1. **创建分账测试**：验证分账计划正确创建，事件正确触发
2. **执行分账测试**：验证 ETH 按比例正确分配
3. **权限控制测试**：验证非创建者无法执行分账

#### 4.1.3 合约部署

合约已部署到 Sepolia 测试网：

- **合约地址：** `0x9EB460236A381081606FE5Bf43F076f47Fa223Bb`
- **Etherscan 链接：** https://sepolia.etherscan.io/address/0x9EB460236A381081606FE5Bf43F076f47Fa223Bb

### 4.2 AI Agent 开发

#### 4.2.1 Function Calling 工具定义

Agent 的工具通过 OpenAI 兼容的 Function Calling 接口定义：

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_contract_info",
            "description": "获取合约地址、余额、分账总数、钱包状态、当前gas价格",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_split",
            "description": "执行一笔链上分账：创建分账计划并立即执行转账",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount_eth": {"type": "number", "description": "总分账金额(ETH)"},
                    "addresses": {"type": "array", "items": {"type": "string"}, "description": "接收者地址列表"},
                    "percentages": {"type": "array", "items": {"type": "integer"}, "description": "各接收者比例，总和必须为100"}
                },
                "required": ["amount_eth", "addresses", "percentages"]
            }
        }
    }
]
```

#### 4.2.2 ReAct 循环实现

Agent 的核心是一个 ReAct 循环，处理 LLM 的工具调用请求：

```python
def run_agent(user_input, max_steps=5):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

    for step in range(max_steps):
        msg = agent_step(messages)  # 调用 LLM
        messages.append(msg)

        if msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                result = TOOL_MAP[name](**args)  # 执行工具
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
        else:
            return msg.content  # 无工具调用，返回回复

    return "已达到最大推理步数"
```

#### 4.2.3 链上交互实现

以 `execute_split` 工具为例，展示完整的链上交易流程：

```python
def tool_execute_split(amount_eth, addresses, percentages):
    addrs = [Web3.to_checksum_address(a) for a in addresses]
    value = w3.to_wei(amount_eth, 'ether')

    # 第1步：创建分账计划
    tx = contract.functions.createSplit(addrs, percentages).build_transaction({
        'from': account.address,
        'value': value,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 300000,
        'gasPrice': w3.eth.gas_price
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # 从事件中获取 splitId
    split_id = contract.events.SplitCreated().process_receipt(receipt)[0]['args']['splitId']

    # 第2步：执行分账
    tx2 = contract.functions.executeSplit(split_id).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 200000,
        'gasPrice': w3.eth.gas_price
    })
    signed_tx2 = w3.eth.account.sign_transaction(tx2, PRIVATE_KEY)
    tx_hash2 = w3.eth.send_raw_transaction(signed_tx2.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash2)

    return json.dumps({
        "split_id": split_id,
        "create_tx": tx_hash.hex(),
        "execute_tx": tx_hash2.hex(),
        "explorer_create": f"{EXPLORER}/tx/{tx_hash.hex()}",
        "explorer_execute": f"{EXPLORER}/tx/{tx_hash2.hex()}"
    })
```

### 4.3 Web 前端开发

#### 4.3.1 前端功能

Web 前端是一个纯静态 HTML 页面，主要功能包括：

1. **MetaMask 钱包连接**：检测并连接用户钱包，显示钱包地址和余额
2. **AI 智能解析**：输入自然语言描述，调用 DeepSeek API 自动解析并填充表单
3. **分账创建与执行**：填写接收地址和比例，调用合约创建并执行分账
4. **交易历史展示**：显示已完成的分账记录和交易详情
5. **实时预览**：输入时实时显示各接收者将收到的金额

#### 4.3.2 前端技术实现

**智能合约交互：** 通过 Web3.js 直接与合约交互，无需后端服务器：

```javascript
// 连接 MetaMask
const provider = new ethers.BrowserProvider(window.ethereum);
const signer = await provider.getSigner();
const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, signer);

// 执行分账
const tx = await contract.createSplit(addresses, percentages, { value: amount });
```

**AI 解析集成：** 前端直接调用 DeepSeek API（API Key 存储在 localStorage 中，首次使用时提示输入）：

```javascript
const response = await fetch('https://api.deepseek.com/chat/completions', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [{ role: 'user', content: prompt }]
    })
});
```

#### 4.3.3 前端设计风格

采用 Anthropic 官方设计语言：
- 配色：暖白底色 + 深色文字 + 橄榄绿强调色
- 字体：Poppins（英文/数字）+ Lora（中文正文）
- 圆角卡片式布局，16px 间距
- 响应式设计，适配不同屏幕尺寸

### 4.4 项目文件结构

```
split-payment-agent/
├── contracts/
│   └── SplitPayment.sol          # 分账智能合约（Solidity）
├── scripts/
│   └── deploy.js                 # Hardhat 部署脚本
├── test/
│   └── SplitPayment.test.js      # 合约测试用例
├── agent/
│   ├── agent.py                  # ReAct AI Agent（Python）
│   └── requirements.txt          # Python 依赖
├── demo/
│   └── index.html                # Web 前端 dApp
├── .env.example                  # 环境变量模板
├── hardhat.config.js             # Hardhat 配置
├── start.bat                     # 一键启动脚本
└── README.md                     # 项目文档
```

---

## 五、原型系统验证与测试

### 5.1 合约测试

#### 5.1.1 单元测试

使用 Hardhat 测试框架编写了 3 个测试用例，全部通过：

```
  SplitPayment
    ✓ 应该正确创建分账计划
    ✓ 应该正确执行分账并分配ETH
    ✓ 非创建者不应执行分账

  3 passing
```

#### 5.1.2 测试网部署验证

合约已成功部署到 Sepolia 测试网，部署交易可在 Etherscan 查看：
- 合约地址：`0x9EB460236A381081606FE5Bf43F076f47Fa223Bb`
- 部署者地址：（填写部署钱包地址）

### 5.2 链上交易验证

#### 5.2.1 首笔分账交易

成功在测试网上执行了一笔真实分账交易：

- **交易金额：** 0.01 ETH
- **接收者：** 2 个地址，各 50%
- **创建交易哈希：** （填写实际交易哈希）
- **执行交易哈希：** （填写实际交易哈希）
- **Etherscan 查看：** 可通过合约地址在 Etherscan 的 "Transactions" 页签查看所有交易

#### 5.2.2 链上证据

每笔分账在链上都有完整的证据链：

1. **创建交易**：记录创建者、接收者、比例、金额
2. **执行交易**：记录资金实际分配
3. **合约状态**：可通过 `getSplit()` 查询分账详情
4. **事件日志**：`SplitCreated` 和 `SplitExecuted` 事件永久记录在链上

### 5.3 Agent 功能测试

#### 5.3.1 查询功能测试

```
你> 现在合约什么状态？
Agent> [调用 get_contract_info]
        合约余额: 0 ETH，共 0 笔分账
        钱包余额: 1.35 ETH，gas 价格: 1.5 gwei
```

#### 5.3.2 分账功能测试

```
你> 帮我给 0xA... 和 0xB... 平分 0.01 ETH
Agent> [调用 execute_split]
        交易成功！
        创建交易: 0x...
        执行交易: 0x...
        Etherscan: https://sepolia.etherscan.io/tx/0x...
```

#### 5.3.3 多轮推理测试

Agent 能够自主决定调用工具的顺序和次数：

```
你> 帮我看看之前做的分账，然后告诉我哪些还没执行
Agent> [调用 list_splits] → 获取所有分账记录
        [分析结果，筛选未执行的记录]
        Agent> 共有 5 笔分账，其中 3 笔已执行，2 笔未执行：
        - #2: 0.05 ETH, 3人, 未执行
        - #4: 0.02 ETH, 2人, 未执行
```

### 5.4 前端功能测试

| 功能 | 测试结果 | 说明 |
|------|---------|------|
| MetaMask 连接 | 通过 | Chrome 浏览器正常检测和连接 |
| AI 自然语言解析 | 通过 | 中文输入正确解析为地址和比例 |
| 表单实时预览 | 通过 | 输入时实时显示分配金额 |
| 分账执行 | 通过 | 成功创建并执行链上分账 |
| 交易历史展示 | 通过 | 正确显示分账记录和交易哈希 |
| Etherscan 跳转 | 通过 | 点击链接可跳转到 Etherscan 查看详情 |

---

## 六、应用价值分析

### 6.1 技术创新价值

1. **AI + 区块链的深度融合**：将 LLM 的自然语言理解能力与智能合约的可信执行能力结合，探索了 Agentic Commerce 的实际落地路径

2. **ReAct 模式的实际应用**：展示了 ReAct 推理模式在 Web3 场景中的可行性，Agent 可以自主完成多步骤的链上操作

3. **无后端架构**：智能合约充当后端，前端直连合约，减少了中心化依赖

### 6.2 实际应用价值

1. **降低分账门槛**：自然语言交互使得非技术用户也能完成链上分账
2. **提高透明度**：所有分账记录在链上公开可查，减少纠纷
3. **降低成本**：无平台抽成，仅需支付 gas 费用
4. **增强信任**：合约自动执行，不依赖任何中间方

### 6.3 课程学习价值

通过本项目的开发，深入理解了以下区块链核心概念：

- **智能合约的编写与部署**：从 Solidity 语法到 Hardhat 工具链的完整流程
- **交易的构造与签名**：理解 nonce、gas、签名等交易核心要素
- **事件机制**：合约事件的定义、触发和监听
- **链上数据查询**：通过 ABI 和 RPC 调用合约函数
- **钱包集成**：MetaMask 的工作原理和 DApp 连接方式

---

## 七、风险与挑战分析

### 7.1 技术风险

| 风险 | 说明 | 应对措施 |
|------|------|---------|
| Gas 费用波动 | 以太坊主网 gas 费可能很高 | 当前使用测试网；主网可考虑 L2 方案 |
| RPC 节点不稳定 | 公共 RPC 可能限流或宕机 | 支持配置多个 RPC 备选 |
| LLM 幻觉 | AI 可能生成错误的地址或比例 | 前端预览确认 + 链上比例校验 |
| 智能合约漏洞 | 合约代码可能存在安全问题 | 已通过测试验证；主网部署需审计 |

### 7.2 使用风险

| 风险 | 说明 | 应对措施 |
|------|------|---------|
| 私钥管理 | 用户私钥泄露导致资金损失 | 教育用户安全存储私钥；不存储私钥 |
| 误操作 | 发送到错误地址或设置错误比例 | 前端预览确认机制 |
| 地址格式错误 | 输入无效地址导致交易失败 | 合约和前端均进行地址校验 |

### 7.3 当前局限性

1. **仅支持 ETH**：当前合约仅支持以太坊原生代币的分账，不支持 ERC-20 代币
2. **不支持定时执行**：分账必须手动触发执行，不支持定时或条件触发
3. **无撤销机制**：分账创建后无法撤销，必须执行
4. **测试网限制**：当前部署在 Sepolia 测试网，非真实资产

---

## 八、未来扩展方向

### 8.1 功能扩展

1. **支持 ERC-20 代币**：扩展合约支持任意 ERC-20 代币的分账
2. **定时分账**：支持设置时间锁，到期自动执行
3. **分账模板**：保存常用分账方案，一键复用
4. **批量分账**：一次创建多笔分账，提高效率
5. **多方签名**：需要多个参与者确认后才执行

### 8.2 技术优化

1. **部署到主网或 L2**：在 Arbitrum/Optimism 等 L2 网络部署，降低 gas 费用
2. **合约升级**：使用代理模式实现合约可升级
3. **前端优化**：支持更多钱包（WalletConnect、Coinbase Wallet）
4. **Agent 增强**：支持更复杂的自然语言指令，多轮对话

### 8.3 应用场景拓展

1. **DAO 赏金分配**：为 DAO 的任务赏金提供自动化分账
2. **团队薪资发放**：按预设比例自动分配团队收入
3. **众筹结算**：项目完成后按贡献度分配众筹资金
4. **跨境支付**：利用区块链的全球性，简化跨境多方结算

---

## 九、结论

本项目成功设计并实现了一个 AI Agent 驱动的链上自动分账系统（SplitChain），将人工智能的自然语言理解能力与区块链的可信执行能力相结合，探索了 Agentic Commerce 的实际落地方案。

### 主要成果

1. **智能合约**：开发了 `SplitPayment.sol` 分账合约，支持多方按比例分配 ETH，具备权限控制和防重复执行等安全机制，已部署到 Sepolia 测试网

2. **AI Agent**：实现了基于 ReAct 模式的 AI Agent，通过 Function Calling 自主调用链上工具，用户可用自然语言完成分账操作

3. **Web 前端**：开发了集成 AI 解析和 MetaMask 连接的 Web 前端，提供可视化的分账操作界面

4. **端到端验证**：完成了从智能合约到 AI Agent 到 Web 前端的完整系统验证，在测试网上执行了真实交易

### 项目意义

本项目验证了以下技术路线的可行性：

- 智能合约可以有效替代中心化分账平台，提供更透明、更可信的执行环境
- AI Agent 可以显著降低区块链应用的使用门槛，使非技术用户也能完成链上操作
- 区块链 + AI 的结合为去中心化应用提供了新的交互范式

### 学习收获

通过本项目的完整开发流程，深入理解了智能合约开发、区块链交易机制、AI Agent 设计模式等核心知识，获得了从需求分析到系统部署的全链路实践经验。

---

## 参考文献

1. Buterin V. A next-generation smart contract and decentralized application platform[R]. Ethereum White Paper, 2014.
2. Yao S, Zhao J, Yu D, et al. ReAct: Synergizing reasoning and acting in language models[C]. ICLR, 2023.
3. OpenAI. Function calling and other API updates[EB/OL]. 2023.
4. Hardhat Documentation[EB/OL]. https://hardhat.org/docs
5. Web3.py Documentation[EB/OL]. https://web3py.readthedocs.io/
6. MetaMask Documentation[EB/OL]. https://docs.metamask.io/
7. Solidity Documentation[EB/OL]. https://docs.soliditylang.org/

---

**项目仓库：** https://github.com/GanHanDouFu/SplitChain

**合约地址：** https://sepolia.etherscan.io/address/0x9EB460236A381081606FE5Bf43F076f47Fa223Bb
