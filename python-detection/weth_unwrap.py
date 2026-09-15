"""Decode WETH Transfer/Deposit/Withdrawal logs in one tx -> find final native ETH receiver."""
import os, sys
import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
s = requests.Session()
if os.getenv("PROXY_URL"):
    s.proxies = {"http": os.getenv("PROXY_URL"), "https": os.getenv("PROXY_URL")}
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL"), request_kwargs={"timeout": 60}, session=s))

WETH = Web3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
def h(sig):
    x = Web3.keccak(text=sig).hex()
    return x if x.startswith("0x") else "0x" + x
TOPICS = {
    h("Transfer(address,address,uint256)"): "Transfer",
    h("Deposit(address,uint256)"): "Deposit",
    h("Withdrawal(address,uint256)"): "Withdrawal",
}
def addr(t):
    return Web3.to_checksum_address("0x" + t.hex()[-40:])

rcpt = w3.eth.get_transaction_receipt(sys.argv[1])
print("total logs:", len(rcpt.logs))
for i, lg in enumerate(rcpt.logs):
    print(i, str(lg["address"]), lg["topics"][0].hex()[:12])
print("-" * 50)
for lg in rcpt.logs:
    t0 = lg["topics"][0].hex()
    if not t0.startswith("0x"):
        t0 = "0x" + t0
    a = str(lg["address"]).lower()
    if "c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2" not in a:
        continue
    if t0 in TOPICS:
        kind = TOPICS[t0]
        if kind == "Transfer":
            print(f"WETH Transfer {int.from_bytes(lg['data'],'big')/1e18:.6f}  {addr(lg['topics'][1])} -> {addr(lg['topics'][2])}")
        elif kind == "Deposit":
            print(f"WETH Deposit  {int.from_bytes(lg['data'],'big')/1e18:.6f}  to {addr(lg['topics'][1])}")
        elif kind == "Withdrawal":
            src = addr(lg['topics'][1]); wad = int.from_bytes(lg['data'],'big')/1e18
            print(f"WETH Withdraw {wad:.6f}  unwrapped by {src} (this address receives native ETH)")
            code = w3.eth.get_code(src)
            print(f"   receiver {src} is {'a CONTRACT' if code else 'an EOA (plain wallet)'}; code len={len(code)}")
