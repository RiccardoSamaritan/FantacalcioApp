from typing import Dict, Optional
from src.playerstats import PlayerStats
from src.role import Role

class Player:
    """
    Class to represent a player in Fantacalcio.
    """
    def __init__(self, cod: int, role: str, name: str, team: str):
        self.cod = cod
        self.role = Role(role)
        self.name = name
        self.real_team = team
        self.matchday_stats: Dict[int, PlayerStats] = {}
        self.matchday_fantavoto: Dict[int, float] = {}
    
    def add_matchday_stats(self, matchday: int, stats: Dict):
        """
        Add statistics for a specific matchday.
        """
        self.matchday_stats[matchday] = PlayerStats(
            rating=stats.get('Rating', 0),
            gf=stats.get('Gf', 0),
            gs=stats.get('Gs', 0),
            rp=stats.get('Rp', 0),
            rs=stats.get('Rs', 0),
            rf=stats.get('Rf', 0),
            au=stats.get('Au', 0),
            amm=stats.get('Amm', 0),
            esp=stats.get('Esp', 0),
            ass=stats.get('Ass', 0)
        )
    
    def add_matchday_fantavoto(self, matchday:int):
        """
        Add fantavoto for a specific matchday
        """
        self.matchday_fantavoto[matchday] = self.calculate_fantavoto(matchday)

    def get_stats(self, matchday: int) -> Optional[PlayerStats]:
        """Return stats from a specific matchday"""
        return self.matchday_stats.get(matchday)
    
    def calculate_fantavoto(self, matchday: int) -> float:
        """
        Calculate the "fantavoto" for a specific matchday
        """
        stats = self.get_stats(matchday)
        if not stats or stats.rating == 0:
            return 0.0
        
        fantavoto = stats.rating
        
        fantavoto += stats.gf * 3        
        fantavoto += stats.ass * 1       
        fantavoto -= stats.rp * 3        
        fantavoto += stats.rs * 3        
        fantavoto -= stats.amm * 0.5     
        fantavoto -= stats.esp * 1       
        fantavoto -= stats.au * 2        
        
        # Goalkeeper bonus for clean sheet
        if self.role == Role.GOALKEEPER and stats.gs == 0:
            fantavoto += 1
        
        # Goalkeeper malus for every goal conceded
        if self.role == Role.GOALKEEPER:
            fantavoto -= stats.gs * 1
        
        return round(fantavoto, 1)
    
    def has_played(self, matchday: int) -> bool:
        """Verify if a player has played in a specific matchday"""
        stats = self.get_stats(matchday)
        return stats is not None and stats.rating > 0
    
    def __str__(self):
        return f"{self.name} ({self.role.value}) - {self.real_team}"
    
    def __repr__(self):
        return f"Player(cod={self.cod}, name='{self.name}', role={self.role.value}, team='{self.real_team}')"