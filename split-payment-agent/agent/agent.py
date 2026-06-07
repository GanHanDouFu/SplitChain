"""
SplitChain AI Agent — ReAct pattern with function calling.
LLM (DeepSeek) autonomously plans, calls tools, observes results, and responds.
"""

import json, sys, os
from web3 import Web3
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
EXPLORER = "https://sepolia.etherscan.io"

ABI = json.loads("""[{"inputs":[{"internalType":"address[]","name":"_recipients","type":"address[]"},{"internalType":"uint256[]","name":"_percentages","type":"uint256[]"}],"name":"createSplit","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_splitId","type":"uint256"}],"name":"executeSplit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_splitId","type":"uint256"}],"name":"getSplit","outputs":[{"internalType":"address","name":"creator","type":"address"},{"internalType":"address[]","name":"recipients","type":"address[]"},{"internalType":"uint256[]","name":"percentages","type":"uint256[]"},{"internalType":"uint256","name":"totalAmount","type":"uint256"},{"internalType":"bool","name":"executed","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"splitCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"splitId","type":"uint256"},{"indexed":true,"internalType":"address","name":"creator","type":"address"},{"indexed":false,"internalType":"uint256","name":"totalAmount","type":"uint256"}],"name":"SplitCreated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"splitId","type":"uint256"},{"indexed":true,"internalType":"address","name":"creator","type":"address"},{"indexed":false,"internalType":"uint256","name":"totalAmount","type":"uint256"}],"name":"SplitExecuted","type":"event"}]""")

# ── C ──
class C:
    B='\033[1m';D='\033[2m';G='\033[92m';Y='\033[93m';R='\033[91m';C='\033[96m';P='\033[95m';E='\033[0m'


# ── Global state ──
w3 = None; account = None; contract = None; client = None


# ── Tools (callable by Agent) ──
def tool_get_contract_info():
    """Get contract address, balance, split count, gas price."""
    bal = w3.from_wei(w3.eth.get_balance(CONTRACT_ADDRESS), 'ether')
    cnt = contract.functions.splitCount().call()
    wbal = w3.from_wei(w3.eth.get_balance(account.address), 'ether')
    gas = w3.from_wei(w3.eth.gas_price, 'gwei')
    return json.dumps({"contract_address":CONTRACT_ADDRESS,"contract_balance_eth":float(bal),"total_splits":cnt,"wallet_address":account.address,"wallet_balance_eth":float(wbal),"gas_price_gwei":float(gas)},ensure_ascii=False)

def tool_list_splits():
    """List all split records."""
    cnt = contract.functions.splitCount().call()
    if cnt==0: return "暂无分账记录"
    items=[]
    for i in range(min(cnt,20)):
        s=contract.functions.getSplit(i).call()
        items.append({"id":i,"amount_eth":float(w3.from_wei(s[3],'ether')),"recipient_count":len(s[1]),"executed":s[4],"creator":s[0]})
    return json.dumps(items,ensure_ascii=False)

def tool_get_split(split_id:int):
    """Get detail of a specific split by ID."""
    s=contract.functions.getSplit(split_id).call()
    amt=float(w3.from_wei(s[3],'ether'))
    recs=[]
    for a,p in zip(s[1],s[2]):
        recs.append({"address":a,"percentage":p,"amount_eth":round(amt*p/100,6)})
    return json.dumps({"id":split_id,"amount_eth":amt,"executed":s[4],"creator":s[0],"recipients":recs},ensure_ascii=False)

def tool_execute_split(amount_eth:float, addresses:list, percentages:list):
    """Create and execute a payment split. Returns tx hashes."""
    addrs=[Web3.to_checksum_address(a) for a in addresses]
    v=w3.to_wei(amount_eth,'ether')
    # create
    tx=contract.functions.createSplit(addrs,percentages).build_transaction({'from':account.address,'value':v,'nonce':w3.eth.get_transaction_count(account.address),'gas':300000,'gasPrice':w3.eth.gas_price})
    stx=w3.eth.account.sign_transaction(tx,PRIVATE_KEY)
    h1=w3.eth.send_raw_transaction(stx.raw_transaction)
    r1=w3.eth.wait_for_transaction_receipt(h1)
    sid=contract.events.SplitCreated().process_receipt(r1)[0]['args']['splitId']
    # execute
    tx2=contract.functions.executeSplit(sid).build_transaction({'from':account.address,'nonce':w3.eth.get_transaction_count(account.address),'gas':200000,'gasPrice':w3.eth.gas_price})
    stx2=w3.eth.account.sign_transaction(tx2,PRIVATE_KEY)
    h2=w3.eth.send_raw_transaction(stx2.raw_transaction)
    w3.eth.wait_for_transaction_receipt(h2)
    return json.dumps({"split_id":sid,"amount_eth":amount_eth,"recipient_count":len(addrs),"create_tx":h1.hex(),"execute_tx":h2.hex(),"explorer_create":f"{EXPLORER}/tx/{h1.hex()}","explorer_execute":f"{EXPLORER}/tx/{h2.hex()}"},ensure_ascii=False)


