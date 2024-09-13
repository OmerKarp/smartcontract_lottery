from scripts.helpfull_scripts import (
    get_account,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    VRFCoordinatorV2_5Mock_loggic
)
from brownie import exceptions, network, interface
from scripts.deploy_luck_token import deploy_luck_token
from web3 import Web3
import pytest

def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only running on local blockchain environments")

    # Deploy the contract
    luck_token = deploy_luck_token()

    # Use the IERC20 interface to interact with the deployed contract
    erc20 = interface.IERC20(luck_token.address)

    # Expected token count (in wei)
    expected_token_count = Web3.to_wei(1000000, 'ether')  # 1,000,000 tokens with 18 decimals

    # Get the actual token count for the account that deployed the contract
    actual_token_count = erc20.balanceOf(get_account())

    # Assert that the actual token count matches the expected token count
    assert expected_token_count == actual_token_count, f"Expected {expected_token_count}, but got {actual_token_count}"
