from brownie import Lottery
from scripts.helpfull_scripts import get_account

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]

    # Get ticket elements and their names
    elements = lottery.getTicketElements()
    element_names = {
        0: "rock_paper_scissors_game",
        1: "color_game",
        2: "number_game",
        3: "dark_light_game"
    }

    # Prompt user for guesses
    guesses = []
    for i, element in enumerate(elements):
        element_name = element_names[element]
        max_guess = lottery.getElementDifficulty(element)
        
        while True:
            try:
                guess = int(input(f"Enter your guess for Element {i + 1} ({element_name}), between 1 and {max_guess}: "))
                if 1 <= guess <= max_guess:
                    break
                else:
                    print(f"Invalid guess! Please enter a number between 1 and {max_guess}.")
            except ValueError:
                print("Invalid input! Please enter an integer.")
        
        guesses.append((element, guess))

    # Convert list of tuples to a format suitable for the contract
    guess_tuples = [(elem, val) for elem, val in guesses]

    # Call the enter function with the correct format
    tx = lottery.enter(guess_tuples, {"from": account, "value": lottery.getEntranceFee() + 100000000})
    tx.wait(1)

    print(f"(+++) {account.address} entered the lottery with guesses: {guesses}")
    
    # Retrieve and print player guesses
    player_guesses = lottery.getSinglePlayerGuesses(account.address)
    print(f"(+++) playerGuesses: {player_guesses}")

    # Print the event data for the guess submission
    if 'GuessSubmitted' in tx.events:
        for guess_array in tx.events['GuessSubmitted']:
            print(f"(+++) Full lottery guesses event: {guess_array}")
    else:
        print("No GuessSubmitted event found.")

def main():
    enter_lottery()
