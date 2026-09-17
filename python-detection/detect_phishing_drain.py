"""
detect_phishing_drain.py  —  KYT alert generator (Rules R1 + R2)
----------------------------------------------------------------
WHAT IT DOES (business logic, not just mechanics):
  R1  Unlimited-approval watch:
        scan recent blocks for ERC-20 Approval(owner, spender, value=2^256-1)
        where the spender is a *contract* and the owner was a *fresh* wallet
        (nonce just before the approval is small).
  R2  Rapid-drain follow-through:
        within a time window after that approval, look for an ERC-20 Transfer
        with from == owner going to an address that is NOT the owner itself.
        That is the on-chain footprint of a third party calling transferFrom.

WHY THESE CHOICES (read this, it is the whole point of the exercise):
  * We generate *candidates for a human analyst*, not verdicts. Real KYT
    engines fire alerts and compliance analysts triage them. Offline we have
    no label database, so output stays "CANDIDATE - review".
  * "Fresh wallet" is measured by the owner's nonce AT THE BLOCK JUST BEFORE
    the approval (get_transaction_count(owner, block=approve_block-1)), not by
    the current nonce. A wallet that did this drain months ago has since sent
    more txs; using current nonce would wrongly say it is "old".
  * "Spender is a contract" = get_code length > 0. Legitimate infinite approvals
    go to DEX routers, so we keep a small KNOWN_ROUTERS exclude list to cut
    obvious false positives. A production system uses a full labelled database
    (Etherscan verified contracts / Chainalysis tags); here we approximate it.
  * We filter by events, not by replaying every tx: Approval/Transfer are the
    exact ERC-20 topics, so eth_getLogs is cheap and deterministic.
  * Time window is blocks, not wall-clock: ~12s/block, so DRAIN_WINDOW_BLOCKS=600
    is about 2 hours (the case drained in seconds; 2h is a safe upper bound).

USAGE:
    python detect_phishing_drain.py            # scan last 200 blocks
    python detect_phishing_drain.py 500        # scan last 500 blocks
    python detect_phishing_drain.py 200 900    # lookback, drain-window in blocks

Read-only. Uses the same Alchemy endpoint + local proxy as the other tools.
"""
import os
import sys
from datetime import datetime, timezone, timedelta

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

APPROVAL = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
MAX_UINT256 = 2 ** 256 - 1

# Heuristics (tune these; every threshold = a business decision, document it).
MAX_FRESH_NONCE = 5          # "fresh" = this few or fewer txs before the approval
DRAIN_WINDOW_BLOCKS = 600    # ~2h: how far after the approval we look for outflow
# Known, legitimate infinite-approval routers — exclude to cut false positives.
KNOWN_ROUTERS = {
    "0x111111125421cA6dc452d289314280a0f8842A65",  # 1inch AggregationRouter v6
    "0xDef1C0ded9bec7f1A160819833240f027b25EfF",    # 0x / ZeroEx ExchangeProxy
    "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45",    # Uniswap V3 SwapRouter
    "0xE592427A0AEce92De3Edee1F18E0157C05861564",    # Uniswap V3 SwapRouter old
}
BJ = timezone(timedelta(hours=8))


def hx(b):
    s = b.hex() if hasattr(b, "hex") else str(b)
    return s if s.startswith("0x") else "0x" + s


def pad32(addr):
    return "0x" + addr.lower().replace("0x", "").rjust(64, "0")


def addr_from_topic(t):
    return Web3.to_checksum_address("0x" + hx(t)[-40:])


def get_logs_chunked(from_block, to_block, topics, address=None):
    """eth_getLogs over a range, chunked because providers cap result size.
    Alchemy rejects an over-wide / too-large getLogs with HTTP 400, so we walk
    the range in CHUNK steps and halve a chunk on failure. This mirrors how a
    production collector pages logs instead of one giant query."""
    CHUNK = 50
    out, cur = [], from_block
    while cur <= to_block:
        end = min(cur + CHUNK - 1, to_block)
        size = CHUNK
        while size >= 1:
            try:
                req = {"fromBlock": hex(cur), "toBlock": hex(cur + size - 1), "topics": topics}
                if address:
                    req["address"] = address
                out.extend(w3.eth.get_logs(req))
                cur += size
                break
            except Exception as e:
                size //= 2                       # too big -> shrink and retry
                if size < 1:
                    print(f"  (skip {cur}..{cur+CHUNK-1}: {e})")
                    cur += CHUNK
                    break
    return out


def block_time(bn):
    blk = w3.eth.get_block(bn)
    return datetime.fromtimestamp(blk.timestamp, tz=timezone.utc)


