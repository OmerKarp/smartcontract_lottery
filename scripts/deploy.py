from brownie import accounts, config,Lottery, network
from scripts.helpfull_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS

def deploy_lottery():
    account = get_account()
    vrf_coordinator = config["networks"][network.show_active()]["COORDINATOR"]
    price_feed_address = config["networks"][network.show_active()]["eth_usd_price_feed"]
    keyHash = config["networks"][network.show_active()]["keyHash"]

    lottery = Lottery.deploy(price_feed_address, vrf_coordinator,keyHash, {"from": account})
    print(f"(+++) the lottery contract was deployed at the {network.show_active()} network!!! with the address {lottery}")

def main():
    deploy_lottery()
