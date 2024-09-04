from brownie import Lottery,network
from scripts.helpfull_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract
import time

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]

    winning_amount = lottery.balance()

    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    if len(lottery.get_players()) == 0:
        print(f"(+++) There are 0 players in the lottery.")
    else:
        time.sleep(180)
        print(f"(+++) {lottery.recentWinner()} is the new winner! he won {winning_amount} wei ({winning_amount/(10 ** 18)} ETH)")

def end_lottery_development():
    account = get_account()
    lottery = Lottery[-1]

    winning_amount = lottery.balance()

    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)

    if len(lottery.get_players()) > 0:
        request_id = ending_transaction.events["RequestSent"]["requestId"]
        STATIC_RNG = [775]

        get_contract("vrf_coordinator").fulfillRandomWordsWithOverride(
            request_id,lottery.address,STATIC_RNG, {"from": account}
        )

        time.sleep(10)
        print(f"(+++) {lottery.recentWinner()} is the new winner! he won {winning_amount} wei ({winning_amount/(10 ** 18)} ETH)")
    else:
        print(f"(+++) There are 0 players in the lottery.")

def main():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        end_lottery()
    else:
        end_lottery_development()