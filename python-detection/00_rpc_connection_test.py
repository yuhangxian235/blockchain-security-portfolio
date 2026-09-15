"""
Day-1 sanity check: connect to an Ethereum RPC and read basic chain info.
Read-only — it sends no transactions.

Setup (PowerShell), inside the python-detection folder:
    python -m venv .venv
    ./.venv/Scripts/Activate.ps1
    pip install -r requirements.txt
    copy .env.example .env   # paste your Alchemy URL; set PROXY_URL if direct link is unstable
    python 00_rpc_connection_test.py
"""

import os
import sys
import time

import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()  # reads RPC_URL and optional PROXY_URL from .env

rpc_url = os.getenv("RPC_URL")
if not rpc_url or "PASTE_YOUR_KEY" in rpc_url:
    sys.exit("RPC_URL missing: copy .env.example to .env and paste your Alchemy/Infura URL.")

# Direct links to overseas RPCs can be unstable on some networks; PROXY_URL is optional.
proxy_url = os.getenv("PROXY_URL")
session = requests.Session()
if proxy_url:
    session.proxies = {"http": proxy_url, "https": proxy_url}

w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 60}, session=session))


def call_with_retry(fn, retries=3, wait=2):
    last_err = None
    for i in range(retries):
        try:
            return fn()
        except Exception as err:  # noqa: BLE001 - report and retry transient network errors
            last_err = err
            print(f"  attempt {i + 1}/{retries} failed: {err!r}; retrying...")
            time.sleep(wait)
    raise last_err


block = call_with_retry(lambda: w3.eth.block_number)
print("connected      : True")
print("latest block   :", block)
print("chain id       :", call_with_retry(lambda: w3.eth.chain_id), "(1 = Ethereum mainnet)")

# Example: read ETH balance of a known address (Vitalik's wallet as a demo)
demo = Web3.to_checksum_address("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
print("demo balance   :", w3.from_wei(w3.eth.get_balance(demo), "ether"), "ETH")
print("proxy in use   :", proxy_url or "none (direct)")
print("RPC OK — environment ready for Week-3 data pulling.")
