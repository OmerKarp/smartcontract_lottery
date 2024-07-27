from brownie import Lottery
from scripts.helpfull_scripts import get_account

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("(+++) The lottery is started!")

def main():
    start_lottery()