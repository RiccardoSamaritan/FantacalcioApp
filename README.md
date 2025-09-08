[![PyPI Version][pypi-version-shield]][pypi-url]
[![Forks][forks-shield]][forks-url]
[![Stars][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]

# About

A comprehensive Python library for simulating Italian fantasy football (Fantacalcio) seasons with probabilistic algorithms, multi-season support, and flexible team management.

> [!NOTE]
> This library is designed to support data science and machine learning projects in the fantasy football domain. It provides realistic season simulations and statistical analysis tools for research, not to replace the original game experience.

# Features

- **Multi-Season Support**: Simulate different seasons (2024-25, 2023-24, 2022-23, 2021-22) with automatic data directory management
- **Multiple Input Formats**: Load teams from JSON, CSV files, or pandas DataFrames
- **Probabilistic Simulation**: Probabilistic algorithms eliminate luck factor for realistic season outcomes
- **Flexible Configuration**: Support for various team compositions and formation rules.

The app takes as input a given number of teams (usually a multiple of 2 in a range between 8 and 12) with 25 players (3 goalkeepers, 8 defenders, 8 midfielders and 6 forwards), which is the most common format used in the game. 

# Game Rules

## Formation

To simplify the implementation, the following rules have been applied to fantasy football by default:
  - The only allowed formation is 4-3-3, which means 1 goalkeeper, 4 defenders, 3 midfielders and 3 forwards. If there are not enough players in a role with a valid vote, a player with a null vote will be fielded anyway.
  
  - The user doesn't field players; instead, they are automatically selected based on the highest "fantavoto", while respecting positional requirements.

## Bonus and Malus
  The following bonus and malus are applied to a player's vote in order to calculate his "fantavoto":
   - +3 for each goal or penalty scored;
   - +1 for each assist;
   - -1 for each goal taken (applied only to goalkeepers);
   - -3 for each missed penalty;
   - +3 for each saved penalty (applied only to goalkeepers);
   - -0,5 if he gets a yellow card;
   - -1 if he gets a red card;
   - -2 for each autogoal;
   - +1 if he keeps a clean sheet (applied only to goalkeepers).

## Defense Modifier
  The defense modifier is used, which awards bonus points to the team based on the average rating of the 4 defenders:
   - If the average rating is < 6, bonus +1
   - If the average rating is ≥ 6 and < 6.25, bonus +2
   - If the average rating is ≥ 6.25 and < 6.5, bonus +3
   - If the average rating is ≥ 6.5 and < 6.75, bonus +4
   - If the average rating is ≥ 6.75 and < 7, bonus +5
   - If the average rating is ≥ 7 and < 7.25, bonus +6
   - If the average rating is ≥ 7.25, bonus +7
  The modifier is applied only if 4 defenders are fielded.

# Installation

Before installing the package, make sure you have **`Python 3.8` or higher** installed on your system.
In case you want to avoid any conflicts with your system's Python packages, you might want to create (and activate) a dedicated virtual environment:

```bash
python -m venv /path/to/fantacalciosimulator_env
source /path/to/fantacalciosimulator_env/bin/activate
```

## Install via PIP

You can install the package from the `Python Package Index (PyPI)` using pip:

```bash
pip install fantacalciosimulator
```
## Installing from source

1. Clone the repository:
   
   ```bash
   git clone https://github.com/RiccardoSamaritan/FantacalcioSimulator
   ```

2. Move into the repository directory and install the package with:
   
   ```bash
   cd FantacalcioSimulator/
   pip install .
   ```

# Quick Start

## Basic Usage

```python
from fantacalciosimulator import FantacalcioSimulator

# Initialize simulator with season and teams file
simulator = FantacalcioSimulator(
    season_year="2024-25",
    teams_file="teams_input_example.csv"
)

# Simulate complete season
results = simulator.simulate_season("My Fantasy League 2024-25")

# Display final table
print(simulator.get_final_table())
```

## Using Different Input Formats

### CSV Format
```python
# CSV with format: team_name,player_name,role
simulator = FantacalcioSimulator("2024-25", "teams.csv")
```

### JSON Format
```python
# JSON with nested team structure
simulator = FantacalcioSimulator("2024-25", "teams.json")
```

### Pandas DataFrame
```python
import pandas as pd
from fantacalciosimulator import FantacalcioSimulator

df = pd.read_csv("teams.csv")
simulator = FantacalcioSimulator.from_dataframe("2024-25", df)
```

## Configuration Options

```python
# Disable defense modifier
simulator = FantacalcioSimulator(
    season_year="2024-25",
    teams_file="teams.csv",
    defense_modifier=False
)

# Custom data directory
simulator = FantacalcioSimulator(
    season_year="2024-25", 
    teams_file="teams.csv",
    data_dir="custom_data_path"
)
```

## Advanced Usage Examples

### Complete Analysis Workflow
```python
from fantacalciosimulator import FantacalcioSimulator

# Initialize and simulate
simulator = FantacalcioSimulator("2024-25", "teams.csv")
results = simulator.simulate_season("My League")

# Get detailed team information
teams_info = simulator.get_teams_info()
for team in teams_info:
    print(f"{team['name']}: {team['total_players']} players, Valid: {team['valid_composition']}")

# Analyze specific team progression
team_progression = simulator.get_team_progression("Team Alpha")
print(f"Final points: {team_progression['final_total']}")

# Display championship results
print(f"Champion: {results['champion']} with {results['champion_points']} points")
print(f"Highest fantasy score: {results['highest_fantasy_score']} by {results['highest_fantasy_team']}")
```

### Quick Simulation Function
```python
from fantacalciosimulator import quick_simulation

# One-line season simulation
results = quick_simulation(
    season_year="2024-25",
    teams_file="teams.csv",
    season_name="Championship 2025"
)
```

### Team Validation
```python
from fantacalciosimulator import load_and_validate_teams

# Validate teams before simulation
teams_info = load_and_validate_teams("2024-25", "teams.csv")
valid_teams = [t for t in teams_info if t['valid_composition']]
print(f"{len(valid_teams)} valid teams out of {len(teams_info)}")
```

# Data Sources
 
**`FantacalcioSimulator`** matchday statistics are taken from [Fantacalcio.it](https://www.fantacalcio.it/voti-fantacalcio-serie-a), one of the most popular Italian fantasy football platforms.

Other useful resources from the same site are:
- [Player fantasy market value](https://www.fantacalcio.it/quotazioni-fantacalcio)
- [Player statistics](https://www.fantacalcio.it/statistiche-serie-a)
- [Goalkeeper grid](https://www.fantacalcio.it/griglia-portieri)
- [Penalty takers](https://www.fantacalcio.it/rigoristi-serie-a)

<!-- Badge definitions -->
[pypi-version-shield]: https://img.shields.io/pypi/v/fantacalciosimulator?style=for-the-badge&logo=pypi&logoColor=white
[pypi-url]: https://pypi.org/project/fantacalciosimulator/
[forks-shield]: https://img.shields.io/github/forks/RiccardoSamaritan/FantacalcioSimulator?style=for-the-badge
[forks-url]: https://github.com/RiccardoSamaritan/FantacalcioSimulator/network/members
[stars-shield]: https://img.shields.io/github/stars/RiccardoSamaritan/FantacalcioSimulator?style=for-the-badge
[stars-url]: https://github.com/RiccardoSamaritan/FantacalcioSimulator/stargazers
[issues-shield]: https://img.shields.io/github/issues/RiccardoSamaritan/FantacalcioSimulator?style=for-the-badge
[issues-url]: https://github.com/RiccardoSamaritan/FantacalcioSimulator/issues
[license-shield]: https://img.shields.io/github/license/RiccardoSamaritan/FantacalcioSimulator?style=for-the-badge
[license-url]: https://github.com/RiccardoSamaritan/FantacalcioSimulator/blob/main/LICENSE