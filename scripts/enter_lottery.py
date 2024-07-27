from brownie import accounts, config,Lottery, network
from scripts.helpfull_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_contract, fund_subscription_with_link, VRFCoordinatorV2_5Mock_loggic, read_stats,printBlue
import time

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print(f"(+++) {account.address} entered the lottery!")

def main():
    enter_lottery()
    read_stats()