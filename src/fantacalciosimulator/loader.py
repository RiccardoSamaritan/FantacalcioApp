import json
import pandas as pd
from typing import List, Dict, Union
from pathlib import Path
from .team import Team
from .player import Player

def create_name_to_code_mapping(csv_file: str) -> Dict[str, int]:
    """
    Create a mapping from player names to their codes.
    
    Args:
        csv_file: Path to CSV file
        
    Returns:
        Dictionary mapping player names to their codes
    """
    if not Path(csv_file).exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    df = pd.read_csv(csv_file)
    name_to_code = {}
    
    for _, row in df.iterrows():
        name = row['Name']
        cod = int(row['Cod'])
        name_to_code[name] = cod
    
    return name_to_code

def load_teams_from_json(json_file: str, data_dir: str = "data") -> List[Team]:
    """
    Load team configurations from JSON file.

    Args:
        json_file: Path to JSON file containing team configurations
        data_dir: Directory containing matchday CSV files to map names to codes
        
    Returns:
        List of Team objects with player codes assigned
    """
    json_path = Path(json_file)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    csv_files = list(Path(data_dir).glob("matchday*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")
    
    first_csv = sorted(csv_files)[0]
    name_to_code = create_name_to_code_mapping(first_csv)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        teams_config = json.load(f)
    
    teams = []
    for team_config in teams_config:
        team_name = team_config['name']
        
        if 'players' in team_config:
            player_codes = team_config['players']
        else:
            player_codes = []

            for role_key in ['goalkeepers', 'defenders', 'midfielders', 'forwards']:
                if role_key in team_config:
                    for player_info in team_config[role_key]:
                        player_name = player_info.split(' (')[0].strip()
                        
                        if player_name in name_to_code:
                            player_codes.append(name_to_code[player_name])
                        else:
                            print(f"Warning: Player '{player_name}' not found in CSV data")

        team = Team(name=team_name, player_codes=player_codes)
        teams.append(team)
    
    return teams

def load_teams_from_csv(csv_file: str, data_dir: str = "data") -> List[Team]:
    """
    Load team configurations from CSV file.
    
    Expected CSV format:
    team_name,player_name,role
    Team Alpha,Fazzini (Empoli),midfielder
    Team Alpha,Carnesecchi (Atalanta),goalkeeper
    Team Alpha,Tomori (Milan),defender
    
    Args:
        csv_file: Path to CSV file containing team configurations
        data_dir: Directory containing matchday CSV files to map names to codes
        
    Returns:
        List of Team objects with player codes assigned
    """
    csv_path = Path(csv_file)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    teams_df = pd.read_csv(csv_path)

    required_columns = ['team_name', 'player_name', 'role']
    missing_columns = [col for col in required_columns if col not in teams_df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in CSV: {missing_columns}")

    matchday_csv_files = list(Path(data_dir).glob("matchday*.csv"))
    if not matchday_csv_files:
        raise FileNotFoundError(f"No matchday CSV files found in {data_dir}")
    
    first_csv = sorted(matchday_csv_files)[0]
    name_to_code = create_name_to_code_mapping(str(first_csv))
    
    teams = []
    for team_name, team_data in teams_df.groupby('team_name'):
        player_codes = []
        
        for _, player_row in team_data.iterrows():
            player_name = player_row['player_name']
            role = player_row['role']
            
            player_name_clean = player_name.split(' (')[0].strip()
            
            if player_name_clean in name_to_code:
                player_codes.append(name_to_code[player_name_clean])
            else:
                print(f"Warning: Player '{player_name_clean}' not found in CSV data")
        
        team = Team(name=team_name, player_codes=player_codes)
        teams.append(team)
    
    return teams

def load_teams_from_dataframe(df: pd.DataFrame, data_dir: str = "data") -> List[Team]:
    """
    Load team configurations from pandas DataFrame.
    
    Expected DataFrame format:
    Columns: team_name, player_name, role
    Example data:
    team_name       player_name              role
    Team Alpha      Fazzini (Empoli)        midfielder
    Team Alpha      Carnesecchi (Atalanta)  goalkeeper
    Team Alpha      Tomori (Milan)          defender

    Args:
        df: DataFrame containing team configurations
        data_dir: Directory containing matchday CSV files to map names to codes
        
    Returns:
        List of Team objects with player codes assigned
    """
    required_columns = ['team_name', 'player_name', 'role']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in DataFrame: {missing_columns}")
 
    matchday_csv_files = list(Path(data_dir).glob("matchday*.csv"))
    if not matchday_csv_files:
        raise FileNotFoundError(f"No matchday CSV files found in {data_dir}")
    
    first_csv = sorted(matchday_csv_files)[0]
    name_to_code = create_name_to_code_mapping(str(first_csv))

    teams = []
    for team_name, team_data in df.groupby('team_name'):
        player_codes = []
        
        for _, player_row in team_data.iterrows():
            player_name = player_row['player_name']
            
            player_name_clean = player_name.split(' (')[0].strip()
            
            if player_name_clean in name_to_code:
                player_codes.append(name_to_code[player_name_clean])
            else:
                print(f"Warning: Player '{player_name_clean}' not found in CSV data")
        
        team = Team(name=team_name, player_codes=player_codes)
        teams.append(team)
    
    return teams

def load_player_data_from_matchday_csv(csv_file: str) -> Dict[int, Dict]:
    """
    Load player data from a matchday CSV file.
    
    Args:
        csv_file: Path to CSV file
        
    Returns:
        Dictionary mapping player codes to their data
    """
    if not Path(csv_file).exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    df = pd.read_csv(csv_file)
    players_data = {}
    
    for _, row in df.iterrows():
        cod = int(row['Cod'])
        players_data[cod] = {
            'Team': row['Team'],
            'Role': row['Role'],
            'Name': row['Name'],
            'Rating': row['Rating'],
            'Gf': row['Gf'] if pd.notna(row['Gf']) else 0,
            'Gs': row['Gs'] if pd.notna(row['Gs']) else 0,
            'Rp': row['Rp'] if pd.notna(row['Rp']) else 0,
            'Rs': row['Rs'] if pd.notna(row['Rs']) else 0,
            'Rf': row['Rf'] if pd.notna(row['Rf']) else 0,
            'Au': row['Au'] if pd.notna(row['Au']) else 0,
            'Amm': row['Amm'] if pd.notna(row['Amm']) else 0,
            'Esp': row['Esp'] if pd.notna(row['Esp']) else 0,
            'Ass': row['Ass'] if pd.notna(row['Ass']) else 0
        }
    
    return players_data

def populate_teams_with_players(teams: List[Team], data_dir: str = "data") -> List[Team]:
    """
    Populate teams with actual Player objects from CSV data.
    
    Args:
        teams: List of Team objects with player codes
        data_dir: Directory containing CSV files
        
    Returns:
        List of Team objects populated with Player objects
    """
    data_path = Path(data_dir)
    csv_files = list(data_path.glob("matchday*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")

    first_csv = sorted(csv_files)[0]
    players_data = load_player_data_from_matchday_csv(first_csv)
    
    role_mapping = {
        'P': 'G',
        'D': 'D', 
        'C': 'M',
        'A': 'F'
    }

    for team in teams:
        for cod in team.player_codes:
            if cod in players_data:
                data = players_data[cod]
                role = role_mapping.get(data['Role'], data['Role'])
                
                player = Player(
                    cod=cod,
                    role=role,
                    name=data['Name'],
                    team=data['Team']
                )
                
                team.add_player(player)
            else:
                print(f"Warning: Player code {cod} not found in CSV data")

        if not team.validate_team_composition():
            stats = team.get_team_stats()
            print(f"Warning: Team {team.name} invalid composition - "
                  f"P:{stats['goalkeepers']} D:{stats['defenders']} "
                  f"C:{stats['midfielders']} A:{stats['forwards']}")
    
    return teams

def load_all_matchday_stats(teams: List[Team], data_dir: str = "data") -> List[Team]:
    """
    Load statistics for all matchdays from CSV files and populate player stats.
    
    Args:
        teams: List of Team objects with Player objects already created
        data_dir: Directory containing CSV files
        
    Returns:
        List of Team objects with complete player statistics
    """
    data_path = Path(data_dir)
    csv_files = list(data_path.glob("matchday*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")

    def extract_matchday_num(path):
        try:
            name = path.stem
            return int(name.replace('matchday', ''))
        except ValueError:
            return 0
    
    csv_files = sorted(csv_files, key=extract_matchday_num)

    all_players = {}
    for team in teams:
        for player in team.players:
            all_players[player.cod] = player

    for csv_file in csv_files:
        matchday_num = extract_matchday_num(csv_file)
        if matchday_num == 0:
            continue
        
        print(f"Loading matchday {matchday_num} stats...")
        matchday_data = load_player_data_from_matchday_csv(csv_file)
        
        for cod, data in matchday_data.items():
            if cod in all_players:
                all_players[cod].add_matchday_stats(matchday_num, data)
                all_players[cod].add_matchday_fantavoto(matchday_num)
    
    print(f"Loaded stats for {len(csv_files)} matchdays")
    return teams

def setup_complete_teams(teams_source: Union[str, pd.DataFrame], data_dir: str = "data") -> List[Team]:
    """
    Complete team setup pipeline supporting multiple input formats.
    
    This function performs complete team setup from various sources: JSON files,
    CSV files, or pandas DataFrames. It automatically detects the input format
    and uses the appropriate loading method.
    
    Supported Input Formats:
    - JSON files
    - CSV files
    - Pandas DataFrame
    
    Args:
        teams_source: Path to teams file (JSON/CSV) or pandas DataFrame with team data
        data_dir: Directory containing matchday CSV files
        
    Returns:
        List of fully configured Team objects with all player statistics loaded
        
    Raises:
        FileNotFoundError: If teams file or matchday data directory doesn't exist
        ValueError: If unsupported file format or invalid DataFrame structure
    """
    if isinstance(teams_source, pd.DataFrame):
        teams = load_teams_from_dataframe(teams_source, data_dir)

    elif isinstance(teams_source, str):
        teams_path = Path(teams_source)
        if not teams_path.exists():
            raise FileNotFoundError(f"Teams file not found: {teams_source}")

        if teams_path.suffix.lower() == '.csv':
            teams = load_teams_from_csv(teams_source, data_dir)
        elif teams_path.suffix.lower() == '.json':
            teams = load_teams_from_json(teams_source, data_dir)
        else:
            raise ValueError(f"Unsupported file format: {teams_path.suffix}. Supported formats: .json, .csv")
    
    else:
        raise ValueError("teams_source must be a file path (str) or pandas DataFrame")

    teams = populate_teams_with_players(teams, data_dir)
    teams = load_all_matchday_stats(teams, data_dir)
    
    return teams