def main(lookback, drain_window):
    latest = w3.eth.block_number
    from_block = latest - lookback
    print(f"Scanning blocks {from_block} .. {latest}  (~{lookback*12/60:.0f} min back)")
    print(f"R1: unlimited approve to a contract spender by a fresh wallet")
    print(f"R2: token outflow from owner within {drain_window} blocks after approval")
    print("=" * 78)

    logs = get_logs_chunked(from_block, latest, topics=[APPROVAL])
    print(f"Raw Approval events in window: {len(logs)}")

    # --- Step 2 (R1): keep only unlimited approvals, dedup ---
    candidates = {}
    for lg in logs:
        if len(lg.topics) < 3:
            continue
        owner = addr_from_topic(lg.topics[1])
        spender = addr_from_topic(lg.topics[2])
        amount = int(hx(lg.data), 16) if hx(lg.data) != "0x" else 0
        if amount != MAX_UINT256:
            continue                      # R1 core: only UNLIMITED approvals
        if spender.lower() in KNOWN_ROUTERS:
            continue                      # false-positive cut: known infra
        key = (owner.lower(), spender.lower(), lg.address.lower())
        if key not in candidates or lg.blockNumber < candidates[key][0]:
            candidates[key] = (lg.blockNumber, owner, spender, lg.address)

    print(f"Unlimited approvals (excluding known routers): {len(candidates)}")
    print("-" * 78)

    # Caches: many candidates share the same spender (routers) and even the same
    # owner. Cuts RPC calls by an order of magnitude when scanning wide ranges.
    code_cache = {}      # spender -> bool(is_contract)
    nonce_cache = {}     # (owner, block) -> pre_nonce

    def spender_is_contract(sp):
        if sp not in code_cache:
            try:
                code_cache[sp] = len(w3.eth.get_code(sp)) > 2
            except Exception:
                code_cache[sp] = False
        return code_cache[sp]

    def owner_pre_nonce(own, ablk):
        key = (own, ablk - 1)
        if key not in nonce_cache:
            try:
                nonce_cache[key] = w3.eth.get_transaction_count(own, block_identifier=ablk - 1)
            except Exception:
                nonce_cache[key] = 999
        return nonce_cache[key]

    # --- Step 3: filter to fresh owners + contract spenders; check R2 outflow ---
    hits = 0
    for (owner, spender, token), (ablock, _, _, _) in candidates.items():
        # 3b first (cached, cheap): spender must be a contract
        if not spender_is_contract(spender):
            continue

        # 3a. owner freshness: nonce at the block just BEFORE the approval
        pre_nonce = owner_pre_nonce(owner, ablock)
        if pre_nonce > MAX_FRESH_NONCE:
            continue

        # 3c (R2): any Transfer(from=owner) to a non-self address in the window?
        out_logs = get_logs_chunked(ablock, min(ablock + drain_window, latest),
                                    topics=[TRANSFER, pad32(owner)], address=token)
        outflow = []
        for ol in out_logs:
            if len(ol.topics) < 3:
                continue
            to = addr_from_topic(ol.topics[2])
            if to.lower() == owner.lower():
                continue                  # self-transfer, not a drain
            raw = int(hx(ol.data), 16) if hx(ol.data) != "0x" else 0
            outflow.append((ol.blockNumber, ol.transactionHash.hex(), to, raw))

        if not outflow:
            continue                      # approved but nothing taken yet

        hits += 1
        at = block_time(ablock).astimezone(BJ)
        first = min(outflow, key=lambda x: x[0])
        print(f"[CANDIDATE #{hits}] PHISHING-DRAIN PATTERN")
        print(f"  victim (owner)   : {owner}   (pre-approval nonce={pre_nonce})")
        print(f"  malicious spender: {spender}  (contract, infinite allowance)")
        print(f"  token            : {token}")
        print(f"  approve block    : {ablock}  ({at:%Y-%m-%d %H:%M:%S} Beijing)")
        for blk, th, to, raw in sorted(outflow)[:5]:
            ft = block_time(blk).astimezone(BJ)
            print(f"    outflow -> {to}  raw={raw}  blk={blk} ({ft:%H:%M:%S})  tx=0x{th[:16]}...")
        print(f"  => CANDIDATE, needs analyst review. Do NOT act automatically.")
        print("-" * 78)

    print(f"Done. Candidates flagged: {hits}.")
    if hits == 0:
        print("No candidate in this window — expected; infinite-approval drains are rare "
              "events. Re-run over a larger lookback if needed.")


if __name__ == "__main__":
    lookback = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    drain_window = int(sys.argv[2]) if len(sys.argv) > 2 else DRAIN_WINDOW_BLOCKS
    main(lookback, drain_window)
