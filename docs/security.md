# Security considerations

Implemented:
- Fixed three-signer allowlist; constructor rejects zero and duplicate signer addresses.
- onlySigner modifier enforces signer authorization on-chain.
- Per-payment hasApproved mapping prevents duplicate approvals.
- Terminal released/refunded flags prevent double settlement.
- OpenZeppelin SafeERC20 and ReentrancyGuard protect token transfer flows.
- Checks-effects-interactions: state is updated before outgoing token transfer.
- Refund restricted to the original payer and only after expiry.
- Approval rejected after expiry.
- Amount, merchant, signer and deadline validation.
- Deadline bounded to 30 days.
- Chainlink answer must be positive, timestamped, not future-dated and no older than one day.

Limitations:
- Educational prototype; not audited and not production ready.
- Fixed signer set; no rotation, recovery, or governance flow.
- No KYC/AML provider. Wallet allowlisting is not identity verification.
- Streamlit server-side signing uses local testnet-only keys. Production should use wallet-side signing or secure custody.
- Oracle price is informational; no settlement amount conversion is performed.
- Demo token has no real value.
