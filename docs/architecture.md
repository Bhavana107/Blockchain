# PayGuard architecture

Customer and approvers interact through Streamlit. The application uses Web3.py to call the PayGuard smart contract on Ethereum Sepolia.

Components:
1. Customer deposits demo ERC-20 tokens.
2. MockUSDC represents test payment value and has no real-world value.
3. PayGuard stores escrow state, signer approvals, deadlines and terminal payment status.
4. Three preconfigured signers approve; two unique approvals trigger release to the merchant.
5. The original payer can claim a refund after expiry if the payment was not released.
6. PayGuard reads ETH/USD from the Chainlink Sepolia proxy through AggregatorV3Interface.

Payment lifecycle: Pending -> Released (2 of 3 approvals) OR Pending -> Refunded (payer after deadline).
