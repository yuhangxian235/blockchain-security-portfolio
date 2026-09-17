"""
detect_peel_chain.py — detect automated layering via peel-chain structure.
==========================================================================
WHY THIS IS A STEP UP FROM R1/R2:
  R1/R2 flags a single event (approve -> immediate drain). A peel chain is a
  *graph structure*: a fresh node receives a large amount, then splits it into
  several *similar-sized* chunks to fresh child nodes, and each child may split
  again. We score that structure instead of a one-line threshold.

THE PEEL-CHAIN SCORE (0-8):
  +2  node is fresh / one-use        (current nonce small, e.g. <= 8)
  +2  splits into >= 2 chunks        (>= 2 distinct outgoing ETH destinations)
  +2  chunks are similar-sized       (coefficient of variation < 0.6)
  +2  recursion: a child also splits  (automation continues the pattern)
  >= 5 => likely automated peel-chain / layering.

DATA & LIMITS (be honest in the comments):
  * Uses Alchemy getAssetTransfers (ETH, external+internal) per node.
  * "Fresh" uses CURRENT nonce as a proxy. One-use mules are drained to ~0 and
    have tiny nonces, so it works here; for wallets that later reused funds this
    proxy weakens. A production version uses historical nonce at first outflow.
  * Depth limited to 2 to keep RPC calls bounded on a free tier.
  * No label DB: we cannot say "exchange/mixer", only "peel-chain behaviour".

USAGE:
    python detect_peel_chain.py [0xROOT_ADDRESS]
    default root = the known July-2026 mule 0x6040E865...
"""
import os
import sys
import statistics
from collections import defaultdict
from dotenv import load_dotenv
from web3 import Web3
import requests

load_dotenv()
rpc = os.getenv("RPC_URL")
proxy = os.getenv("PROXY_URL")
sess = requests.Session()
if proxy:
    sess.proxies = {"http": proxy, "https": proxy}
w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 60}, session=sess))

DEFAULT_ROOT = "0x6040E865152db6E833105D86d086fb7FA5b97534"
MAX_DEPTH = 2
MIN_CHUNK = 0.5          # ignore dust when detecting "chunks"
FRESH_NONCE = 8          # proxy: one-use mule
SIMILAR_CV = 0.6         # below this => chunks look auto-generated


def eth_out(addr):
    """All ETH value-bearing transfers OUT of addr (external+internal)."""
    out, page = [], None
    for _ in range(8):
        req = {"fromAddress": Web3.to_checksum_address(addr),
               "category": ["external", "internal"],
               "order": "asc", "excludeZeroValue": True, "maxCount": "0x3e8"}
        if page:
            req["pageKey"] = page
        r = w3.provider.make_request("alchemy_getAssetTransfers", [req])["result"]
        out.extend(r["transfers"])
        page = r.get("pageKey")
        if not page:
            break
    return [t for t in out if t.get("asset") == "ETH" and t.get("to")]


def is_fresh(addr):
    try:
        return w3.eth.get_transaction_count(Web3.to_checksum_address(addr)) <= FRESH_NONCE
    except Exception:
        return False


def split_chunks(addr):
    """Group outgoing ETH into (child -> amount). Filter dust."""
    children = defaultdict(float)
    for t in eth_out(addr):
        try:
            v = float(t["value"])
        except Exception:
            continue
        if v >= MIN_CHUNK:
            children[t["to"].lower()] += v
    return children


def score_node(addr, children):
    score, reasons = 0, []
    if is_fresh(addr):
        score += 2; reasons.append("fresh/one-use")
    vals = list(children.values())
    if len(vals) >= 2:
        score += 2; reasons.append(f"{len(vals)} chunks")
        mean = statistics.mean(vals)
        cv = (statistics.pstdev(vals) / mean) if mean else 9
        if cv < SIMILAR_CV:
            score += 2; reasons.append(f"similar (CV={cv:.2f})")
    return score, reasons


def walk(addr, depth, seen):
    addr = Web3.to_checksum_address(addr)
    indent = "  " * depth
    children = split_chunks(addr)
    score, reasons = score_node(addr, children)
    fresh = is_fresh(addr)
    print(f"{indent}- {addr}  nonce={w3.eth.get_transaction_count(addr)}  "
          f"out-chunks={len(children)}  peel-score={score}/8  [{', '.join(reasons)}]")
    for child, amt in sorted(children.items(), key=lambda kv: -kv[1]):
        print(f"{indent}    -> {child}  {amt:,.2f} ETH")
    # recurse into children only if this node itself looks like a peel
    if depth < MAX_DEPTH and score >= 4 and child not in seen:
        for child in children:
            if child not in seen:
                seen.add(child)
                walk(child, depth + 1, seen)


def main(root):
    print("PEEL-CHAIN / LAYERING DETECTOR")
    print(f"root: {root}   max depth={MAX_DEPTH}")
    print("=" * 72)
    seen = {root.lower()}
    walk(root, 0, seen)
    print("=" * 72)
    print("peel-score >= 5 => likely automated layering. "
          "Final exchange/mixer destination needs a labelled DB (out of scope).")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ROOT)
