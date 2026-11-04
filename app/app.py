import sys
from pathlib import Path
from datetime import datetime,timedelta,timezone
import streamlit as st
from web3 import Web3

sys.path.insert(0,str(Path(__file__).resolve().parent))
from chain import get_web3,get_contracts,get_account,send_transaction,explorer_link

st.set_page_config(page_title="PayGuard | Merchant Gateway",page_icon="🛡️",layout="wide")
st.title("🛡️ PayGuard")
st.caption("Multi-signature merchant payment gateway · Ethereum Sepolia testnet")

try:
    w3=get_web3()
    payguard,token=get_contracts(w3)
    decimals=token.functions.decimals().call()
    symbol=token.functions.symbol().call()
except Exception as exc:
    st.error(f"Configuration incomplete: {exc}")
    st.info("Follow SETUP.md. This prototype is testnet-only; never use real funds.")
    st.stop()

with st.sidebar:
    st.success(f"Connected · chain ID {w3.eth.chain_id}")
    st.write("Gateway:",payguard.address)
    st.write("Demo token:",token.address)
    st.caption("Do not use production private keys.")

tabs=st.tabs(["Customer · Create payment","Approvers · Approve","Merchant · Payment lookup","Chainlink · ETH/USD"])

def show_tx(tx_hash):
    st.success("Transaction confirmed.")
    st.markdown(f"[View transaction on Sepolia Etherscan]({explorer_link(tx_hash)})")

with tabs[0]:
    st.subheader("Create escrow payment")
    st.write("Customer deposits demo pUSD. Funds remain in escrow until two authorized signers approve.")
    try:
        customer=get_account("customer")
        bal=token.functions.balanceOf(customer.address).call()
        st.metric("Customer test-token balance",f"{bal/10**decimals:,.2f} {symbol}")
    except Exception as exc: st.warning(str(exc))
    with st.form("new_payment"):
        merchant=st.text_input("Merchant wallet address")
        amount=st.number_input(f"Amount ({symbol})",min_value=0.01,value=25.0,step=5.0)
        hours=st.selectbox("Approval deadline (hours)",[1,6,12,24,48],index=3)
        submit=st.form_submit_button("Approve token & create payment",type="primary")
    if submit:
        try:
            if not Web3.is_address(merchant): st.error("Enter a valid merchant address.")
            else:
                customer=get_account("customer")
                raw_amount=int(amount*10**decimals)
                deadline=int((datetime.now(timezone.utc)+timedelta(hours=hours)).timestamp())
                allowance=token.functions.allowance(customer.address,payguard.address).call()
                if allowance<raw_amount:
                    h,_=send_transaction(token.functions.approve(payguard.address,raw_amount),"customer")
                    st.write("Token allowance approved."); st.code(h)
                h,receipt=send_transaction(payguard.functions.createPayment(Web3.to_checksum_address(merchant),raw_amount,deadline),"customer")
                show_tx(h)
                events=payguard.events.PaymentCreated().process_receipt(receipt)
                if events: st.metric("Created payment ID",int(events[0]["args"]["paymentId"]))
        except Exception as exc: st.error(f"Payment creation failed: {exc}")

with tabs[1]:
    st.subheader("Authorized approver console")
    pid=st.number_input("Payment ID",min_value=1,step=1,value=1,key="approval_pid")
    role=st.selectbox("Signer account",["signer1","signer2","signer3"])
    try:
        signer=get_account(role)
        p=payguard.functions.getPayment(int(pid)).call()
        approved=payguard.functions.hasApproved(int(pid),signer.address).call()
        state="Released" if p[5] else ("Refunded" if p[6] else "Pending")
        a,b,c=st.columns(3)
        a.metric("Amount",f"{p[2]/10**decimals:,.2f} {symbol}")
        b.metric("Approvals",f"{p[4]}/2")
        c.metric("Status",state)
        st.write("Merchant:",p[1])
        st.write("Signer:",signer.address)
        if approved: st.info("This signer has already approved this payment.")
        if st.button("Approve payment",type="primary",disabled=(p[5] or p[6] or approved)):
            h,_=send_transaction(payguard.functions.approvePayment(int(pid)),role)
            show_tx(h); st.rerun()
    except Exception as exc: st.warning(f"Payment unavailable or signer setup incomplete: {exc}")

with tabs[2]:
    st.subheader("Merchant payment lookup")
    pid=st.number_input("Payment ID to inspect",min_value=1,step=1,value=1,key="lookup_pid")
    if st.button("Load payment"):
        try:
            p=payguard.functions.getPayment(int(pid)).call()
            state="Released" if p[5] else ("Refunded" if p[6] else "Pending")
            x,y,z=st.columns(3)
            x.metric("Amount",f"{p[2]/10**decimals:,.2f} {symbol}")
            y.metric("Approvals",f"{p[4]}/2")
            z.metric("Status",state)
            st.write("Payer:",p[0]); st.write("Merchant:",p[1])
            st.write("Deadline (UTC):",datetime.fromtimestamp(p[3],timezone.utc).isoformat())
        except Exception as exc: st.error(str(exc))
    st.divider()
    st.subheader("Refund expired payment")
    refund_id=st.number_input("Payment ID to refund",min_value=1,step=1,value=1,key="refund_pid")
    st.caption("Only the original payer can refund, and only after expiry.")
    if st.button("Refund using configured customer wallet"):
        try:
            h,_=send_transaction(payguard.functions.refundExpired(int(refund_id)),"customer")
            show_tx(h); st.rerun()
        except Exception as exc: st.error(f"Refund failed: {exc}")

with tabs[3]:
    st.subheader("Chainlink ETH/USD Data Feed")
    try:
        price,feed_decimals,updated=payguard.functions.getLatestEthUsdPrice().call()
        st.metric("ETH / USD",f"${price/10**feed_decimals:,.2f}")
        st.caption("On-chain Chainlink feed read from the Sepolia proxy.")
        st.caption("Last updated (UTC): "+datetime.fromtimestamp(updated,timezone.utc).isoformat())
        st.caption("Oracle price is informational in this MVP; escrow amounts are demo-token denominated.")
    except Exception as exc: st.error(f"Feed unavailable or stale: {exc}")

st.divider()
st.caption("Academic testnet prototype only. Not audited. Never use real assets or production keys.")
