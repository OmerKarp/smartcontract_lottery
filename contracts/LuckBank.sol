// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract LuckBank is Ownable {
    mapping(address => uint256) public luckStakingBalance;
    address[] public stakers;
    IERC20 public immutable luckToken;
    mapping(address => uint256) public stakersRewards;
    address public lotteryAddress;

    event Received(address indexed sender, uint256 amount);

    constructor(address _luckTokenAddress) Ownable(msg.sender) {
        luckToken = IERC20(_luckTokenAddress);
    }

    function setLotteryAddress(address _lotteryAddress) public onlyOwner {
        lotteryAddress = _lotteryAddress;
    }

    receive() external payable {
        emit Received(msg.sender, msg.value);
    }

    function isStaker(address _address) public view returns (bool) {
        for (uint i = 0; i < stakers.length; i++) {
            if (stakers[i] == _address) {
                return true;
            }
        }
        return false;
    }

    function stakeTokens(uint256 _amount) public {
        require(_amount > 0, "Amount must be more than 0");
        IERC20(luckToken).transferFrom(msg.sender, address(this), _amount);
        luckStakingBalance[msg.sender] += _amount;
        if (!isStaker(msg.sender)) {
            stakers.push(msg.sender);
        }
    }

    function unstakeTokens() public {
        //NEED TO PROTECT FROM REENTRENCY ATTACK
        uint256 balance = luckStakingBalance[msg.sender];
        require(balance > 0, "Staking balance cannot be 0");
        IERC20(luckToken).transfer(msg.sender, balance);
        luckStakingBalance[msg.sender] = 0;
        for (
            uint16 stakersIndex = 0;
            stakersIndex < stakers.length;
            stakersIndex++
        ) {
            if (stakers[stakersIndex] == msg.sender) {
                stakers[stakersIndex] = stakers[stakers.length - 1];
                stakers.pop();
            }
        }
    }

    function getStakerShare(address staker) public view returns (uint256) {
        uint256 totalStaked = IERC20(luckToken).balanceOf(address(this));
        if (totalStaked == 0) {
            return 0;
        }
        // Scale by 1e18 so we dont get 0 beacuse of solidity floor system
        return (luckStakingBalance[staker] * 1e18) / totalStaked;
    }

    function claimReward() public {
        //NEED TO PROTECT FROM REENTRENCY ATTACK
        uint256 reward = stakersRewards[msg.sender];
        require(reward > 0, "No rewards to claim");
        require(
            address(this).balance >= reward,
            "Insufficient balance in contract"
        );
        payable(msg.sender).transfer(reward);
        stakersRewards[msg.sender] = 0;
    }

    function updateStakersRewards(uint256 earnings) public {
        require(
            msg.sender == lotteryAddress,
            "Only the lottery contract can call the updateStakersRewards function!!"
        );

        for (
            uint16 stakersIndex = 0;
            stakersIndex < stakers.length;
            stakersIndex++
        ) {
            address staker = stakers[stakersIndex];
            uint256 scaledShare = getStakerShare(staker);

            // Calculate the reward for the staker
            if (scaledShare > 0) {
                // Multiply earnings by scaled share and divide by 1e18
                stakersRewards[staker] += (earnings * scaledShare) / 1e18;
            }
        }
    }
}
