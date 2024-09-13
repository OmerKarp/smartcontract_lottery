from scripts.helpfull_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.deploy_luck_token import deploy_luck_token
from scripts.deploy_luck_bank import deploy_luck_bank
from brownie import exceptions, network, interface, web3 as Web3 
import pytest

def test_set_lottery_address():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only running on local blockchain environments")
    
    # Deploy contracts
    luck_token = deploy_luck_token()
    luck_bank = deploy_luck_bank()  # No need to pass luck_token.address here
    account = get_account()
    
    # Test setting the lottery address
    new_lottery_address = get_account(index=1).address
    luck_bank.setLotteryAddress(new_lottery_address, {'from': account})
    assert luck_bank.lotteryAddress() == new_lottery_address

def test_stake_tokens():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only running on local blockchain environments")
    
    # Deploy contracts
    luck_token = deploy_luck_token()
    luck_bank = deploy_luck_bank()  # No need to pass luck_token.address here
    account = get_account()
    stake_amount = Web3.to_wei(1000, 'ether')  # Converting to the token's decimals
    
    # Use the IERC20 interface to interact with the deployed contract
    erc20 = interface.IERC20(luck_token.address)
    
    # Approve LuckBank to spend tokens
    erc20.approve(luck_bank.address, stake_amount, {'from': account})
    
    # Stake tokens
    luck_bank.stakeTokens(stake_amount, {'from': account})
    
    # Check balance
    assert luck_bank.luckStakingBalance(account.address) == stake_amount

def test_unstake_tokens():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only running on local blockchain environments")
    
    # Deploy contracts
    luck_token = deploy_luck_token()
    luck_bank = deploy_luck_bank()  # No need to pass luck_token.address here
    account = get_account()
    stake_amount = Web3.to_wei(1000, 'ether')  # Converting to the token's decimals
    
    # Use the IERC20 interface to interact with the deployed contract
    erc20 = interface.IERC20(luck_token.address)

    # Approve LuckBank to spend tokens
    erc20.approve(luck_bank.address, stake_amount, {'from': account})
    
    # Stake tokens
    luck_bank.stakeTokens(stake_amount, {'from': account})
    
    initial_luck_amount = erc20.balanceOf(account.address)

    # Unstake tokens
    luck_bank.unstakeTokens({'from': account})
    
    assert luck_bank.luckStakingBalance(account.address) == 0
    assert erc20.balanceOf(account.address) == initial_luck_amount + stake_amount 

def test_claim_reward():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only running on local blockchain environments")
    
    # Deploy contracts
    luck_token = deploy_luck_token()
    luck_bank = deploy_luck_bank()  # No need to pass luck_token.address here
    account = get_account()
    
    # Use the IERC20 interface to interact with the deployed contract
    erc20 = interface.IERC20(luck_token.address)
    
    # Stake tokens to make the account a staker
    stake_amount = Web3.to_wei(1000, 'ether')
    erc20.approve(luck_bank.address, stake_amount, {'from': account})
    luck_bank.stakeTokens(stake_amount, {'from': account})

    # Set lottery address
    luck_bank.setLotteryAddress(account.address, {'from': account})

    # Send ETH to the contract
    earnings = Web3.to_wei(10, 'ether')
    account.transfer(luck_bank.address, earnings)

    # Set up a reward
    luck_bank.updateStakersRewards(earnings, {'from': account})

    # Check the contract's balance before claiming
    contract_balance_before = Web3.eth.get_balance(luck_bank.address)

    # Claim the reward
    initial_balance = Web3.eth.get_balance(account.address)
    luck_bank.claimReward({'from': account})
    final_balance = Web3.eth.get_balance(account.address)

    # Calculate the expected final balance
    expected_balance = initial_balance + earnings

    # Assert that the final balance is as expected
    assert final_balance == expected_balance

    # The contract's balance should have decreased by the reward amount
    assert Web3.eth.get_balance(luck_bank.address) == contract_balance_before - earnings

