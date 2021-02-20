# Fantasy premier league team generation

### About
Generates a Fantasy Premier League team with linear programming and a points prediction algorithm based on player statistics from the FPL API. See [dghosef.me/fpl-writeup](dghosef.me/fpl-writeup) for more details and a full writeup. 

### Requirements
Python >= 3.6 \
PuLP \
requests \
Pandas
### Usage
Edit the src/main.py file to your liking(basic instructions in the file). Then run `python src/main.py` a team should be outputted. If you don't alter src/main.py, by default the picked team for the period gw18-28 will be outputted

### Changes
#### Urgent
Don't transfer in yellow-marked players