from scripts.helpfull_scripts import read_stats

def main():
    try:
        read_stats()
    except IndexError:
        print("(+++) Lottery hasnt been deployed yet!!!")