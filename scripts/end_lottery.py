from brownie import Lottery, network
from scripts.helpfull_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]

    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    if len(lottery.get_players()) == 0:
        print(f"(+++) There are 0 players in the lottery.")


def end_lottery_development():
    account = get_account()
    lottery = Lottery[-1]

    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)

    if len(lottery.get_players()) > 0:
        request_id = ending_transaction.events["RequestSent"]["requestId"]
        STATIC_RNG = [22457654523000873890618985732870744312626094790626683287552762375778023379207]

        # Print the request_id and STATIC_RNG for debugging
        print(f"(+++) Request ID: {request_id}")
        print(f"(+++) STATIC_RNG: {STATIC_RNG}")

        tx = get_contract("vrf_coordinator").fulfillRandomWordsWithOverride(
            request_id, lottery.address, STATIC_RNG, {"from": account}
            )
        tx.wait(1)

        request_fulfilled_event = tx.events["RequestFulfilled"]
        print(f"(+++) The event RequestFulfilled is: {request_fulfilled_event}")
    else:
        print(f"(+++) There are 0 players in the lottery.")

def main():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        end_lottery()
    else:
        end_lottery_development()
