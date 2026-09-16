"""Decode a 1inch AggregationRouter v6 `swap` call.

Layout of swap(address executor, SwapDescription desc, bytes permit, bytes data),
where SwapDescription is a static tuple of 7 words:
  srcToken, dstToken, srcReceiver, dstReceiver, amount, minReturnAmount, flags.
dstToken = 0x0...0 means NATIVE ETH. dstReceiver is the real payout address.
Token legs show in logs; the final native-ETH payout is an internal CALL with no
log, so the authoritative destination is read here from calldata.
"""
import os, sys
import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
s = requests.Session()
if os.getenv("PROXY_URL"):
    s.proxies = {"http": os.getenv("PROXY_URL"), "https": os.getenv("PROXY_URL")}
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL"), request_kwargs={"timeout": 60}, session=s))

def as_addr(word: bytes) -> str:
    return Web3.to_checksum_address(word[-20:])
def as_int(word: bytes) -> int:
    return int.from_bytes(word, "big")
def kind(addr: str, blk=None) -> str:
    code = w3.eth.get_code(addr, block_identifier=blk)
    return "CONTRACT" if code else "EOA(wallet)"

tx = w3.eth.get_transaction(sys.argv[1])
raw = bytes(tx.input)
print("to (router) :", tx.to)
print("selector    :", raw[:4].hex())
body = raw[4:]
words = [body[i:i+32] for i in range(0, len(body), 32)]
labels = ["executor", "desc.srcToken", "desc.dstToken", "desc.srcReceiver",
          "desc.dstReceiver", "desc.amount", "desc.minReturn", "desc.flags",
          "offset.permit", "offset.data"]
for i, lab in enumerate(labels):
    if i >= len(words):
        break
    w = words[i]
    if "amount" in lab or "minReturn" in lab or "flags" in lab or "offset" in lab:
        print(f"{lab:18}: {as_int(w)}")
    else:
        a = as_addr(w)
        note = "NATIVE ETH" if int.from_bytes(w, 'big') == 0 else ""
        print(f"{lab:18}: {a}  {note}")

dst = as_addr(words[4])
print("-" * 60)
print("REAL PAYOUT (dstReceiver):", dst, "->", kind(dst))
b, b0 = tx.blockNumber, tx.blockNumber - 1
bal_now = w3.eth.get_balance(dst, block_identifier=b)
bal_pre = w3.eth.get_balance(dst, block_identifier=b0)
print(f"ETH balance of dstReceiver: block {b0}: {bal_pre/1e18:.6f} -> block {b}: {bal_now/1e18:.6f}  (delta {(bal_now-bal_pre)/1e18:+.6f})")
