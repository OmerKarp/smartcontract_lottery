import time
from scripts.deploy import deploy_lottery
from scripts.start_lottery import start_lottery
from scripts.enter_lottery import enter_lottery
from scripts.end_lottery import end_lottery_development
from scripts.calculating_winner import calculating_winner
from scripts.deploy_luck_token import deploy_luck_token
from scripts.deploy_luck_bank import deploy_luck_bank
from scripts.helpfull_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract, read_stats
from brownie import Lottery,network, LuckToken, LuckBank


def main():
    account = get_account()
    account2 = get_account(index = 1)
    deploy_luck_token()
    deploy_luck_bank()
    deploy_lottery()
    
    start_lottery()
    enter_lottery([(3, 2), (3, 1), (0, 3), (2, 10)])
    enter_lottery([(3, 2), (3, 1), (0, 3), (2, 10)])
    enter_lottery([(3, 2), (3, 1), (0, 3), (2, 1)])
    end_lottery_development()
    read_stats()
    calculating_winner()
    read_stats()

    start_lottery()
    enter_lottery([(3, 2), (3, 1), (0, 3), (2, 10)])
    read_stats()
