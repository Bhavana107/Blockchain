# PayGuard — Multi-Signature Payment Gateway for Merchants

PayGuard is a FinTech + Blockchain academic prototype that holds a customer's ERC-20 test-token payment in escrow and releases it to a merchant only after 2 of 3 authorized merchant signers approve. If the approval deadline expires first, the original payer can claim a refund.

## Current repository contents
- `contracts/PayGuard.sol`: 2-of-3 approval escrow, ERC-20 safe transfers, expiry refunds, events and Chainlink ETH/USD read.
- `contracts/MockUSDC.sol`: mintable six-decimal demo token (no real value).
- `app/`: Streamlit interaction layer using Web3.py.
- `docs/`: architecture, security notes and manual test plan.
- `SETUP.md`: Windows, Remix, Sepolia and local app setup.
- `artifacts/`: ABI placeholders; replace with compiled Remix ABIs before running Streamlit.

## Build status
Source scaffold is committed. Contract compilation, testnet deployment, ABI export, Streamlit end-to-end testing and demo recording are still to be completed and verified.

## Run the UI locally
After completing deployment and secrets setup in [SETUP.md](SETUP.md):

```powershell
py -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app/app.py
```

## Architecture
`Customer / Approvers -> Streamlit -> Web3.py -> PayGuard.sol -> MockUSDC`

`PayGuard.sol -> Chainlink ETH/USD Sepolia proxy (read-only price data)`

## Team split (2 students)
- Student 1: Remix compilation/deployment, Solidity review, test cases and Sepolia verification.
- Student 2: Streamlit/Web3.py UI, ABI/secrets configuration, documentation and demo recording.
- Both: review contract behavior, run acceptance tests and prepare the presentation.

## Evaluation mapping
| Criterion | Evidence |
|---|---|
| Blockchain / Solidity (25%) | ERC-20 escrow, structs, mappings, events, custom errors, 2-of-3 approvals |
| Deployment + real-time data (25%) | Sepolia deployment and Chainlink ETH/USD feed read |
| Security (15%) | Signer allowlist, duplicate prevention, SafeERC20, ReentrancyGuard, expiry checks |
| Collaboration / documentation (15%) | Shared GitHub branch, clear task split, README, architecture and security docs |
| FinTech / presentation (20%) | Merchant escrow problem and live transaction walkthrough |

## Safety
Testnet-only educational prototype. Not audited and not production ready. Never use real funds or production private keys. Do not commit `.streamlit/secrets.toml`, private keys, seed phrases, or RPC credentials.

## Workflow
Work on `feature/payguard-mvp`; merge into `main` only after contract review, testing and deployment verification.
