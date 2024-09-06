// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract LuckBank is Ownable {
    mapping(address => uint256) public luckStakingBalance;
    address[] public stakers;
    IERC20 public luckToken;
    mapping(address => uint256) public stakersRewards;

    constructor(address _luckTokenAddress) Ownable(msg.sender) {
        luckToken = IERC20(_luckTokenAddress);
    }

    function isStaker(address _address) internal view returns (bool) {
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
        return
            IERC20(luckToken).balanceOf(staker) /
            IERC20(luckToken).totalSupply();
    }

    function claimReward() public {
        //NEED TO PROTECT FROM REENTRENCY ATTACK
        uint256 reward = stakersRewards[msg.sender];
        luckToken.transfer(msg.sender, reward);
        stakersRewards[msg.sender] = 0;
    }

    function updateStakersRewards(uint256 earnings) public onlyOwner {
        for (
            uint16 stakersIndex = 0;
            stakersIndex < stakers.length;
            stakersIndex++
        ) {
            stakersRewards[stakers[stakersIndex]] +=
                earnings *
                getStakerShare(stakers[stakersIndex]);
        }
    }
}
