from brownie import Lottery
from scripts.helpfull_scripts import get_account

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    
    ticket_difficulty = lottery.getTicketDifficulty()
    elements = lottery.getTicketElements()

    print(f"(+++) The lottery is started with ticket difficulty: {ticket_difficulty}")
    print(f"(+++) Elements in the lottery ticket:")

    element_names = ["rock_paper_scissors_game", "color_game", "number_game", "dark_light_game"]
    for i, element in enumerate(elements):
        element_name = element_names[element]
        element_difficulty = lottery.getElementDifficulty(element)
        print(f"    Element {i + 1}: {element_name}, Difficulty: {element_difficulty}")

def main():
    start_lottery()