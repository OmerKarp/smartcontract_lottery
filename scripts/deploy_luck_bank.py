from brownie import LuckBank,LuckToken, config, network
from scripts.helpfull_scripts import get_account

def deploy_luck_bank():
    account = get_account()
    luckToken = LuckToken[-1]
    luckBank = LuckBank.deploy(luckToken.address, {"from": account}, publish_source=config["networks"][network.show_active()].get("verify",False))
    luckBank.tx.wait(1)
    return luckBank

def main():
    deploy_luck_bank()

