# from scripts.helpfull_scripts import (
#     get_account,
#     get_contract,
#     LOCAL_BLOCKCHAIN_ENVIRONMENTS,
#     VRFCoordinatorV2_5Mock_loggic
# )
# from brownie import exceptions, network
# from scripts.deploy import deploy_lottery
# from web3 import Web3
# import pytest


# def test_get_entrance_fee():
#     if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
#         pytest.skip()
#     lottery_contract = deploy_lottery()

#     expected_entrance_fee = Web3.to_wei(0.025, "ether") # 2000/1 == 50/x ==> x = 0.025
#     entrance_fee = lottery_contract.getEntranceFee()

#     print(entrance_fee)
#     assert expected_entrance_fee == entrance_fee


# def test_cant_enter_unless_started():
#     if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
#         pytest.skip()
#     lottery_contract = deploy_lottery()

#     with pytest.raises(exceptions.VirtualMachineError):
#         lottery_contract.enter(
#             {"from": get_account(), "value": lottery_contract.getEntranceFee()}
#         )


# def test_can_start_and_enter_lottery():
#     if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
#         pytest.skip()
#     lottery_contract = deploy_lottery()

#     account = get_account()
#     lottery_contract.startLottery({"from": account})
#     lottery_contract.enter(
#         {"from": account, "value": lottery_contract.getEntranceFee()}
#     )
#     assert lottery_contract.players(0) == account


# def test_can_end_lottery():
#     if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
#         pytest.skip()
#     lottery_contract = deploy_lottery()

#     account = get_account()
#     lottery_contract.startLottery({"from": account})
#     lottery_contract.enter(
#         {"from": account, "value": lottery_contract.getEntranceFee()}
#     )
#     VRFCoordinatorV2_5Mock_loggic()
#     lottery_contract.endLottery({"from": account})
#     assert lottery_contract.lottery_state() == 2


# def test_can_pick_winner_correctly():
#     if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
#         pytest.skip()
#     lottery_contract = deploy_lottery()

#     account = get_account()

#     lottery_contract.startLottery({"from": account})

#     lottery_contract.enter({"from": account, "value": lottery_contract.getEntranceFee()})
#     print(f"(+++) {account.address} entered the lottery!")
#     lottery_contract.enter({"from": get_account(index=1), "value": lottery_contract.getEntranceFee()})
#     print(f"(+++) {get_account(index=1).address} entered the lottery!")
#     lottery_contract.enter({"from": get_account(index=2), "value": lottery_contract.getEntranceFee()})
#     print(f"(+++) {get_account(index=2).address} entered the lottery!")

#     print(lottery_contract.balance())
    
#     starting_balance_of_account = get_account(index=1).balance()
#     balance_of_lottery = lottery_contract.balance()
#     subscription_balance = get_contract("vrf_coordinator").getSubscriptionBalance(lottery_contract.get_subscriptionId())
#     print(f"(+++) starting_balance_of_account: {starting_balance_of_account},balance_of_lottery: {balance_of_lottery},balance_of_sub: {subscription_balance}")
#     transaction = lottery_contract.endLottery({"from": account})
#     print("(+++) The lottery is ENDED!")
#     request_id = transaction.events["RequestSent"]["requestId"]
#     STATIC_RNG = [775]


#     print(f"(+++) starting_balance_of_account: {starting_balance_of_account},balance_of_lottery: {balance_of_lottery},balance_of_sub: {subscription_balance}")
#     get_contract("vrf_coordinator").fulfillRandomWordsWithOverride(
#         request_id,lottery_contract.address,STATIC_RNG, {"from": account}
#     )
#     print(f"(+++) starting_balance_of_account: {starting_balance_of_account},balance_of_lottery: {balance_of_lottery},balance_of_sub: {subscription_balance}")
#     # 777 % 3 = 0
#     print(lottery_contract.recentWinner())
#     print(lottery_contract.balance())
#     assert lottery_contract.recentWinner() == get_account(index=1)
#     assert lottery_contract.balance() == 0
#     assert get_account(index = 1).balance() == starting_balance_of_account + balance_of_lottery