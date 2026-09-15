"""
Lab tool: fully inspect one transaction from an Ethereum RPC.
Usage:  python inspect_tx.py 0xTXHASH
Prints: overview, decoded input, ERC20 Transfer/Approval logs, token metadata,
and (for a drain tx) the victim's earlier Approval to the spender.
Read-only.
"""
import os
import sys
from datetime import datetime, timezone, timedelta

import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
rpc = os.getenv("RPC_URL")
proxy = os.getenv("PROXY_URL")
session = requests.Session()
if proxy:
    session.proxies = {"http": proxy, "https": proxy}
w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 60}, session=session))

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
APPROVAL = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
SELECTORS = {
    "0x23b872dd": "transferFrom(address from,address to,uint256 amount)",
    "0x095ea7b3": "approve(address spender,uint256 amount)",
    "0xa9059cbb": "transfer(address to,uint256 amount)",
}
BJ = timezone(timedelta(hours=8))


def hx(b):
    s = b.hex() if hasattr(b, "hex") else str(b)
    return s if s.startswith("0x") else "0x" + s


def addr_from_topic(t):
    return Web3.to_checksum_address("0x" + hx(t)[-40:])


def _decode_token_string(raw):
    # Handles both ABI-encoded dynamic strings and fixed bytes32 (USDT uses bytes32).
    raw = bytes(raw)
    if not raw:
        return None
    if len(raw) == 32:
        return raw.rstrip(b"\x00").decode("utf-8", "ignore")
    try:
        length = int(raw[32:64].hex(), 16)
        return raw[64:64 + length].decode("utf-8", "ignore").strip("\x00")
    except Exception:
        return raw.rstrip(b"\x00").decode("utf-8", "ignore")


def _raw_static_call(addr, selector):
    return bytes(w3.eth.call({"to": Web3.to_checksum_address(addr), "data": selector}))


def token_meta(addr):
    # Raw eth_call with known selectors: decimals()=0x313ce567, symbol()=0x95d89b41, name()=0x06fdde03
    name = sym = "?"
    dec = 18
    try:
        dec = int(_raw_static_call(addr, "0x313ce567").hex(), 16)
    except Exception:
        pass
    try:
        sym = _decode_token_string(_raw_static_call(addr, "0x95d89b41")) or "?"
    except Exception:
        pass
    try:
        name = _decode_token_string(_raw_static_call(addr, "0x06fdde03")) or "?"
    except Exception:
        pass
    return str(name), str(sym), dec


def human(amount_raw, decimals):
    try:
        return f"{amount_raw / (10 ** int(decimals)):,.6f}".rstrip("0").rstrip(".")
    except Exception:
        return str(amount_raw)


