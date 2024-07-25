from brownie import accounts, config,Lottery, network
from scripts.helpfull_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS

latestRequestId = 112380465960345515620071896874860889910842743219185763094417396937748749297414

def request_a_random_number():
    lottery = Lottery[-1]
    account = get_account()  # Ensure you have a valid account for sending the transaction
    
    tx = lottery.requestRandomWords(False, {"from": account})  # Include the 'from' field in transaction parameters
    requestId = tx.events["RequestSent"]["requestId"]  # Extract requestId from the event
    print(f"(+++) A request was made, the requestId is: {requestId}")
    return requestId

def get_status_of_request(requestId):
    lottery = Lottery[-1]
    
    requestStatus = lottery.getRequestStatus(requestId)
    print(f"(+++) the request status of {requestId} is: {requestStatus}")

def main():
    # latestRequestId = request_a_random_number()
    get_status_of_request(latestRequestId)