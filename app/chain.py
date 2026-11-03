import json
from pathlib import Path
import streamlit as st
from web3 import Web3

ROOT=Path(__file__).resolve().parents[1]
ABI_DIR=ROOT/"artifacts"

def get_web3():
    rpc=st.secrets.get("RPC_URL","")
    if not rpc: raise RuntimeError("Add RPC_URL to .streamlit/secrets.toml")
    w3=Web3(Web3.HTTPProvider(rpc,request_kwargs={"timeout":30}))
    if not w3.is_connected(): raise RuntimeError("RPC connection failed.")
    expected=int(st.secrets.get("CHAIN_ID",11155111))
    if w3.eth.chain_id!=expected: raise RuntimeError(f"Wrong chain: expected {expected}, got {w3.eth.chain_id}.")
    return w3

def load_abi(filename):
    path=ABI_DIR/filename
    if not path.exists(): raise FileNotFoundError(f"Missing {path}. Export ABI from Remix.")
    data=json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data,dict) and "abi" in data: return data["abi"]
    if isinstance(data,list) and data: return data
    raise ValueError(f"{filename} is empty. Replace it with the compiled ABI JSON from Remix.")

def get_contracts(w3):
    payguard_addr=Web3.to_checksum_address(st.secrets["PAYGUARD_ADDRESS"])
    token_addr=Web3.to_checksum_address(st.secrets["TOKEN_ADDRESS"])
    pg=w3.eth.contract(address=payguard_addr,abi=load_abi("PayGuard.abi.json"))
    token=w3.eth.contract(address=token_addr,abi=load_abi("MockUSDC.abi.json"))
    return pg,token

def get_account(role):
    key=st.secrets.get(f"{role.upper()}_PRIVATE_KEY","")
    if not key: raise RuntimeError(f"Missing {role.upper()}_PRIVATE_KEY in local secrets.")
    return get_web3().eth.account.from_key(key)

def send_transaction(fn,role):
    w3=get_web3(); account=get_account(role)
    tx=fn.build_transaction({
        "from":account.address,
        "nonce":w3.eth.get_transaction_count(account.address,"pending"),
        "chainId":w3.eth.chain_id,
        "gas":700000,
        "gasPrice":w3.eth.gas_price
    })
    signed=account.sign_transaction(tx)
    raw=getattr(signed,"raw_transaction",None) or signed.rawTransaction
    tx_hash=w3.eth.send_raw_transaction(raw)
    receipt=w3.eth.wait_for_transaction_receipt(tx_hash,timeout=180)
    if receipt.status!=1: raise RuntimeError(f"Transaction reverted: {tx_hash.hex()}")
    return tx_hash.hex(),receipt

def explorer_link(tx_hash):
    return f"https://sepolia.etherscan.io/tx/{tx_hash}"