def test_claim_reward_two_stakers():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only running on local blockchain environments")

    # Deploy contracts
    luck_token = deploy_luck_token()
    luck_bank = deploy_luck_bank()  # No need to pass luck_token.address here
    account1 = get_account()
    account2 = get_account(index=1)
    
    # Use the IERC20 interface to interact with the deployed contract
    erc20 = interface.IERC20(luck_token.address)

    # Stake amounts for both accounts
    stake_amount_1 = Web3.to_wei(1000, 'ether')
    stake_amount_2 = Web3.to_wei(2000, 'ether')

    # Transfer tokens from account1 to account2 so account2 can stake
    erc20.transfer(account2.address, stake_amount_2, {'from': account1})

    # Account 1 stakes
    erc20.approve(luck_bank.address, stake_amount_1, {'from': account1})
    luck_bank.stakeTokens(stake_amount_1, {'from': account1})

    # Account 2 stakes
    erc20.approve(luck_bank.address, stake_amount_2, {'from': account2})
    luck_bank.stakeTokens(stake_amount_2, {'from': account2})

    # Log staker balances for debugging
    print(f"Account 1 Staking Balance: {luck_bank.luckStakingBalance(account1.address)}")
    print(f"Account 2 Staking Balance: {luck_bank.luckStakingBalance(account2.address)}")

    # Set lottery address
    luck_bank.setLotteryAddress(account1.address, {'from': account1})

    # Send ETH to the contract as earnings
    earnings = Web3.to_wei(15, 'ether')
    account1.transfer(luck_bank.address, earnings)

    # Set up a reward distribution
    luck_bank.updateStakersRewards(earnings, {'from': account1})

    # Log rewards for debugging
    print(f"Earnings: {Web3.eth.get_balance(luck_bank.address)}")
    print(f"Account 1 Reward Before Claim: {luck_bank.stakersRewards(account1.address)}")
    print(f"Account 2 Reward Before Claim: {luck_bank.stakersRewards(account2.address)}")

    # Calculate expected rewards
    total_staked = stake_amount_1 + stake_amount_2
    expected_reward_1 = (stake_amount_1 / total_staked) * earnings
    expected_reward_2 = (stake_amount_2 / total_staked) * earnings

    # Check the contract's balance before claiming
    contract_balance_before = Web3.eth.get_balance(luck_bank.address)

    # Claim rewards for both accounts
    initial_balance_1 = Web3.eth.get_balance(account1.address)
    luck_bank.claimReward({'from': account1})
    final_balance_1 = Web3.eth.get_balance(account1.address)
    reward_1 = final_balance_1 - initial_balance_1

    initial_balance_2 = Web3.eth.get_balance(account2.address)
    luck_bank.claimReward({'from': account2})
    final_balance_2 = Web3.eth.get_balance(account2.address)
    reward_2 = final_balance_2 - initial_balance_2

    # Assert that the final balances are as expected
    tolerance = Web3.to_wei(10, 'wei')  # Tolerance for floating-point precision
    assert abs(final_balance_1 - (initial_balance_1 + expected_reward_1)) < tolerance
    assert abs(final_balance_2 - (initial_balance_2 + expected_reward_2)) < tolerance

    # The contract's balance should have decreased by the reward amount
    assert Web3.eth.get_balance(luck_bank.address) == contract_balance_before - (reward_1 +reward_2)

def test_update_stakers_rewards():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only running on local blockchain environments")
    
    # Deploy contracts
    luck_token = deploy_luck_token()
    luck_bank = deploy_luck_bank()  # No need to pass luck_token.address here
    account = get_account()
    
    # Use the IERC20 interface to interact with the deployed contract
    erc20 = interface.IERC20(luck_token.address)

    # Stake tokens
    stake_amount = Web3.to_wei(1000, 'ether')
    erc20.approve(luck_bank.address, stake_amount, {'from': account})
    luck_bank.stakeTokens(stake_amount, {'from': account})
    
    # Set lottery address
    luck_bank.setLotteryAddress(account.address, {'from': account})

    # Send ETH to the contract
    earnings = Web3.to_wei(10, 'ether')
    account.transfer(luck_bank.address, earnings)

    # Update rewards
    luck_bank.updateStakersRewards(earnings, {'from': account})
    
    staker_share = stake_amount / erc20.balanceOf(luck_bank.address)  # Calculate share
    expected_reward = earnings * staker_share
    assert luck_bank.stakersRewards(account.address) == expected_reward

def test_is_staker():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only running on local blockchain environments")
    
    # Deploy contracts
    luck_token = deploy_luck_token()
    luck_bank = deploy_luck_bank()  # No need to pass luck_token.address here
    account = get_account()
    account_not_staker = get_account(index=1)
    stake_amount = Web3.to_wei(1000, 'ether')  # Converting to the token's decimals
    
    # Use the IERC20 interface to interact with the deployed contract
    erc20 = interface.IERC20(luck_token.address)
    
    # Stake tokens
    erc20.approve(luck_bank.address, stake_amount, {'from': account})
    luck_bank.stakeTokens(stake_amount, {'from': account})
    
    # Check if the account is a staker
    assert luck_bank.isStaker(account.address) == True
    assert luck_bank.isStaker(account_not_staker.address) == False
