from scripts.helpfull_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_contract
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

def test_setElementDifficulty(): # also tests the getElementDifficulty function
    luck_token, luck_bank, lottery, account = setup_environment()

    # Enum value for rock_paper_scissors_game (0 in the enum)
    element = 0  # rock_paper_scissors_game
    difficulty = 5  # Example difficulty level

    # Set the element difficulty using the lottery contract
    lottery.setElementDifficulty(element, difficulty, {'from': account})

    # Check if the element's difficulty is correctly set
    assert lottery.elements_difficulty_level(element) == difficulty
    assert lottery.getElementDifficulty(element) == difficulty

def test_startLottery(): # also tests the set_games,getTicketDifficulty,getTicketElements functions
    luck_token, luck_bank, lottery, account = setup_environment()

    # Ensure the lottery is in the OPEN state
    lottery.startLottery({'from': account})
    assert lottery.lottery_state() == 0  # LOTTERY_STATE.OPEN

    ticket_wanted_difficulty_level = lottery.wanted_difficulty_level()
    ticket_difficulty_level = lottery.getTicketDifficulty()

    assert ticket_difficulty_level >= ticket_wanted_difficulty_level
    assert ticket_difficulty_level < ticket_wanted_difficulty_level * 100 # the difficulty level didnt explode for some reason

    ticket_elements = lottery.getTicketElements()

    assert len(ticket_elements) > 1

def test_enter_lottery():
    luck_token, luck_bank, lottery, account = setup_environment()
    account2 = get_account(index=1)

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.startLottery({'from': account2})

    # Ensure the lottery is in the OPEN state
    lottery.startLottery({'from': account})

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
    tx = lottery.enter(guess_tuples, {"from": account, "value": entrance_fee + 100000000})
    tx.wait(1)

    # Check if the player was added to the players array
    assert lottery.players(0) == account

    assert Web3.eth.get_balance(lottery.address) == (entrance_fee + 100000000)
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

def test_set_subscriptionId():
    luck_token, luck_bank, lottery, account = setup_environment()
    account2 = get_account(index=1)

    fake_s_subscriptionId = 123
    lottery.set_subscriptionId(fake_s_subscriptionId,{"from": account})

    assert lottery.s_subscriptionId() == fake_s_subscriptionId

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.set_subscriptionId(fake_s_subscriptionId,{"from": account2})

def test_get_random_3_digits():
    luck_token, luck_bank, lottery, account = setup_environment()

    random_big_number = 22457654523000873890618985732870744312626094790626683287552762375778023379207
    random_3_digits_namber = lottery.get_random_3_digits(random_big_number,0)

    assert random_3_digits_namber == 207 # last 3 digit of the number

    random_3_digits_namber = lottery.get_random_3_digits(random_big_number,1)
    assert random_3_digits_namber == 920 # last 4 digit of the number without the last one

def test_generateGuesses():
    luck_token, luck_bank, lottery, account = setup_environment()

    lottery.startLottery({'from': account})

    random_big_number = 22457654523000873890618985732870744312626094790626683287552762375778023379207
    random_guesses = lottery.generateGuesses(random_big_number)

    print(random_guesses)
    assert len(random_guesses) != 0
    assert len(random_guesses) == len(lottery.getTicketElements())

def test_endLottery_no_players(): # also tests the resetTicket, getRecentTicket, getTicket, getTicketHistory functions
    luck_token, luck_bank, lottery, account = setup_environment()
    account2 = get_account(index=1)

    lottery.startLottery({'from': account})

    ticket = [lottery.getTicketDifficulty(),lottery.getTicketElements(),[],[]]

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.endLottery({'from': account2})

    lottery.endLottery({'from': account})

    assert lottery.lottery_state() == 1  # LOTTERY_STATE.CLOSED

    ticket_difficulty_level = lottery.getTicketDifficulty()
    ticket_elements = lottery.getTicketElements()

    assert ticket_difficulty_level == 1
    assert ticket_elements == []

    ticket_in_history = lottery.getRecentTicket()

    assert ticket_in_history == ticket 

    nth_ticket = lottery.getTicket(0)

    assert nth_ticket == ticket

    # test with 2 tickets

    lottery.startLottery({'from': account})

    new_ticket = [lottery.getTicketDifficulty(),lottery.getTicketElements(),[],[]]

    lottery.endLottery({'from': account})
    
    second_ticket_in_history = lottery.getRecentTicket()

    assert second_ticket_in_history == new_ticket 

    nth_ticket_again = lottery.getTicket(1)

    assert nth_ticket_again == new_ticket

    # test the getTicketHistory

    ticket_history = lottery.getTicketHistory()

    assert ticket_history == [nth_ticket,nth_ticket_again]
 
