# coding=UTF-8
from pick_team import pick_team, transfer
from player import Player
if __name__ == "__main__":
    mode = 'transfer'
    if mode == 'transfer':
        # Update this to your current team. Don't include backup gk
        # Players are of the form Player(name, position, team)
        # 1 stands for gk, 2 - def, 3 - mid, 4 - fwd
        current_team = [Player("Pope", 1, "BUR"),
                        Player("Targett", 2, "AVl"),
                        Player("Cancelo", 2, "MCI"),
                        Player("Walker-Peters", 2, "SOU"),
                        Player("Bednarek", 2, "SOU"),
                        Player("Dias", 2, "MCI"),
                        Player("Grealish", 3, "AVL"),
                        Player("El Ghazi", 3, "AVL"),
                        Player("De Bruyne", 3, "MCI"),
                        Player("Fernandes", 3, "MUN"),
                        Player("Rashford", 3, "MUN"),
                        Player("Brewster", 4, "SHU"),
                        Player("Martial", 4, "MUN"),
                        Player("Rodrigo", 4, "LEE")]
        # Update this to be the prices of the players in current_team. Prices
        # should be in the same order as the players in current_team
        prices = [5.4, 4.6, 5.7, 4.8, 4.9, 5.8, 7.7, 5.7, 11.7, 11.2, 9.5, 4.5,
                  8.7, 5.7]
        # Change cur_gw to the gameweek that is about to come.
        # Change transfer_count to the max number of transfers
        # Change itb to the amount of remaining money in the bank
        # If you want to regrab data from the FPL api, set refresh_data to True
        transfer(cur_gw=20, team=current_team, prices=prices, transfer_count=1,
                 itb=0.2, refresh_data=False)
    elif mode == 'pick':
        # See above for parameter explanation. Only difference is budget, which
        # is the amount of money you have for your team. Does not pick a
        # backup gk, so subtract the backup gk cost from your budget
        pick_team(cur_gw=19, budget=96, refresh_data=False)
    else:
        print("Set mode to either 'transfer' or 'pick'")
