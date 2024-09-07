from brownie import config,Lottery, network,LuckBank
from scripts.helpfull_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_contract, VRFCoordinatorV2_5Mock_loggic

def deploy_lottery():
    account = get_account()
    luckBank = LuckBank[-1]
    vrf_coordinator = get_contract("vrf_coordinator")
    lottery = Lottery.deploy(get_contract("eth_usd_price_feed").address, 
                             get_contract("vrf_coordinator"),
                             config["networks"][network.show_active()]["keyHash"],
                             luckBank.address,
                             {"from": account},
                             publish_source=config["networks"][network.show_active()].get("verify",False)
                            )
    print(f"(+++) The lottery contract was deployed at the {network.show_active()} network!!! with the address {lottery}")
    luckBank.setLotteryAddress(lottery.address)
    print(f"(+++) Set the lottery address in the Luck Bank.")
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        VRFCoordinatorV2_5Mock_loggic()
    else:
        tx = lottery.set_subscriptionId(config["networks"][network.show_active()]["s_subscriptionId"],{"from": account})
        tx.wait(1)
        tx = vrf_coordinator.addConsumer(config["networks"][network.show_active()]["s_subscriptionId"], lottery.address, {"from": account})
        tx.wait(1)
        print(f"(+++) Consumer added!!! Subscription state is: {vrf_coordinator.getSubscription(str(config['networks'][network.show_active()]['s_subscriptionId']))}")
    return lottery

def main():
    deploy_lottery()