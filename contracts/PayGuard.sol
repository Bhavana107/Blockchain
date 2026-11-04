// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IERC20} from "https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v5.0.2/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v5.0.2/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v5.0.2/contracts/utils/ReentrancyGuard.sol";

interface AggregatorV3Interface {
    function decimals() external view returns (uint8);
    function latestRoundData() external view returns (uint80,int256,uint256,uint256,uint80);
}

/// @title PayGuard
/// @notice Academic testnet prototype: ERC-20 escrow with 2-of-3 merchant approvals.
contract PayGuard is ReentrancyGuard {
    using SafeERC20 for IERC20;

    uint8 public constant REQUIRED_APPROVALS = 2;
    uint8 public constant SIGNER_COUNT = 3;
    uint256 public constant MIN_PAYMENT_DURATION = 10 minutes;
    uint256 public constant MAX_PAYMENT_DURATION = 30 days;
    uint256 public constant MAX_PRICE_AGE = 1 days;

    IERC20 public immutable paymentToken;
    AggregatorV3Interface public immutable ethUsdFeed;
    address[3] public signers;
    uint256 public nextPaymentId = 1;

    struct Payment {
        address payer;
        address merchant;
        uint256 amount;
        uint64 deadline;
        uint8 approvalCount;
        bool released;
        bool refunded;
    }

    mapping(uint256 => Payment) private payments;
    mapping(uint256 => mapping(address => bool)) public hasApproved;

    event PaymentCreated(uint256 indexed paymentId,address indexed payer,address indexed merchant,uint256 amount,uint64 deadline);
    event PaymentApproved(uint256 indexed paymentId,address indexed signer,uint8 approvalCount);
    event PaymentReleased(uint256 indexed paymentId,address indexed merchant,uint256 amount);
    event PaymentRefunded(uint256 indexed paymentId,address indexed payer,uint256 amount,uint256 refundedAt);

    error ZeroAddress();
    error InvalidSigners();
    error InvalidAmount();
    error InvalidDeadline();
    error NotAuthorizedSigner();
    error PaymentNotFound();
    error PaymentAlreadyFinalized();
    error ApprovalWindowClosed();
    error AlreadyApproved();
    error DeadlineNotPassed();
    error InvalidPrice();
    error TokenTransferFailed();

    constructor(address tokenAddress,address feedAddress,address[3] memory initialSigners) {
        if(tokenAddress==address(0)||feedAddress==address(0)) revert ZeroAddress();
        if(tokenAddress==address(this)) revert InvalidSigners();
        for(uint256 i=0;i<SIGNER_COUNT;i++){
            if(initialSigners[i]==address(0)) revert InvalidSigners();
            for(uint256 j=i+1;j<SIGNER_COUNT;j++){
                if(initialSigners[i]==initialSigners[j]) revert InvalidSigners();
            }
            signers[i]=initialSigners[i];
        }
        paymentToken=IERC20(tokenAddress);
        ethUsdFeed=AggregatorV3Interface(feedAddress);
    }

    modifier onlySigner(){
        bool authorized;
        for(uint256 i=0;i<SIGNER_COUNT;i++){ if(msg.sender==signers[i]){authorized=true;break;} }
        if(!authorized) revert NotAuthorizedSigner();
        _;
    }

    /// @notice Escrow `amount` tokens until `deadline`. Payer must have approved this contract.
    function createPayment(address merchant,uint256 amount,uint64 deadline) external nonReentrant returns(uint256 paymentId){
        if(merchant==address(0)||merchant==msg.sender) revert ZeroAddress();
        if(amount==0) revert InvalidAmount();
        if(deadline<=block.timestamp) revert InvalidDeadline();
        uint256 duration=deadline-block.timestamp;
        if(duration<MIN_PAYMENT_DURATION||duration>MAX_PAYMENT_DURATION) revert InvalidDeadline();

        // Pull funds first (reverts atomically on failure), then record state.
        paymentToken.safeTransferFrom(msg.sender,address(this),amount);

        paymentId=nextPaymentId;
        payments[paymentId]=Payment(msg.sender,merchant,amount,deadline,0,false,false);
        nextPaymentId=paymentId+1;
        emit PaymentCreated(paymentId,msg.sender,merchant,amount,deadline);
    }

    /// @notice Signer approves a pending payment; 2 approvals release funds to the merchant.
    function approvePayment(uint256 paymentId) external onlySigner nonReentrant {
        Payment storage p=payments[paymentId];
        if(p.payer==address(0)) revert PaymentNotFound();
        if(p.released||p.refunded) revert PaymentAlreadyFinalized();
        if(block.timestamp>p.deadline) revert ApprovalWindowClosed();
        if(hasApproved[paymentId][msg.sender]) revert AlreadyApproved();
        hasApproved[paymentId][msg.sender]=true;
        p.approvalCount+=1;
        emit PaymentApproved(paymentId,msg.sender,p.approvalCount);
        if(p.approvalCount>=REQUIRED_APPROVALS){
            p.released=true;
            paymentToken.safeTransfer(p.merchant,p.amount);
            emit PaymentReleased(paymentId,p.merchant,p.amount);
        }
    }

    /// @notice After the deadline passes with no release, anyone may trigger the refund
    ///         (payer, merchant or an arbiter) so funds never get stuck if the payer is inactive.
    function refundExpired(uint256 paymentId) external nonReentrant {
        Payment storage p=payments[paymentId];
        if(p.payer==address(0)) revert PaymentNotFound();
        if(p.released||p.refunded) revert PaymentAlreadyFinalized();
        if(block.timestamp<=p.deadline) revert DeadlineNotPassed();
        p.refunded=true;
        paymentToken.safeTransfer(p.payer,p.amount);
        emit PaymentRefunded(paymentId,p.payer,p.amount,block.timestamp);
    }

    function getPayment(uint256 paymentId) external view returns(Payment memory){
        Payment memory p=payments[paymentId];
        if(p.payer==address(0)) revert PaymentNotFound();
        return p;
    }

    function getSigners() external view returns(address[3] memory){ return signers; }

    /// @dev Returns a validated, fresh ETH/USD price. Reverts if stale, negative or zero.
    function getLatestEthUsdPrice() external view returns(int256 price,uint8 feedDecimals,uint256 updatedAt){
        (,price,,updatedAt,)=ethUsdFeed.latestRoundData();
        feedDecimals=ethUsdFeed.decimals();
        if(price<=0||updatedAt==0||updatedAt>block.timestamp+1 hours||block.timestamp-updatedAt>MAX_PRICE_AGE) revert InvalidPrice();
    }
}
