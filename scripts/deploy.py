from brownie import config,Lottery, network
from scripts.helpfull_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_contract, VRFCoordinatorV2_5Mock_loggic, read_stats

def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(get_contract("eth_usd_price_feed").address, 
                             get_contract("vrf_coordinator"),
                             config["networks"][network.show_active()]["keyHash"],
                             {"from": account})
    print(f"(+++) the lottery contract was deployed at the {network.show_active()} network!!! with the address {lottery}")
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        VRFCoordinatorV2_5Mock_loggic()
    else:
        lottery.set_subscriptionId(config["networks"][network.show_active()]["s_subscriptionId"],{"from": account})
    return lottery

def main():
    deploy_lottery()
    read_stats()