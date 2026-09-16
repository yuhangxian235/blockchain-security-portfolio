"""Quick on-chain profile of an address: EOA/contract, balance, nonce, inbound senders.
Usage: python profile_address.py 0xADDR [0xADDR ...]"""
import os, sys
import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
s = requests.Session()
if os.getenv("PROXY_URL"):
    s.proxies = {"http": os.getenv("PROXY_URL"), "https": os.getenv("PROXY_URL")}
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL"), request_kwargs={"timeout": 60}, session=s))
latest = w3.eth.block_number
FROM = latest - 30000   # ~last 4 days window for inbound counting

for a in sys.argv[1:]:
    a = Web3.to_checksum_address(a)
    code = w3.eth.get_code(a)
    bal = w3.eth.get_balance(a) / 1e18
    nonce = w3.eth.get_transaction_count(a)
    print("=" * 70)
    print(a, "->", "CONTRACT" if code else "EOA(wallet)", f"codeLen={len(code)}")
    print(f"   ETH balance now: {bal:.4f}   nonce(outgoing tx count): {nonce}")
    params = {"fromBlock": hex(FROM), "toBlock": "latest", "toAddress": a,
              "category": ["external"], "order": "asc", "maxCount": "0x32", "excludeZeroValue": True}
    incoming, senders, pages = [], set(), 0
    while pages < 10:
        r = w3.provider.make_request("alchemy_getAssetTransfers", [params])["result"]
        incoming += r["transfers"]
        for t in r["transfers"]:
            senders.add(t["from"])
        if not r.get("pageKey"):
            break
        params["pageKey"] = r["pageKey"]; pages += 1
    print(f"   inbound ETH transfers(last ~4d, up to {len(incoming)} shown): unique senders = {len(senders)}")
    if len(senders) <= 8:
        for x in list(senders)[:8]:
            print("      sender:", x)
