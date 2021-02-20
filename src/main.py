# coding=UTF-8
from pick_team import pick_team, transfer
from player import Player
if __name__ == "__main__":
    mode = 'transfer'
    if mode == 'transfer':
        # Update this to your current team. Don't include backup gk
        # Players are of the form Player(name, position, team)
        # 1 stands for gk, 2 - def, 3 - mid, 4 - fwd. Keys are players, values are prices
        team_prices = {Player("Pope", 1, "BUR"): 5.5,
                       Player("Mina", 2, "EVE"): 5.5,
                       Player("Cancelo", 2, "MCI"): 5.9,
                       Player("Digne", 2, "EVE"): 6.1,
                       Player("Bednarek", 2, "SOU"): 4.9,
                       Player("Dias", 2, "MCI"): 5.9,
                       Player("Saka", 3, "ARS"): 5.3,
                       Player("Grealish", 3, "AVL"): 7.7,
                       Player("Foden", 3, "MCI"): 6.1,
                       Player("Fernandes", 3, "MUN"): 11.3,
                       Player("Rashford", 3, "MUN"): 9.5,
                       Player("Calvert-Lewin", 4, "EVE"): 7.7,
                       Player("Martial", 4, "MUN"): 8.7,
                       Player("Rodrigo", 4, "LEE"): 5.7}
        current_team = list(team_prices.keys())
        prices = list(team_prices.values())
        # Change cur_gw to the gameweek that is about to come.
        # Change transfer_count to the max number of transfers
        # Change itb to the amount of remaining money in the bank
        # If you want to regrab data from the FPL api, set refresh_data to True
        transfer(cur_gw=24, team=current_team, prices=prices, transfer_count=1,
                 itb=4.8, refresh_data=True)
    elif mode == 'pick':
        # See above for parameter explanation. Only difference is budget, which
        # is the amount of money you have for your team. Does not pick a
        # backup gk, so subtract the backup gk cost from your budget
        pick_team(cur_gw=19, budget=96, refresh_data=False)
    else:
        print("Set mode to either 'transfer' or 'pick'")
