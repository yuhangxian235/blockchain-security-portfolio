"""
Trace an address's asset flows (external ETH + ERC20) after a block.
Usage: python trace_address.py 0xADDRESS [start_block]
Reusable for fund-flow tracing. Read-only.
"""
import os
import sys
from datetime import datetime, timezone, timedelta

import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
proxy = os.getenv("PROXY_URL")
s = requests.Session()
if proxy:
    s.proxies = {"http": proxy, "https": proxy}
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL"), request_kwargs={"timeout": 60}, session=s))
BJ = timezone(timedelta(hours=8))

KNOWN = {
    "0xdac17f958d2ee523a2206206994597c13d831ec7": ("USDT", 6),
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": ("USDC", 6),
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": ("WETH", 18),
}
SELECTORS = {
    "0xa9059cbb": "transfer", "0x095ea7b3": "approve", "0x23b872dd": "transferFrom",
    "0x1249c58b": "mint?", "0x38ed1739": "swapExactTokensForETH",
    "0x7ff36ab5": "swapExactETHForTokens", "0x8803dbee": "swapTokensForExactTokens",
}
_tx_cache = {}


def token_meta(addr):
    if addr.lower() in KNOWN:
        return KNOWN[addr.lower()]
    def call(sel):
        return bytes(w3.eth.call({"to": Web3.to_checksum_address(addr), "data": sel}))
    sym, dec = "?", 18
    try:
        r = call("0x95d89b41")
        sym = (r[:32] if len(r) == 32 else r[64:64 + int(r[32:64].hex(), 16)]).decode("utf-8", "ignore").strip("\x00") or "?"
    except Exception:
        pass
    try:
        dec = int(call("0x313ce567").hex(), 16)
    except Exception:
        pass
    return sym, dec


def tx_meta(h):
    if h not in _tx_cache:
        try:
            t = w3.eth.get_transaction(h)
            inp = (t.input.hex() if hasattr(t.input, "hex") else str(t.input))
            inp = inp if inp.startswith("0x") else "0x" + inp
            _tx_cache[h] = (t["from"], t.to, inp[:10])
        except Exception:
            _tx_cache[h] = ("?", "?", "?")
    return _tx_cache[h]


def fetch(addr, category, start):
    out, key, pages = [], None, 0
    while pages < 6:
        req = {"fromBlock": hex(start), "toAddress" if False else "fromAddress": addr,
               "category": [category], "order": "asc", "maxCount": "0x64",
               "excludeZeroValue": True}
        # include both directions: query by fromAddress AND toAddress separately
        out.append((req, key))
        break
    return out


def flows(addr, start):
    rows, key, pages = [], None, 0
    for direction, field in (("OUT", "fromAddress"), ("IN", "toAddress")):
        k = None
        for _ in range(6):
            req = {"fromBlock": hex(start), field: addr, "category": ["external", "erc20"],
                   "order": "asc", "maxCount": "0x64", "excludeZeroValue": True}
            if k:
                req["pageKey"] = k
            res = w3.provider.make_request("alchemy_getAssetTransfers", [req])["result"]
            for t in res["transfers"]:
                rows.append(t)
            k = res.get("pageKey")
            if not k:
                break
    rows.sort(key=lambda t: (int(t["blockNum"], 16), t["hash"]))
    return rows


def main():
    addr = Web3.to_checksum_address(sys.argv[1])
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    print(f"flows for {addr} since block {start}\n")
    seen = set()
    for t in flows(addr, start):
        h = t["hash"]
        if h in seen and t["category"] == "external":
            pass
        ctr = t["rawContract"].get("address")
        if t["category"] == "erc20" and ctr:
            sym, dec = token_meta(ctr)
            try:
                amt = float(t["value"])
            except Exception:
                amt = t["value"]
            asset = sym
        else:
            asset, amt = t.get("asset", "ETH"), t["value"]
        direction = "OUT" if t["from"].lower() == addr.lower() else "IN "
        cp = t["to"] if direction == "OUT" else t["from"]
        signer, txto, sel = tx_meta(h)
        ts = t.get("metadata", {}).get("blockTimestamp", "")
        blk = int(t["blockNum"], 16)
        print(f"{ts[:19].replace('T',' ')} blk={blk} {direction} {str(amt):>18} {asset:<6} "
              f"cp={cp[:12]}..  tx={h[:14]}.. signer={signer[:12]}.. callTo={(txto or '?')[:12]}.. "
              f"{SELECTORS.get(sel.lower(), sel)}")


if __name__ == "__main__":
    main()
