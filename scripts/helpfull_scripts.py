from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    VRFCoordinatorV2_5Mock,
    MockLinkToken,
    Contract,
    Lottery
)
from web3 import Web3

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
LIVE_ENVIRONMENTS = ["sepolia"]

DECIMALS = 8
INITIAL_VALUE = 200000000000

_BASEFEE=100000000000000000 
_GASPRICELINK=1000000000
_WEIPERUNITLINK=4167665613945909

lottery_state_mapping = {
    "0":"OPEN",
    "1":"CLOSED",
    "2":"WATING_FOR_VRFCOORDINATOR",
    "3":"CALCULATING_WINNER",
}

element_mapping = {
        0: "rock_paper_scissors_game",
        1: "color_game",
        2: "number_game",
        3: "dark_light_game"
    }

def get_account(index = None, id = None):
    if index:
        return accounts[index]
    elif id:
        return accounts.load(id)
    elif (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorV2_5Mock,
    "link_token": MockLinkToken,
}


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, and
    return that mock contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract

def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    print("(+++) Deployed MockV3Aggregator!!!")
    MockLinkToken.deploy({"from": account})
    print("(+++) Deployed link_token!!!")
    VRFCoordinatorV2_5Mock.deploy(_BASEFEE,_GASPRICELINK,_WEIPERUNITLINK, {"from": account})
    print("(+++) Deployed VRFCoordinatorV2_5Mock!!!")


def VRFCoordinatorV2_5Mock_loggic():
    account = get_account()
    lottery = Lottery[-1]

    vrf_Coordinator = get_contract("vrf_coordinator")
    
    transaction_receipt = vrf_Coordinator.createSubscription({"from": account})
    transaction_receipt.wait(1)
    sub_ID = transaction_receipt.events["SubscriptionCreated"]["subId"]
    print(f"(+++) Created subscription!!! subscription state is: {vrf_Coordinator.getSubscription(str(sub_ID))}")

    transaction_receipt = fund_subscription_with_link(sub_ID,1000*10**18,account)
    transaction_receipt.wait(1)
    print(f"(+++) Subscription funded!!! subscription state is: {vrf_Coordinator.getSubscription(str(sub_ID))}")

    transaction_receipt = vrf_Coordinator.addConsumer(sub_ID,Lottery[-1].address,{"from": account})
    transaction_receipt.wait(1)
    print(f"(+++) Consumer added!!! subscription state is: {vrf_Coordinator.getSubscription(str(sub_ID))}")

    lottery.set_subscriptionId(sub_ID,{"from": account})
    print(f"(+++) SubscriptionId had been set!!! its now {lottery.get_subscriptionId()}")

def read_stats():
    lottery = Lottery[-1]
    vrf_Coordinator = get_contract("vrf_coordinator")

    sub_ID = lottery.get_subscriptionId()

    # Print existing stats
    printPurple(f"(+++) SubscriptionId: {lottery.get_subscriptionId()}")
    printPurple(f"(+++) vrf_Coordinator stats: {vrf_Coordinator.getSubscription(sub_ID)}")
    printPurple(f"(+++) The lottery state is: {lottery_state_mapping[str(lottery.lottery_state())]}")
    printPurple(f"(+++) The players in the lottery are: {lottery.get_players()}")
    printPurple(f"(+++) The winning_amount is: {lottery.balance()} wei ({lottery.balance()/(10 ** 18)} ETH)")

    # Get ticket information
    ticket_difficulty = lottery.getTicketDifficulty()
    ticket_elements = lottery.getTicketElements()
    
    printBlue(f"(+++) Ticket Difficulty Level: {ticket_difficulty}")

    # Print ticket elements with difficulty
    printBlue(f"(+++) Ticket Elements: ")
    for i, element in enumerate(ticket_elements):
        element_name = element_mapping[element]
        element_difficulty = lottery.getElementDifficulty(element)  # Assuming you have a function to get the difficulty
        printBlue(f"    Element {i + 1}: {element_name} (difficulty = {element_difficulty})")

    # Print player guesses from Full_Lottery_Guess
    printBlue(f"(+++) Lottery Guesses: ")
    (lottery_guessers,lottery_guesses) = lottery.getPlayersGuesses()

    # Ensure you have the correct mapping and data structure
    for index_of_guesser, guesser in enumerate(lottery_guessers):
        printBlue(f"    Player {guesser}:")
        player_guesses = lottery_guesses[index_of_guesser]
        
        for index_lottery_guess, lottery_guess in enumerate(player_guesses):  # Ensure correct indexing
            printBlue(f"        {guesser} guess number {index_lottery_guess+1}:")
            for guess in lottery_guess:
                element = guess[0]  # Access the element directly
                guess_value = guess[1]  # Access the guess value directly
                
                element_name = element_mapping[element]  # Use the correct element for lookup
                printBlue(f"            {element_name}: {guess_value}")



def fund_subscription_with_link(sub_ID,amount=5*10**18,account=None):
    account = account if account else get_account()
    vrf_Coordinator = get_contract("vrf_coordinator")
    transaction_receipt = vrf_Coordinator.fundSubscription(sub_ID,amount,{"from": account})
    return transaction_receipt

def printBlue(message):
    print(f"\033[96m{message}\033[00m")

def printPurple(message):
    print(f"\033[95m{message}\033[00m")