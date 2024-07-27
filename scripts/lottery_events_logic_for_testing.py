import time
from scripts.deploy import deploy_lottery
from scripts.start_lottery import start_lottery
from scripts.enter_lottery import enter_lottery
from scripts.end_lottery import end_lottery_development
from scripts.helpfull_scripts import read_stats

def main():
    deploy_lottery()
    read_stats()
    start_lottery()
    read_stats()
    enter_lottery()
    read_stats()
    enter_lottery()
    read_stats()
    end_lottery_development()
    read_stats()

    time.sleep(5)
    start_lottery()
    read_stats()
    enter_lottery()
    read_stats()