from brownie import LuckToken
from scripts.helpfull_scripts import get_account

def deploy_luck_token():
    account = get_account()
    luckToken = LuckToken.deploy({"from": account})
    luckToken.tx.wait(1)

def main():
    deploy_luck_token()