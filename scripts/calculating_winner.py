from brownie import Lottery, network
from scripts.helpfull_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract

def calculating_winner():
    account = get_account()
    lottery = Lottery[-1]

    winning_amount = lottery.balance()

    tx = lottery.calculate_winners({"from": account})
    tx.wait(1)

    # debbuging_elements_event = tx.events["debbuging_elements"]
    # print(f"(+++) The event debbugingElements is: {debbuging_elements_event}")
    # debbuging_uint_event = tx.events["debbuging_uint"]
    # print(f"(+++) The event debbugingUint is: {debbuging_uint_event}")
    solution_generated_event = tx.events["SolutionGenerated"]
    print(f"(+++) The event SolutionGenerated is: {solution_generated_event}")

    recentTicket = lottery.getRecentTicket()
    (_, _, _, recentWinners) = recentTicket

    if not recentWinners:
        print(f"(+++) There are NO WINNERS ({recentWinners} are the new winners)! The winning amount is {winning_amount} in wei ({winning_amount/(10 ** 18)} in ETH)")
        print(f"(+++) The recent Ticket Was {recentTicket}")
        print(f"(+++) The Ticket History is {lottery.getTicketHistory()}")
    else:
        print(f"(+++) {recentWinners} are the new winners! They won {winning_amount/len(recentWinners)} each in wei ({winning_amount/len(recentWinners)/(10 ** 18)} in ETH)")
        print(f"(+++) The recent Ticket Was {recentTicket}")
        print(f"(+++) The Ticket History is {lottery.getTicketHistory()}")



def main():
    calculating_winner()