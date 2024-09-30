from brownie import config, network,LuckToken
from scripts.helpfull_scripts import get_account

def deploy_luck_token():
    account = get_account()
    luckToken = LuckToken.deploy({"from": account}, publish_source=config["networks"][network.show_active()].get("verify",False))
    luckToken.tx.wait(1)
    return luckToken

def main():
    deploy_luck_token()