# Fantacalcio App

The idea behind this project is to scrape data from [Fantacalcio Official Website](https://www.fantacalcio.it/voti-fantacalcio-serie-a) and use it to implement a python software able to 
simulate a Fantacalcio season. The app takes as input a given number of teams (usually a multiply of 2 in a range between 8 and 12) with 25 players (3 goalkeepers, 8 defenders, 8 midfielders and 6 forwards), which is the most common format 
used in the game (anyway it could be changed as you prefer). 

## Game Rules

### Match Calculus Rules
To simplify the implementation, the following rules have been applied to fantasy football by default:
  - The only allowed formation is 4-3-3, which means 1 goalkeeper, 4 defenders, 3 midfielders and 3 forwards. If there are not enough players in a role with a valid vote, a player with a null vote will be fielded anyway.
  
  - The user doesn't field players; instead, they are automatically selected based on the highest "fantavoto", while respecting positional requirements.
  
  - The following bonus and malus are applied to a player's vote in order to calculate his "fantavoto":
     - +3 for each goal or penalty scored;
     - +1 for each assist;
     - -1 for each goal taken (applied only to goalkeepers);
     - -3 for each missed penalty;
     - +3 for each saved penalty (applied only to goalkeepers);
     - -0,5 if he gets a yellow card;
     - -1 if he gets a red card;
     - -2 for each autogoal;
     - +1 if he keeps a clean sheet (applied only to goalkeepers).
       
  - The defense modifier is used, which awards bonus points to the team based on the average rating of the 4 defenders:
     - If the average rating is < 6, bonus +1
     - If the average rating is ≥ 6 and < 6.25, bonus +2
     - If the average rating is ≥ 6.25 and < 6.5, bonus +3
     - If the average rating is ≥ 6.5 and < 6.75, bonus +4
     - If the average rating is ≥ 6.75 and < 7, bonus +5
     - If the average rating is ≥ 7 and < 7.25, bonus +6
     - If the average rating is ≥ 7.25, bonus +7
    The modified is only applied only if 4 defenders are fielded.

  - The goal thresholds are as follows:
     - 1st goal – 66 points
     - 2nd goal – 72 points
     - 3rd goal – 78 points
     - 4th goal – 84 points
     - 5th goal – 90 points
     - 6th goal – 96 points
     - And so on...

### Leaderboard Rules
Winning a match awards 3 points in the leaderboard, a draw gives 1 point, and a loss gives 0 points.
The final leaderboard is calculated by adding up the points earned over the 38 matchdays of the league.
If two or more teams finish with the same number of points in the standings, the following criteria will be used to determine their ranking:
  - Total points earned in individual matches
  - Total goals scored
  - Goal difference
  - Head-to-head ranking (direct encounters)


  
  

