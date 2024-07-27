from brownie import Lottery,network
from scripts.helpfull_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract
import time

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]

    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(180)
    print(f"(+++) {lottery.recentWinner()} is the new winner!")

def end_lottery_development():
    account = get_account()
    lottery = Lottery[-1]

    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)

    request_id = ending_transaction.events["RequestSent"]["requestId"]
    STATIC_RNG = [775]

    get_contract("vrf_coordinator").fulfillRandomWordsWithOverride(
        request_id,lottery.address,STATIC_RNG, {"from": account}
    )

    time.sleep(3)
    print(f"(+++) {lottery.recentWinner()} is the new winner!")

def main():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        end_lottery()
    else:
        end_lottery_development()