from brownie import Lottery,accounts,config, network
from web3 import Web3
from scripts.helpfull_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS

def test_get_entrence_fee():
    account = get_account()
    vrf_coordinator = config["networks"][network.show_active()]["COORDINATOR"]
    price_feed_address = config["networks"][network.show_active()]["eth_usd_price_feed"]
    keyHash = config["networks"][network.show_active()]["keyHash"]

    lottery = Lottery.deploy(price_feed_address, vrf_coordinator,keyHash, {"from": account})

    print(f"(+++)price is = {lottery.getPrice()}")
    print(f"(+++)price to enter is = {lottery.getEntranceFee()}")
    print(f"(+++)price to enter is (IN ETH)= {lottery.getEntranceFee()/(10**18)}")

    assert lottery.getEntranceFee() > Web3.to_wei(0.012, "ether")
    assert lottery.getEntranceFee() < Web3.to_wei(0.018, "ether")