"""Focused hop-1 query: large USDT moves out of the hub in the first ~40 blocks after theft."""
import os
import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
proxy = os.getenv("PROXY_URL")
s = requests.Session()
if proxy:
    s.proxies = {"http": proxy, "https": proxy}
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL"), request_kwargs={"timeout": 60}, session=s))

HUB = Web3.to_checksum_address("0xf84c62572eeafc90c0bce3fb6c85bcb573e68d93")
USDT = "0xdac17f958d2ee523a2206206994597c13d831ec7"
START = 25489460
END = 25489500

for direction, field in (("IN", "toAddress"), ("OUT", "fromAddress")):
    res = w3.provider.make_request("alchemy_getAssetTransfers", [{
        "fromBlock": hex(START), "toBlock": hex(END), field: HUB,
        "category": ["erc20"], "order": "asc",
        "maxCount": "0x12c", "excludeZeroValue": True}])["result"]["transfers"]
    print("=" * 30, direction)
    for t in res:
        if t["rawContract"].get("address", "").lower() != USDT:
            continue
        amt = float(t["value"])
        if amt < 1000:  # skip dust
            continue
        cp = t["from"] if direction == "IN" else t["to"]
        tx = w3.eth.get_transaction(t["hash"])
        print(f"blk={int(t['blockNum'],16)} {amt:>14,.2f} USDT  cp={cp}")
        print(f"    tx={t['hash']}  signer={tx['from']}  callTo={tx.to}  selector={(tx.input.hex() if hasattr(tx.input,'hex') else str(tx.input))[:10]}")
