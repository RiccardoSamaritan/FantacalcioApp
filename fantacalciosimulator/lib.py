"""
Fantacalcio Simulator Library - Simplified API
"""

from .loader import setup_complete_teams, load_teams_from_csv, load_teams_from_dataframe, populate_teams_with_players, load_all_matchday_stats
from .probabilisticseason import ProbabilisticSeason
from typing import List, Dict, Optional
import logging
import pandas as pd
from pathlib import Path


class FantacalcioSimulatorError(Exception):
    """Base exception for Fantacalcio simulator errors."""
    pass


class FileNotFoundError(FantacalcioSimulatorError):
    """Raised when required files are not found."""
    pass


class InvalidTeamConfigError(FantacalcioSimulatorError):
    """Raised when team configuration is invalid."""
    pass


class FantacalcioSimulator:
    """
    Main class for interacting with the Fantacalcio simulator.
    """

    def __init__(self, season_year: str, teams_file: Optional[str] = None, data_dir: str = "data", log_level: str = "INFO", teams_data: Optional[List] = None, defense_modifier: bool = True):
        """
        Initialize the simulator.
        
        Args:
            season_year: Season to simulate (e.g., "2024-25", "2023-24")
            teams_file: Path to the teams configuration file (JSON or CSV). 
            data_dir: Base directory containing season subdirectories (default: "data")
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            teams_data: Pre-loaded teams data (alternative to teams_file)
            defense_modifier: Whether to apply defense modifier bonus (default: True)
        """
        self._setup_logging(log_level)
        

        if not season_year:
            raise InvalidTeamConfigError("season_year is required (e.g., '2024-25', '2023-24')")
        
        self.season_year = season_year
        self.data_dir = str(Path(data_dir) / season_year)

        if not Path(self.data_dir).exists():
            raise FileNotFoundError(f"Data directory for season '{season_year}' not found: {self.data_dir}")
        
        if teams_file is None and teams_data is None:
            raise InvalidTeamConfigError("Either teams_file or teams_data must be provided")
        
        if teams_file:
            self._validate_inputs(teams_file, self.data_dir)
        
        self.teams_file = teams_file
        self.teams = teams_data
        self.defense_modifier = defense_modifier
        self.season = None
        self._cached_teams_info = None
        
        init_msg = f"Fantacalcio Simulator initialized with season='{season_year}', data_dir='{self.data_dir}'"
        if teams_file:
            init_msg += f", teams_file='{teams_file}'"
        if teams_data:
            init_msg += f", teams_data provided ({len(teams_data)} teams)"
        self.logger.info(init_msg)
    
    def _setup_logging(self, log_level: str) -> None:
        """Setup logging configuration."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    def _validate_inputs(self, teams_file: str, data_dir: str) -> None:
        """Validate input parameters."""
        if not teams_file or not isinstance(teams_file, str):
            raise InvalidTeamConfigError("teams_file must be a non-empty string")
        
        if not data_dir or not isinstance(data_dir, str):
            raise InvalidTeamConfigError("data_dir must be a non-empty string")
        
        teams_path = Path(teams_file)
        if not teams_path.exists():
            raise FileNotFoundError(f"Teams file not found: {teams_file}")
        
        data_path = Path(data_dir)
        if not data_path.exists() or not data_path.is_dir():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    def load_teams(self) -> List:
        """
        Load teams from configuration file or use pre-loaded data.
        
        Returns:
            List of Team objects
            
        Raises:
            FileNotFoundError: If required files are missing
            InvalidTeamConfigError: If team configuration is invalid
        """
        if self.teams is not None:
            return self.teams
            
        if not self.teams_file:
            raise InvalidTeamConfigError("No teams_file provided and no teams_data available")
        
        try:
            self.logger.info("Loading teams configuration...")
            
            teams_path = Path(self.teams_file)
            if teams_path.suffix.lower() == '.csv':
                self.logger.info("Detected CSV format, loading teams from CSV...")
                teams = load_teams_from_csv(self.teams_file, self.data_dir)
                teams = populate_teams_with_players(teams, self.data_dir)
                self.teams = load_all_matchday_stats(teams, self.data_dir)
            elif teams_path.suffix.lower() == '.json':
                self.logger.info("Detected JSON format, loading teams from JSON...")
                self.teams = setup_complete_teams(self.teams_file, self.data_dir)
            else:
                raise InvalidTeamConfigError(f"Unsupported file format: {teams_path.suffix}. Supported formats: .csv, .json")
            
            if not self.teams:
                raise InvalidTeamConfigError("No teams were loaded from configuration")
            
            valid_teams = [t for t in self.teams if t.validate_team_composition()]
            if len(valid_teams) < len(self.teams):
                self.logger.warning(f"{len(self.teams) - len(valid_teams)} teams have invalid compositions")
            
            self.logger.info(f"Successfully loaded {len(self.teams)} teams")
            self._cached_teams_info = None
            return self.teams
            
        except Exception as e:
            self.logger.error(f"Failed to load teams: {str(e)}")
            raise
    
    def create_season(self, season_name: str = "Fantacalcio Season") -> 'ProbabilisticSeason':
        """
        Create a new season with loaded teams.
        
        Args:
            season_name: Name of the season
            
        Returns:
            ProbabilisticSeason object
            
        Raises:
            InvalidTeamConfigError: If no valid teams are available
        """
        if not season_name or not isinstance(season_name, str):
            raise InvalidTeamConfigError("season_name must be a non-empty string")
        
        if not self.teams:
            self.load_teams()
        
        valid_teams = [t for t in self.teams if t.validate_team_composition()]
        if len(valid_teams) < 2:
            raise InvalidTeamConfigError(f"Need at least 2 valid teams for a season, got {len(valid_teams)}")
        
        self.logger.info(f"Creating season '{season_name}' with {len(self.teams)} teams (defense_modifier={self.defense_modifier})")
        self.season = ProbabilisticSeason(self.teams, season_name, self.defense_modifier)
        return self.season
    
    def simulate_season(self, season_name: str = "Fantacalcio Season") -> Dict:
        """
        Simulate a complete season and return results.
        
        Args:
            season_name: Name of the season
            
        Returns:
            Dictionary containing season summary
            
        Raises:
            FantacalcioSimulatorError: If simulation fails
        """
        try:
            if not self.season:
                self.create_season(season_name)
            
            self.logger.info(f"Starting season simulation: {season_name}")
            results = self.season.process_complete_season()
            self.logger.info(f"Season simulation completed. Champion: {results.get('champion', 'Unknown')}")
            return results
            
        except Exception as e:
            self.logger.error(f"Season simulation failed: {str(e)}")
            raise FantacalcioSimulatorError(f"Season simulation failed: {str(e)}")
    
    def get_teams_info(self) -> List[Dict]:
        """
        Get information about all loaded teams (cached for performance).
        
        Returns:
            List of dictionaries with team information
        """
        if self._cached_teams_info is not None:
            return self._cached_teams_info
        
        if not self.teams:
            self.load_teams()
        
        teams_info = []
        for team in self.teams:
            try:
                stats = team.get_team_stats()
                teams_info.append({
                    'name': team.name,
                    'valid_composition': stats['valid_composition'],
                    'goalkeepers': stats['goalkeepers'],
                    'defenders': stats['defenders'],
                    'midfielders': stats['midfielders'],
                    'forwards': stats['forwards'],
                    'total_players': len(team.players)
                })
            except Exception as e:
                self.logger.warning(f"Error processing team {team.name}: {str(e)}")
        
        self._cached_teams_info = teams_info
        return teams_info
    
    def get_final_table(self) -> Optional[str]:
        """
        Get the formatted final table.
        
        Returns:
            Formatted table string or None if season not simulated
        """
        if not self.season:
            return None
        
        return self.season.get_formatted_table()
    
    
    @classmethod
    def from_dataframe(cls, season_year: str, teams_df: pd.DataFrame, data_dir: str = "data", log_level: str = "INFO", defense_modifier: bool = True) -> 'FantacalcioSimulator':
        """
        Create a FantacalcioSimulator from a pandas DataFrame containing teams configuration.
        
        Args:
            season_year: Season to simulate (e.g., "2024-25", "2023-24") - REQUIRED
            teams_df: DataFrame with columns: team_name, player_name, role
            data_dir: Base directory containing season subdirectories
            log_level: Logging level
            defense_modifier: Whether to apply defense modifier bonus (default: True)
            
        Returns:
            FantacalcioSimulator instance
        """
        full_data_dir = str(Path(data_dir) / season_year)
        
        teams = load_teams_from_dataframe(teams_df, full_data_dir)
        teams = populate_teams_with_players(teams, full_data_dir)
        teams = load_all_matchday_stats(teams, full_data_dir)

        return cls(season_year=season_year, teams_file=None, data_dir=data_dir, log_level=log_level, teams_data=teams, defense_modifier=defense_modifier)
    
    def get_team_progression(self, team_name: str) -> Optional[Dict]:
        """
        Get progression data for a specific team.
        
        Args:
            team_name: Name of the team
            
        Returns:
            Dictionary with team progression or None if not found
        """
        if not self.season:
            return None
        
        return self.season.get_team_progression(team_name)


def quick_simulation(season_year: str, 
                    teams_file: str, 
                    data_dir: str = "data",
                    season_name: str = "Fantacalcio Season") -> Dict:
    """
    Quick function to simulate a season with default parameters.
    
    Args:
        season_year: Season to simulate (e.g., "2024-25", "2023-24") - REQUIRED
        teams_file: Path to teams configuration file
        data_dir: Base directory containing season subdirectories
        season_name: Name of the season
        
    Returns:
        Season summary dictionary
    """
    simulator = FantacalcioSimulator(season_year, teams_file, data_dir)
    return simulator.simulate_season(season_name)


def load_and_validate_teams(season_year: str,
                           teams_file: str, 
                           data_dir: str = "data") -> List[Dict]:
    """
    Load teams and return validation information.
    
    Args:
        season_year: Season to simulate (e.g., "2024-25", "2023-24") - REQUIRED
        teams_file: Path to teams configuration file
        data_dir: Base directory containing season subdirectories
        
    Returns:
        List of team information dictionaries
    """
    simulator = FantacalcioSimulator(season_year, teams_file, data_dir)
    return simulator.get_teams_info()


