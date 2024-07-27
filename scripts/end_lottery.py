from brownie import accounts, config,Lottery, network
from scripts.helpfull_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_contract, fund_subscription_with_link, VRFCoordinatorV2_5Mock_loggic, read_stats,printBlue
import time

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]

    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(180)
    print(f"(+++) {lottery.recentWinner()} is the new winner!")

def main():
    end_lottery()
    read_stats()