def main(txhash):
    tx = w3.eth.get_transaction(txhash)
    rc = w3.eth.get_transaction_receipt(txhash)
    blk = w3.eth.get_block(tx.blockNumber)
    t_utc = datetime.fromtimestamp(blk.timestamp, tz=timezone.utc)
    print("=" * 70)
    print("TX OVERVIEW")
    print("hash        :", hx(tx.hash))
    print("status      :", "SUCCESS" if rc.status == 1 else "FAILED")
    print("block       :", tx.blockNumber)
    print("time (UTC)  :", t_utc.strftime("%Y-%m-%d %H:%M:%S"))
    print("time (Beijing):", t_utc.astimezone(BJ).strftime("%Y-%m-%d %H:%M:%S"))
    print("from (EOA)  :", tx["from"])
    print("to (contract):", tx.to)
    print("ETH value   :", w3.from_wei(tx.value, "ether"), "ETH")
    print("nonce       :", tx.nonce)
    print("gas used    :", rc.gasUsed, " / gasPrice:", w3.from_wei(tx.gasPrice, "gwei"), "gwei")
    print("fee (ETH)   :", w3.from_wei(rc.gasUsed * tx.gasPrice, "ether"))

    data = hx(tx.input)
    selector = data[:10]
    print("-" * 70)
    print("INPUT DATA")
    print("selector    :", selector, "->", SELECTORS.get(selector, "(unknown/other method)"))
    if selector in ("0x23b872dd", "0x095ea7b3", "0xa9059cbb"):
        body = data[10:]
        words = [body[i:i + 64] for i in range(0, len(body), 64)]
        if selector == "0x23b872dd":
            print("  from      :", Web3.to_checksum_address("0x" + words[0][24:]))
            print("  to        :", Web3.to_checksum_address("0x" + words[1][24:]))
            print("  amount    :", int(words[2], 16))
        elif selector == "0x095ea7b3":
            print("  spender   :", Web3.to_checksum_address("0x" + words[0][24:]))
            print("  amount    :", int(words[1], 16), "(2^256-1 = unlimited)")
        elif selector == "0xa9059cbb":
            print("  to        :", Web3.to_checksum_address("0x" + words[0][24:]))
            print("  amount    :", int(words[1], 16))

    print("-" * 70)
    print(f"LOGS ({len(rc.logs)} total)")
    victims = set()
    for lg in rc.logs:
        t0 = hx(lg.topics[0]).lower() if lg.topics else ""
        if t0 == TRANSFER and len(lg.topics) >= 3:
            frm, to = addr_from_topic(lg.topics[1]), addr_from_topic(lg.topics[2])
            raw = int(hx(lg.data), 16) if hx(lg.data) != "0x" else 0
            name, sym, dec = token_meta(lg.address)
            print(f"  [Transfer] token={sym} ({lg.address})  {frm} -> {to}  amount={human(raw, dec)} (raw {raw})")
            # the EOA that broadcast the drain tx is the receiver-side; the victim is 'from'
            if frm.lower() != tx["from"].lower():
                victims.add((frm, lg.address))
        elif t0 == APPROVAL and len(lg.topics) >= 3:
            owner = addr_from_topic(lg.topics[1]); spender = addr_from_topic(lg.topics[2])
            raw = int(hx(lg.data), 16)
            print(f"  [Approval] owner={owner} spender={spender} amount={raw}")
        else:
            print(f"  [other log] contract={lg.address} topic0={t0[:12]}")

    print("-" * 70)
    print("INTERNAL TXNS (value-bearing traces)")
    params = {"fromBlock": hex(tx.blockNumber), "toBlock": hex(tx.blockNumber),
              "fromAddress": tx["from"]}
    try:
        it = w3.provider.make_request("alchemy_getAssetTransfers",
                                      [{"fromBlock": hex(tx.blockNumber), "toBlock": hex(tx.blockNumber),
                                        "fromAddress": tx["from"], "category": ["internal", "external"],
                                        "excludeZeroValue": True}])["result"]["transfers"]
        for tr in it:
            if tr["hash"].lower() == txhash.lower():
                print(f"  {tr.get('from')} -> {tr.get('to')}  {tr.get('value')} {tr.get('asset')}")
    except Exception as e:
        print("  (internal lookup skipped:", repr(e), ")")

    # find the victim's earlier approve tx(s) by scanning txs SIGNED BY the victim
    print("-" * 70)
    print("EARLIER APPROVAL(S) BY VICTIM  (drain signer =", tx["from"], ")")
    drain_signer = tx["from"]
    for victim, token in victims:
        page_key, pages, found = None, 0, False
        while pages < 8:
            req = {"fromBlock": "0x0", "fromAddress": Web3.to_checksum_address(victim),
                   "category": ["external"], "order": "asc", "maxCount": "0x64",
                   "excludeZeroValue": False}
            if page_key:
                req["pageKey"] = page_key
            out = w3.provider.make_request("alchemy_getAssetTransfers", [req])["result"]
            for tr in out["transfers"]:
                if tr["blockNum"] >= hex(tx.blockNumber):
                    continue
                atx = w3.eth.get_transaction(tr["hash"])
                d = hx(atx.input)
                if d[:10].lower() != "0x095ea7b3":
                    continue
                if not atx.to or atx.to.lower() != token.lower():
                    continue
                body = d[10:]
                wd = [body[i:i + 64] for i in range(0, len(body), 64)]
                sp = Web3.to_checksum_address("0x" + wd[0][24:])
                amt = int(wd[1], 16)
                ablk = w3.eth.get_block(atx.blockNumber)
                at = datetime.fromtimestamp(ablk.timestamp, tz=timezone.utc).astimezone(BJ)
                _, sym, _ = token_meta(token)
                match = "  <== THIS IS THE DRAIN SIGNER" if sp.lower() == drain_signer.lower() else ""
                print(f"  victim approved spender={sp} on {sym} amount={amt}"
                      f"{' (UNLIMITED)' if amt > 10**30 else ''}{match}")
                print(f"    approve tx={hx(atx.hash)} block={atx.blockNumber} time={at:%Y-%m-%d %H:%M:%S} BJ")
                found = True
            page_key = out.get("pageKey")
            if not page_key:
                break
            pages += 1
        if not found:
            print("  no standard ERC20 approve found for", victim)


if __name__ == "__main__":
    main(Web3.to_checksum_address(sys.argv[1]) if len(sys.argv[1]) == 42 else sys.argv[1])
