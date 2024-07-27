from brownie import accounts, config,Lottery, network
from scripts.helpfull_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_contract, fund_subscription_with_link, VRFCoordinatorV2_5Mock_loggic, read_stats,printBlue
import time

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("(+++) The lottery is started!")

def main():
    start_lottery()
    read_stats()