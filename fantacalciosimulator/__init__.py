"""
Fantacalcio Simulator - A comprehensive Python library for Italian fantasy football simulation.

This package provides tools for:
- Processing matchday data Excel from Fantacalcio.it
- Simulating complete seasons with probabilistic results
- Team management and validation
- Statistical analysis and reporting
"""

from .lib import (
    FantacalcioSimulator,
    FantacalcioSimulatorError,
    FileNotFoundError,
    InvalidTeamConfigError,
    quick_simulation,
    load_and_validate_teams
)

from .loader import setup_complete_teams
from .probabilisticseason import ProbabilisticSeason
from .team import Team
from .player import Player
from .role import Role
from .playerstats import PlayerStats

__version__ = "0.1.2"
__author__ = "Riccardo Samaritan"
__email__ = "riccardo.samaritan@gmail.com"

__all__ = [
    # Main library API
    "FantacalcioSimulator",
    "FantacalcioSimulatorError", 
    "FileNotFoundError",
    "InvalidTeamConfigError",
    "quick_simulation",
    "load_and_validate_teams",
    
    # Core components
    "setup_complete_teams",
    "ProbabilisticSeason",
    "Team",
    "Player", 
    "Role",
    "PlayerStats"
]