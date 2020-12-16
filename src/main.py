from pick_team import pick_team
from player import Player
if __name__ == "__main__":
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
    prices = [4.9, 4.5, 5.8, 5.5, 4.7, 4.1, 7.6, 12.4, 11.0, 4.4, 9.3,
              6.3, 6.0, 10.7]
    # transfer(17, current_team, prices, 1, hivemind=True)
    pick_team(18, past_gws=10, hivemind=False, refresh_data=False)
    pick_team(18, past_gws=10, hivemind=False, refresh_data=False, sub_factors=[0,0,0])
