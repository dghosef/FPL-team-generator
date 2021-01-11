# coding=UTF-8
from pick_team import pick_team, transfer
from player import Player
if __name__ == "__main__":
    mode = 'pick'
    if mode == 'transfer':
        # Update this to your current team. Don't include backup gk
        # Players are of the form Player(name, position, team)
        # 1 stands for gk, 2 - def, 3 - mid, 4 - fwd
        current_team = [Player("Martínez", 1, "AVL"),
                        Player("Taylor", 2, "BUR"),
                        Player("Chilwell", 2, "CHE"),
                        Player("Cancelo", 2, "MCI"),
                        Player("Walker-Peters", 2, "SOU"),
                        Player("Kilman", 2, "WOL"),
                        Player("Grealish", 3, "AVL"),
                        Player("Salah", 3, "LIV"),
                        Player("Fernandes", 3, "MUN"),
                        Player("Reed", 3, "FUL"),
                        Player("Son", 3, "TOT"),
                        Player("Bamford", 4, "LEE"),
                        Player("Adams", 4, "SOU"),
                        Player("Kane", 4, "TOT")]
        # Update this to be the prices of the players in current_team. Prices
        # should be in the same order as the players in current_team
        prices = [4.9, 4.5, 5.8, 5.5, 4.7, 4.1, 7.6, 12.4, 11.0, 4.4, 9.3,
                6.3, 6.0, 10.7]
        # Change cur_gw to the gameweek that is about to come.
        # Change transfer_count to the max number of transfers
        # Change itb to the amount of remaining money in the bank
        # If you want to regrab data from the FPL api, set refresh_data to True
        transfer(cur_gw=17, team=current_team, prices=prices, transfer_count=1,
                 itb=0.0, refresh_data=False)
    elif mode == 'pick':
        # See above for parameter explanation. Only difference is budget, which
        # is the amount of money you have for your team. Does not pick a
        # backup gk, so subtract the backup gk cost from your budget
        pick_team(cur_gw=18, budget=96, refresh_data=False)
    else:
        print("Set mode to either 'transfer' or 'pick'")
