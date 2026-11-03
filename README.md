# PayGuard — Multi-Signature Merchant Payment Gateway

PayGuard is a FinTech + Blockchain academic prototype. It holds a customer's ERC-20 test-token payment in escrow and releases the funds to a merchant only after 2 of 3 authorized merchant signers approve. If the approval deadline expires first, the original payer can claim a refund.

## Planned MVP
- Solidity escrow contract with ERC-20 test token support
- 2-of-3 multi-signature approval
- Automatic release after threshold
- Payer-only refund after expiry
- Chainlink ETH/USD price-feed read on Ethereum Sepolia
- Streamlit + Web3.py interaction layer
- Sepolia deployment, tests, and documentation

## Safety
This is a testnet-only educational prototype. It is not audited and must never be used with real funds or production private keys. Never commit secrets, seed phrases, or private keys.

## Repository workflow
Implementation will be developed on `feature/payguard-mvp` and merged into `main` after testing.

See `SETUP.md` for setup and deployment instructions.
