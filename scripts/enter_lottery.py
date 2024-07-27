from brownie import Lottery
from scripts.helpfull_scripts import get_account

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print(f"(+++) {account.address} entered the lottery!")

def main():
    enter_lottery()