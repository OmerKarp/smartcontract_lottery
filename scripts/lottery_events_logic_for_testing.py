import time
from scripts.deploy import deploy_lottery
from scripts.start_lottery import start_lottery
from scripts.enter_lottery import enter_lottery
from scripts.end_lottery import end_lottery_development
from scripts.calculating_winner import calculating_winner
from scripts.helpfull_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract, read_stats
from brownie import Lottery,network, LuckToken, LuckBank


def main():
    account = get_account()
    account2 = get_account(index = 1)
    luckToken = LuckToken.deploy({"from": account})
    luckToken.tx.wait(1)

    luckBank = LuckBank.deploy(luckToken.address, {"from": account})
    luckBank.tx.wait(1)

    deploy_lottery()
    start_lottery()
    enter_lottery([(3, 2), (3, 1), (0, 3), (2, 10)])
    end_lottery_development()
    read_stats()
    calculating_winner()
    read_stats()

    start_lottery()
    enter_lottery([(3, 2), (3, 1), (0, 3), (2, 10)])
    read_stats()
