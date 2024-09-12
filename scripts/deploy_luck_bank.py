from brownie import LuckBank,LuckToken
from scripts.helpfull_scripts import get_account

def deploy_luck_bank():
    account = get_account()
    luckToken = LuckToken[-1]
    luckBank = LuckBank.deploy(luckToken.address, {"from": account})
    luckBank.tx.wait(1)

def main():
    deploy_luck_bank()

