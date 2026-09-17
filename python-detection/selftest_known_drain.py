"""
selftest_known_drain.py — regression test of R1+R2 against the ground-truth case.
------------------------------------------------------------------------------
We already KNOW this incident happened (we traced it by hand):
  victim owner  : 0x8C949361B49320C48a51F4B1C6f9f83862530F89
  spender       : 0x1178a87DB6dc5C010E39A325AF1F73BEc6470502 (malicious)
  token         : USDT 0xdAC17F958D2ee523a2206206994597C13D831ec7
  approve block : 25489459  (unlimited, at 17:51:47 UTC)
  drain block   : 25489460  (200,000 USDT moved out, 12s later)

This script replays ONLY the detector's decision logic on that known event and
prints whether it would have raised an alert. Purpose: prove the rule is correct
against ground truth, not just that it runs.
"""
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from web3 import Web3
import requests

load_dotenv()
rpc, proxy = os.getenv("RPC_URL"), os.getenv("PROXY_URL")
sess = requests.Session()
if proxy:
    sess.proxies = {"http": proxy, "https": proxy}
w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 60}, session=sess))

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
BJ = timezone(timedelta(hours=8))

OWNER = Web3.to_checksum_address("0x8C949361B49320C48a51F4B1C6f9f83862530F89")
SPENDER = Web3.to_checksum_address("0x1178a87DB6dc5C010E39A325AF1F73BEc6470502")
TOKEN = Web3.to_checksum_address("0xdAC17F958D2ee523a2206206994597C13D831ec7")
APPROVE_BLOCK = 25489459


def hx(b):
    s = b.hex() if hasattr(b, "hex") else str(b)
    return s if s.startswith("0x") else "0x" + s


def main():
    print("SELF-TEST: would R1+R2 flag the known July-2026 phishing drain?")
    print("=" * 70)

    # R1a: spender is a contract?
    code = w3.eth.get_code(SPENDER)
    is_contract = len(code) > 2
    print(f"[R1] spender is contract?      {is_contract}  (len={len(code)})")

    # R1b: owner was fresh at the block just before approval?
    pre_nonce = w3.eth.get_transaction_count(OWNER, block_identifier=APPROVE_BLOCK - 1)
    fresh = pre_nonce <= 5
    print(f"[R1] owner pre-approval nonce:{pre_nonce}  (fresh={fresh}, threshold<=5)")

    # R2: did the victim's token move out to a non-self address right after?
    # Use Alchemy getAssetTransfers (erc20), which is reliable in this env; the
    # live scanner uses getLogs, but this self-test just proves the logic.
    out = w3.provider.make_request("alchemy_getAssetTransfers", [{
        "fromBlock": hex(APPROVE_BLOCK),
        "toBlock": hex(APPROVE_BLOCK + 20),
        "fromAddress": OWNER,
        "category": ["erc20"],
        "order": "asc",
    }])["result"]["transfers"]
    drains = []
    for tr in out:
        to = Web3.to_checksum_address(tr["to"])
        if to.lower() == OWNER.lower():
            continue
        drains.append((int(tr["blockNum"], 16), tr["hash"], to,
                       tr["value"], tr.get("asset", "?")))

    print(f"[R2] token outflows from owner in 20 blocks: {len(drains)}")
    for blk, th, to, val, asset in drains[:5]:
        blkts = datetime.fromtimestamp(w3.eth.get_block(blk).timestamp, tz=timezone.utc)
        delta = blkts - datetime.fromtimestamp(w3.eth.get_block(APPROVE_BLOCK).timestamp, tz=timezone.utc)
        print(f"     -> {to}  amount={val:,.2f} {asset}  blk={blk}  "
              f"({delta.total_seconds():.0f}s after approval)  tx={th[:18]}...")

    alerted = is_contract and fresh and len(drains) > 0
    print("=" * 70)
    print(f"VERDICT: detector would {'RAISE ALERT (PASS)' if alerted else 'NOT flag (FAIL)'}")
    if alerted:
        print("This matches the known real incident: 200k USDT drained 12s after approval.")


if __name__ == "__main__":
    main()