# ── Tool definitions for LLM ──
TOOLS = [
    {"type":"function","function":{"name":"get_contract_info","description":"获取合约地址、余额、分账总数、钱包状态、当前gas价格","parameters":{"type":"object","properties":{}}}},
    {"type":"function","function":{"name":"list_splits","description":"查看所有分账记录列表","parameters":{"type":"object","properties":{}}}},
    {"type":"function","function":{"name":"get_split","description":"查看某条分账的详细信息","parameters":{"type":"object","properties":{"split_id":{"type":"integer","description":"分账记录ID"}},"required":["split_id"]}}},
    {"type":"function","function":{"name":"execute_split","description":"执行一笔链上分账：创建分账计划并立即执行转账","parameters":{"type":"object","properties":{"amount_eth":{"type":"number","description":"总分账金额(ETH)"},"addresses":{"type":"array","items":{"type":"string"},"description":"接收者地址列表"},"percentages":{"type":"array","items":{"type":"integer"},"description":"各接收者比例，总和必须为100"}},"required":["amount_eth","addresses","percentages"]}}},
]

TOOL_MAP = {"get_contract_info":tool_get_contract_info,"list_splits":tool_list_splits,"get_split":tool_get_split,"execute_split":tool_execute_split}

SYSTEM_PROMPT = f"""你是 SplitChain 的 AI 分账助手。你可以使用工具完成以下操作：
- 查询合约状态、余额、分账记录
- 执行链上分账

请遵循 ReAct 模式：分析用户意图 → 调用工具 → 观察结果 → 继续推理或回复用户。

规则：
1. 如果用户请求分账但缺少地址或比例，主动追问
2. 执行分账后，返回交易哈希和 Etherscan 链接（数据在工具返回中）
3. 用中文回复，友好简洁
4. 用户问"帮我看看"、"现在什么情况"、"状态"等问题时，先查询信息再回答
5. 当前合约地址: {CONTRACT_ADDRESS}，钱包地址: {account.address if account else '未连接'}"""


def agent_step(messages):
    """One call to LLM with tools."""
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.1
    )
    return resp.choices[0].message


def run_agent(user_input, max_steps=5):
    """ReAct loop: think → act → observe → respond."""
    messages = [
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":user_input}
    ]

    for step in range(max_steps):
        msg = agent_step(messages)
        messages.append(msg)

        if msg.tool_calls:
            for tc in msg.tool_calls:
                fn = tc.function
                name = fn.name
                args = json.loads(fn.arguments) if fn.arguments else {}
                handler = TOOL_MAP.get(name)

                if handler:
                    print(f"  {C.D}调用工具: {name}({json.dumps(args,ensure_ascii=False)}){C.E}")
                    try:
                        if args:
                            result = handler(**args)
                        else:
                            result = handler()
                    except Exception as e:
                        result = f"工具执行失败: {e}"
                    print(f"  {C.D}结果: {result[:300]}{'...' if len(result)>300 else ''}{C.E}")
                else:
                    result = f"未知工具: {name}"

                messages.append({"role":"tool","tool_call_id":tc.id,"content":result})
        else:
            # No tool calls — LLM is responding to user
            return msg.content

    return "已达到最大推理步数，请重新描述你的需求。"


def print_banner():
    print(f"""
{C.C}╔══════════════════════════════════════════════════╗
║   SplitChain AI Agent — ReAct + Function Calling  ║
║   链上自动分账系统 · DeepSeek V4 Pro                 ║
╚══════════════════════════════════════════════════╝{C.E}""")


def main():
    global w3, account, contract, client, SYSTEM_PROMPT
    print_banner()

    if not DEEPSEEK_KEY:
        print(f"{C.R}错误: 请配置 DEEPSEEK_API_KEY{C.E}"); sys.exit(1)

    client = OpenAI(api_key=DEEPSEEK_KEY, base_url=DEEPSEEK_URL)
    print(f"{C.G}LLM 已就绪{C.E}")

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print(f"{C.R}错误: 无法连接 Sepolia{C.E}"); sys.exit(1)

    account = w3.eth.account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)
    SYSTEM_PROMPT = SYSTEM_PROMPT.replace("钱包地址: 未连接", f"钱包地址: {account.address}")

    bal = w3.from_wei(w3.eth.get_balance(account.address), 'ether')
    print(f"{C.G}已连接 Sepolia 测试网{C.E}")
    print(f"  钱包: {C.C}{account.address}{C.E}  余额: {bal:.4f} ETH")
    print(f"  合约: {C.C}{CONTRACT_ADDRESS}{C.E}")
    print(f"\n{C.D}我是你的分账助手。输入 help 看示例，或直接说需求。{C.E}\n")

    while True:
        try:
            ui = input(f"{C.B}{C.G}你>{C.E} ").strip()
            if not ui: continue
            if ui.lower() in ('quit','exit','q','退出'): print(f"{C.C}再见!{C.E}"); break
            if ui.lower() in ('clear','cls','清屏'): os.system('cls' if os.name=='nt' else 'clear'); continue
            if ui.lower() in ('help','帮助','h'): print(f"{C.D}直接跟我说话就行，比如'现在合约里有多少钱'、'帮我给两个地址平分0.01 ETH'{C.E}\n"); continue

            print(f"  {C.D}思考中...{C.E}")
            reply = run_agent(ui)
            print(f"\n{C.C}Agent:{C.E} {reply}\n")
        except KeyboardInterrupt:
            print(f"\n{C.C}再见!{C.E}"); break
        except Exception as e:
            print(f"{C.R}错误: {e}{C.E}")


if __name__ == "__main__":
    main()
