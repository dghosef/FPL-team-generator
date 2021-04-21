# coding=UTF-8
from pick_team import pick_team, transfer
from player import Player
if __name__ == "__main__":
    blacklisted = [Player("Antonio", 4, "WHU")]
    mode = 'transfer'
    if mode == 'transfer':
        # Update this to your current team. Don't include backup gk
        # Players are of the form Player(name, position, team)
        # 1 stands for gk, 2 - def, 3 - mid, 4 - fwd. Keys are players, values are prices
        team_prices = {Player("Pope", 1, "BUR"): 5.4,
                       Player("James", 2, "CHE"): 5.0,
                       Player("Cancelo", 2, "MCI"): 5.8,
                       Player("Digne", 2, "EVE"): 6.1,
                       Player("Shaw", 2, "MUN"): 5.2,
                       Player("Dias", 2, "MCI"): 5.9,
                       Player("Saka", 3, "ARS"): 5.1,
                       Player("Lingard", 3, "WHU"): 6.2,
                       Player("Pépé", 3, "ARS"): 7.6,
                       Player("Fernandes", 3, "MUN"): 11.4,
                       Player("Bale", 3, "TOT"): 9.2,
                       Player("Calvert-Lewin", 4, "EVE"): 7.5,
                       Player("Martial", 4, "MUN"): 8.6,
                       Player("Rodrigo", 4, "LEE"): 5.7}
        current_team = list(team_prices.keys())
        prices = list(team_prices.values())
        # Change cur_gw to the gameweek that is about to come.
        # Change transfer_count to the max number of transfers
        # Change itb to the amount of remaining money in the bank
        # If you want to regrab data from the FPL api, set refresh_data to True
        transfer(cur_gw=31, team=current_team, prices=prices, transfer_count=1,
                 itb=1.9, refresh_data=True, blacklisted=blacklisted)
    elif mode == 'pick':
        # See above for parameter explanation. Only difference is budget, which
        # is the amount of money you have for your team. Does not pick a
        # backup gk, so subtract the backup gk cost from your budget
        pick_team(cur_gw=31, budget=105, refresh_data=True, future_gws=1, blacklisted=blacklisted)
    else:
        print("Set mode to either 'transfer' or 'pick'")
