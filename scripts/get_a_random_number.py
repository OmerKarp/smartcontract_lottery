#used for testing back in the day

# from brownie import Lottery 
# from scripts.helpfull_scripts import get_account

# def request_a_random_number():
#     lottery = Lottery[-1]
#     account = get_account()
    
#     tx = lottery.requestRandomWords(False, {"from": account}) 
#     requestId = tx.events["RequestSent"]["requestId"]  
#     print(f"(+++) A request was made, the requestId is: {requestId}")
#     return requestId

# def get_status_of_request(requestId):
#     lottery = Lottery[-1]
    
#     requestStatus = lottery.getRequestStatus(requestId)
#     print(f"(+++) the request status of {requestId} is: {requestStatus}")
#     print(f"(+++) the type is {type(requestStatus[1][0])}")
#     print(f"(+++) the number is {int(requestStatus[1][0])}")


# def main():
#     latestRequestId = request_a_random_number()
#     get_status_of_request(latestRequestId)