def test_endLottery_with_players(): # also tests the get_players,requestRandomWords ,getRequestStatus function
    luck_token, luck_bank, lottery, account = setup_environment()

    lottery.startLottery({'from': account})

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
    tx = lottery.enter(guess_tuples, {"from": account, "value": entrance_fee + 100000000})
    tx.wait(1)

    tx = lottery.endLottery({'from': account})

    assert lottery.lottery_state() == 2  # LOTTERY_STATE.WATING_FOR_VRFCOORDINATOR

    requestId = tx.events['RequestSent']['requestId']
    numWords = tx.events['RequestSent']['numWords']

    assert numWords == lottery.numWords()
    assert requestId != 0

    requestStatus = lottery.getRequestStatus(requestId)

    assert requestStatus == [False, []] # (request.fulfilled, request.randomWords)

def test_fulfillRandomWords(): # also tests the getRequestStatus function
    luck_token, luck_bank, lottery, account = setup_environment()

    lottery.startLottery({'from': account})

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
    tx = lottery.enter(guess_tuples, {"from": account, "value": entrance_fee + 100000000})
    tx.wait(1)

    ending_transaction = lottery.endLottery({'from': account})

    request_id = ending_transaction.events["RequestSent"]["requestId"]
    STATIC_RNG = [22457654523000873890618985732870744312626094790626683287552762375778023379207]

    assert request_id != 0
    
    tx = get_contract("vrf_coordinator").fulfillRandomWordsWithOverride(
        request_id, lottery.address, STATIC_RNG, {"from": account}
        )
    tx.wait(1)

    request_fulfilled_event = tx.events["RequestFulfilled"]

    assert request_fulfilled_event == [request_id, STATIC_RNG]

    assert lottery.lottery_state() == 3  # LOTTERY_STATE.CALCULATING_WINNER

    requestId = ending_transaction.events['RequestSent']['requestId']
    requestStatus = lottery.getRequestStatus(requestId)

    assert requestStatus == [True, [22457654523000873890618985732870744312626094790626683287552762375778023379207]] # (request.fulfilled, request.randomWords)


def test_calculate_winners(): # also tests the payLuckBankEarnings, resetTicket, playersGuesses, checkGuesses functions
    luck_token, luck_bank, lottery, account = setup_environment()
    account2 = get_account(index=1)

    lottery.startLottery({'from': account})

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
    tx = lottery.enter(guess_tuples, {"from": account, "value": entrance_fee + 100000000})
    tx.wait(1)

    ending_transaction = lottery.endLottery({'from': account})

    request_id = ending_transaction.events["RequestSent"]["requestId"]
    STATIC_RNG = [22457654523000873890618985732870744312626094790626683287552762375778023379207]
    
    tx = get_contract("vrf_coordinator").fulfillRandomWordsWithOverride(
        request_id, lottery.address, STATIC_RNG, {"from": account}
        )
    tx.wait(1)

    (playerAddresses,_) = lottery.getPlayersGuesses()
    winningGuesses = lottery.generateGuesses(STATIC_RNG[0])
    tempWinners = []
    winnersCount = 0
    for playerAddress in playerAddresses:
        playerGuesses = lottery.getSinglePlayerGuesses(playerAddress)
        for guesses in playerGuesses:
            if lottery.checkGuesses(guesses, winningGuesses):
                    tempWinners.append(playerAddress)
                    winnersCount += 1
                    break 
            
    initial_winners_balances = [Web3.eth.get_balance(winner) for winner in tempWinners]

    initial_lottery_balance = Web3.eth.get_balance(lottery.address)
    initial_luck_bank_balance = Web3.eth.get_balance(luck_bank.address)

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.calculate_winners({'from': account2})
    
    lottery.calculate_winners({'from': account})

    final_balance = Web3.eth.get_balance(lottery.address)
    final_luck_bank_balance = Web3.eth.get_balance(luck_bank.address)

    assert final_balance == initial_lottery_balance * 0.9
    assert final_luck_bank_balance == initial_luck_bank_balance + initial_lottery_balance * 0.1

    for i in range(len(tempWinners)):
        assert initial_winners_balances[i] == initial_winners_balances[i] + (initial_lottery_balance * 0.9) / len(tempWinners)

    ticket_in_history = lottery.getRecentTicket()

    assert ticket_in_history[2] == winningGuesses
    assert ticket_in_history[3] == tempWinners

    assert lottery.lottery_state() == 1  # LOTTERY_STATE.CLOSE
