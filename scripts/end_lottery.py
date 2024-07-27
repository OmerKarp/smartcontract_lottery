from brownie import Lottery
from scripts.helpfull_scripts import get_account
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