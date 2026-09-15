"""
Day-1 sanity check: connect to an Ethereum RPC and read basic chain info.
Read-only — it sends no transactions.

Setup (PowerShell), inside the python-detection folder:
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    copy .env.example .env        # then edit .env and paste your Alchemy URL
    python 00_rpc_connection_test.py
"""

import os
import sys

from dotenv import load_dotenv
from web3 import Web3

load_dotenv()  # reads RPC_URL from .env

rpc_url = os.getenv("RPC_URL")
if not rpc_url or "PASTE_YOUR_KEY" in rpc_url:
    sys.exit("RPC_URL missing: copy .env.example to .env and paste your Alchemy/Infura URL.")

w3 = Web3(Web3.HTTPProvider(rpc_url))

if not w3.is_connected():
    sys.exit("Connection failed — check the RPC URL, network, or API key.")

print("connected      :", w3.is_connected())
print("chain id       :", w3.eth.chain_id, "(1 = Ethereum mainnet)")
print("latest block   :", w3.eth.block_number)

# Example: read ETH balance of any address (Vitalik's wallet as a demo)
demo = Web3.to_checksum_address("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
print("demo balance   :", w3.from_wei(w3.eth.get_balance(demo), "ether"), "ETH")
print("RPC OK — environment ready for Week-3 data pulling.")
