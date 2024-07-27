from scripts.helpfull_scripts import (
    get_account,
    fund_subscription_with_link,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
import time
from brownie import network, Lottery
import pytest


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery_contract = Lottery[-1]

    account = get_account()
    lottery_contract.startLottery({"from": account})
    lottery_contract.enter({"from": account, "value": lottery_contract.getEntranceFee()})
    lottery_contract.enter({"from": account, "value": lottery_contract.getEntranceFee()})
    # fund_subscription_with_link(lottery_contract.get_subscriptionId(),5*10**18,account)
    lottery_contract.endLottery({"from": account})
    time.sleep(60)
    print("(+++) its been 1 minute")
    time.sleep(60)
    print("(+++) its been 2 minute")
    time.sleep(60)
    print("(+++) its been 3 minute")
    assert lottery_contract.recentWinner() == account
    assert lottery_contract.balance() == 0