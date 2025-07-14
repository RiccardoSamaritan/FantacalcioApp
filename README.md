# Fantacalcio App

This is a Python-based Fantacalcio (Italian fantasy football) simulation application. The project scrapes data from the [Fantacalcio Official Website](https://www.fantacalcio.it/voti-fantacalcio-serie-a) and simulates fantasy football seasons with automatic player selection based on performance metrics.

The app takes as input a given number of teams (usually a multiple of 2 in a range between 8 and 12) with 25 players (3 goalkeepers, 8 defenders, 8 midfielders and 6 forwards), which is the most common format used in the game. 

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
    The modifier is applied only if 4 defenders are fielded.

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

## Installation and Setup

### Development Environment

1. **Create and activate virtual environment:**
   ```bash
   python -m venv fantacalcio_env
   source fantacalcio_env/bin/activate  # Linux/macOS
   # or
   fantacalcio_env\Scripts\activate  # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Main Dependencies
- `pandas>=2.0.0` - Data processing and CSV handling
- `send2trash>=1.8.0` - Safe file deletion after processing

## Project Architecture

### Core Classes
- **Player** (`player.py`): Represents individual players with season statistics and fantavoto calculations
- **PlayerStats** (`playerstats.py`): Dataclass holding per-matchday statistics (goals, assists, cards, etc.)
- **Role** (`role.py`): Enum for player positions (Goalkeeper, Defender, Midfielder, Forward)

### Data Processing Pipeline
1. **Data Collection**: Excel files downloaded from fantacalcio.it containing matchday statistics
2. **Data Conversion**: `data/dataprocessor.py` converts Excel files to CSV format with automatic team detection
3. **Data Structure**: CSV files named `matchday{N}.csv` containing all player statistics per matchday

## Data Retrieval 

Download Excel files from [Fantacalcio.it](https://www.fantacalcio.it/voti-fantacalcio-serie-a). Be sure to select the season that you want to simulate and to download data for each matchday from 1 to 38.
Put the downloaded files into the "data" folder in order to be ready for the data processing.

## Data Processing

### Excel to CSV Converter

This project includes a Python script (`data/dataprocessor.py`) to convert the official Excel files from Fantacalcio.it into clean CSV format for easier data processing.

#### Features:
- **Automatic team detection**: Identifies team names from the Excel structure.
- **Matchday extraction**: Automatically extracts the matchday number from the filename.
- **Player-only extraction**: Filters out headers, titles, and coaches (excludes "ALL" role).
- **Complete data preservation**: Extracts all player statistics (goals, assists, cards, etc.).
- **Auto-cleanup**: Moves processed Excel files to trash after successful conversion.
- **Output**: Saves the cleaned data in a CSV file named `matchday{i}.csv`, where `i` is the matchday number.
#### Usage:

1. **Single file conversion:**
   ```bash
   python data/dataprocessor.py Voti_Fantacalcio_Stagione_2024_25_Giornata_1.xlsx
   ```

2. **Batch conversion (Linux/macOS):**
   ```bash
   for i in {1..38}; do
       python data/dataprocessor.py Voti_Fantacalcio_Stagione_2024_25_Giornata_${i}.xlsx
   done
   ```

3. **Batch conversion (Windows):**
   ```cmd
   for /L %i in (1,1,38) do (
       python data/dataprocessor.py Voti_Fantacalcio_Stagione_2024_25_Giornata_%i.xlsx
   )
   ```

#### Example Output:
```csv
Team,Cod,Role,Name,Rating,Gf,Gs,Rp,Rs,Rf,Au,Amm,Esp,Ass
Atalanta,2792,P,Musso,6,0,0,0,0,0,0,0,0,0
Atalanta,554,D,Zappacosta,6.5,0,0,0,0,0,0,0,0,0
Atalanta,4947,C,Brescianini,8,2,0,0,0,0,0,0,0,0
Bologna,133,P,Skorupski,6.5,0,0,0,0,0,0,0,0,0
```

## Game Logic Implementation

### Formation System
- **Fixed 4-3-3 formation**: 1 goalkeeper, 4 defenders, 3 midfielders, 3 forwards
- **Automatic player selection**: Players are selected based on highest "fantavoto" (fantasy score)
- **Season simulation**: 38 matchdays with a scoring systems based summatory of player's "fantavoto" for each matchday.

### Fantavoto Calculation
The fantasy score calculation (`Player.calculate_fantavoto()`) includes:
- **Base rating**: Player's match rating
- **Goals**: +3 points each
- **Assists**: +1 point each
- **Missed penalties**: -3 points each
- **Saved penalties**: +3 points each (goalkeepers only)
- **Yellow cards**: -0.5 points each
- **Red cards**: -1 point each
- **Own goals**: -2 points each
- **Clean sheet bonus**: +1 point (goalkeepers only)
- **Goals conceded**: -1 point each (goalkeepers only)

### Data Structure Details
- **Player Statistics**: Ratings with "*" are converted to 0.0 (injured/suspended players)
- **Player Codes**: Unique identifiers (`cod`) linking to real Serie A players
- **Matchday Tracking**: Statistics are stored per matchday for season-long analysis

## Testing

The project includes `test_teams.json` with sample team configurations containing 8 teams of 25 players each (3 goalkeepers, 8 defenders, 8 midfielders, 6 forwards), referenced by player codes.
