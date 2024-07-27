from brownie import accounts, config,Lottery, network
from scripts.helpfull_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_contract, fund_subscription_with_link, VRFCoordinatorV2_5Mock_loggic, read_stats,printBlue
import time

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

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("(+++) The lottery is started!")

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print(f"(+++) {account.address} entered the lottery!")

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]

    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(180)
    print(f"(+++) {lottery.recentWinner()} is the new winner!")


def main():
    # deploy_lottery()
    # start_lottery()
    # enter_lottery()
    # end_lottery()
    # read_stats()
    printBlue('hi')