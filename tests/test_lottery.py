from scripts.helpfull_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.deploy_luck_token import deploy_luck_token
from scripts.deploy_luck_bank import deploy_luck_bank
from scripts.deploy import deploy_lottery
from brownie import exceptions, network, interface,reverts, web3 as Web3 
import random
import pytest

def setup_environment():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only running on local blockchain environments")

    # Deploy contracts
    luck_token = deploy_luck_token()
    luck_bank = deploy_luck_bank()
    lottery = deploy_lottery()
    account = get_account()

    return luck_token, luck_bank, lottery, account


def test_setLuckBank():
    luck_token, luck_bank, lottery, account = setup_environment()
    
    # Use the actual deployed luck_bank's address instead of a fake one
    luck_bank_address = luck_bank.address

    # Set the LuckBank address
    lottery.setLuckBank(luck_bank_address, {'from': account})

    # Check if LuckBankAddress was correctly updated
    assert lottery.LuckBankAddress() == luck_bank_address

    # Check if the luckBank contract instance is correctly set by comparing addresses
    assert lottery.luckBank() == luck_bank_address

def test_setElementDifficulty():
    luck_token, luck_bank, lottery, account = setup_environment()

    # Enum value for rock_paper_scissors_game (0 in the enum)
    element = 0  # rock_paper_scissors_game
    difficulty = 5  # Example difficulty level

    # Set the element difficulty using the lottery contract
    lottery.setElementDifficulty(element, difficulty, {'from': account})

    # Check if the element's difficulty is correctly set
    assert lottery.elements_difficulty_level(element) == difficulty

def test_enter_lottery():
    luck_token, luck_bank, lottery, account = setup_environment()

    # Ensure the lottery is in the OPEN state
    lottery.startLottery({'from': account})
    assert lottery.lottery_state() == 0  # LOTTERY_STATE.OPEN

    guesses = []
    elements = lottery.getTicketElements()
    
    for i, element in enumerate(elements):
        max_guess = lottery.getElementDifficulty(element)
        guess = random.randint(1, max_guess)
        guesses.append((element, guess))

    # Calculate entrance fee
    entrance_fee = lottery.getEntranceFee()

    # Ensure the player sends enough ETH (matching entrance fee)
    guess_tuples = [(elem, val) for elem, val in guesses]

    # Call the enter function with the correct format
    tx = lottery.enter(guess_tuples, {"from": account, "value": lottery.getEntranceFee() + 100000000})
    tx.wait(1)

    # Check if the player was added to the players array
    assert lottery.players(0) == account

    # Check if the player's guesses were stored correctly
    # also tests the getPlayersGuesses function
    player_guesses = lottery.getPlayersGuesses()[1]
    assert len(player_guesses) == 1  # Ensure one set of guesses was added
    assert player_guesses[0][0][0] == guess_tuples[0]  # First guess of the first elements of the first address
    assert player_guesses[0][0][1] == guess_tuples[1]  # Second guess of the first elements of the first address

    # Check that the event was emitted
    assert len(tx.events) > 0
    assert 'GuessSubmitted' in tx.events
    assert tx.events['GuessSubmitted']['guesser'] == account
    assert tx.events['GuessSubmitted']['guesses'] == guesses

    # test the getSinglePlayerGuesses function aswell
    player_guesses = lottery.getSinglePlayerGuesses(account.address)
    assert len(player_guesses) == 1  # Ensure one set of guesses was added
    assert player_guesses[0][0] == guess_tuples[0]  # First guess of the first elements 
    assert player_guesses[0][1] == guess_tuples[1]  # Second guess of the first elements

def test_getEntranceFee():
    luck_token, luck_bank, lottery, account = setup_environment()

    entranceFee_in_usd = 50
    hard_coded_eth_usd_price = 2000
    entranceFee_in_eth = entranceFee_in_usd / hard_coded_eth_usd_price 
    entranceFee_in_wei = entranceFee_in_eth * (10**18)

    assert lottery.getEntranceFee() == entranceFee_in_wei