"""Hop 2: native-ETH outflows from the hub after the swap (external + internal).
Token legs show in logs; native ETH moves show here. Filter dust, full hashes."""
import os
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
s = requests.Session()
if os.getenv("PROXY_URL"):
    s.proxies = {"http": os.getenv("PROXY_URL"), "https": os.getenv("PROXY_URL")}
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL"), request_kwargs={"timeout": 60}, session=s))

HUB = Web3.to_checksum_address("0xf84c62572eeafc90c0bce3fb6c85bcb573e68d93")
FROM_BLK = 25489482          # block of the 1inch swap
TO_BLK = "latest"
MIN_ETH = 1.0

def fetch(category):
    params = {"fromBlock": hex(FROM_BLK), "toBlock": TO_BLK, "fromAddress": HUB,
              "category": category, "order": "asc", "maxCount": "0x32", "excludeZeroValue": True}
    out = []
    while True:
        r = w3.provider.make_request("alchemy_getAssetTransfers", [params])["result"]
        out += r["transfers"]
        key = r.get("pageKey")
        if not key:
            break
        params["pageKey"] = key
    return out

seen = set()
blk_ts = {}
total_out = 0.0
for t in fetch(["external", "internal"]):
    val = float(t["value"] or 0)
    if val < MIN_ETH:
        continue
    h = t["hash"]
    if h in seen:
        continue
    seen.add(h)
    total_out += val
    blk = int(t["blockNum"], 16)
    if blk not in blk_ts:
        blk_ts[blk] = w3.eth.get_block(blk).timestamp
    tstr = datetime.fromtimestamp(blk_ts[blk], timezone.utc).strftime("%m-%d %H:%M")
    tx = w3.eth.get_transaction(h)
    print(f"blk{blk} {tstr} UTC  {val:>10.4f} ETH  ({t['category']})  -> {t['to']}")
    print(f"    tx {h}  signer={tx['from']}  callTo={tx['to']}  sel={(tx.input.hex() if hasattr(tx.input,'hex') else str(tx.input))[:10]}")
print("-" * 70)
print(f"total ETH out (>= {MIN_ETH}) since swap: {total_out:.4f}; hub balance now: {w3.eth.get_balance(HUB)/1e18:.4f} ETH")
