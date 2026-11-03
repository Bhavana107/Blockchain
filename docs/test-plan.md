# Manual test plan

| ID | Action | Expected |
|---|---|---|
| T01 | Deployer mints demo tokens to customer | Customer balance increases |
| T02 | Customer approves token and creates payment | Escrow holds tokens; PaymentCreated event emitted |
| T03 | Signer 1 approves | 1/2; payment remains pending |
| T04 | Signer 1 approves again | Reverts AlreadyApproved |
| T05 | Non-signer approves | Reverts NotAuthorizedSigner |
| T06 | Signer 2 approves | 2/2; funds released to merchant |
| T07 | Signer 3 approves after release | Reverts PaymentAlreadyFinalized |
| T08 | Non-payer tries refund | Reverts NotPayer |
| T09 | Payer refunds before deadline | Reverts DeadlineNotPassed |
| T10 | Payer refunds after deadline | Payer receives escrowed tokens |
| T11 | Read ETH/USD | Positive price and timestamp returned |
