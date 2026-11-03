# PayGuard setup — Windows

## Prerequisites
- Windows 10/11
- Python 3.10–3.12 recommended
- MetaMask browser extension
- Sepolia RPC URL from a provider such as Infura or Alchemy
- Fresh testnet-only accounts: customer, signer 1, signer 2, signer 3, merchant
- Sepolia test ETH for the deployer and every account submitting transactions

Never share private keys or seed phrases. Never use a wallet holding real assets.

## 1. Local Python setup
Extract/clone the repository, open it in VS Code, then run:

```powershell
py --version
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Configure MetaMask
Select Ethereum Sepolia (chain ID 11155111). Create fresh test-only accounts for the customer, three signers and merchant. Copy only the public addresses for deployment. Fund the deployer, customer and signers with Sepolia test ETH from a reputable faucet.

## 3. Deploy MockUSDC in Remix
1. Open https://remix.ethereum.org
2. Create MockUSDC.sol and paste contracts/MockUSDC.sol.
3. Compile with Solidity 0.8.20 or compatible 0.8.x.
4. In Deploy & Run, select Injected Provider - MetaMask and confirm Sepolia.
5. Deploy and save the token contract address.
6. Call mint(customerAddress, 1000000000) to mint 1,000 pUSD (6 decimals).

## 4. Deploy PayGuard
1. Create PayGuard.sol in Remix and paste contracts/PayGuard.sol.
2. Compile with Solidity 0.8.20 or compatible 0.8.x. Remix should resolve the version-pinned OpenZeppelin v5.0.2 raw GitHub imports.
3. Deploy using Injected Provider - MetaMask on Sepolia.
4. Constructor arguments:
   - tokenAddress: deployed MockUSDC address
   - feedAddress: 0x694AA1769357215DE4FAC081bf1f309aDC325306 (Chainlink ETH/USD Sepolia proxy; verify against current Chainlink documentation)
   - initialSigners: [signer1Address, signer2Address, signer3Address]
5. Save the PayGuard contract address.

Chainlink official address reference: https://docs.chain.link/data-feeds/api-reference

## 5. Export ABIs
In Remix Solidity Compiler, open compilation details for each compiled contract and copy the ABI JSON array:
- artifacts/PayGuard.abi.json
- artifacts/MockUSDC.abi.json

Replace the empty [] placeholders in those files. Do not paste bytecode.

## 6. Configure local secrets
Copy .streamlit/secrets.toml.example to .streamlit/secrets.toml and fill in:
- RPC_URL: your Sepolia HTTPS RPC endpoint
- CHAIN_ID: 11155111
- PAYGUARD_ADDRESS and TOKEN_ADDRESS
- CUSTOMER_PRIVATE_KEY
- SIGNER1_PRIVATE_KEY, SIGNER2_PRIVATE_KEY, SIGNER3_PRIVATE_KEY

Use only freshly created testnet accounts with no real assets. Keep secrets.toml local; it is gitignored. Never send keys to ChatGPT, commit them, or put them in screenshots.

## 7. Run Streamlit
```powershell
.venv\Scripts\activate
streamlit run app/app.py
```
Open the local URL printed in the terminal (usually http://localhost:8501).

## 8. Demo payment
1. Customer must hold pUSD.
2. Customer tab: enter merchant public address, amount (e.g. 25 pUSD), choose deadline and create payment. The app sends ERC-20 approval first if needed.
3. Record payment ID displayed after the PaymentCreated event.
4. Approvers tab: select signer1 and approve. It should show 1/2 and remain pending.
5. Select signer2 and approve. The second approval releases funds to merchant.
6. Merchant tab: load the payment and confirm Released.
7. Open transaction links in Sepolia Etherscan.

## 9. Refund demo
Create a second payment with a short expiry, wait until after deadline, then use the refund panel. Only the original payer can refund. For a fast demo, a separate local test chain with time manipulation can be used; do not weaken expiry checks in the deployed contract.

## Troubleshooting
- Missing ABI: export and replace the [] placeholders in artifacts/.
- Wrong network: use Sepolia, chain ID 11155111.
- Insufficient funds: the sender wallet needs Sepolia ETH for gas.
- NotAuthorizedSigner: the selected signer private key must match one of the three constructor addresses.
- InvalidPrice: feed may be unavailable or stale; inspect the official Chainlink feed documentation.
- RPC error: check endpoint URL, provider quota and network connectivity.

## Prototype limitations
This is an unaudited academic demo. Server-side private-key signing is only for a controlled testnet. Production should use browser-wallet signing or a secure signing service, governance for signer rotation, robust oracle monitoring, professional security review, and compliance integrations.
