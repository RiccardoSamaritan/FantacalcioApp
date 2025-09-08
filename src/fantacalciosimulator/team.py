from typing import List, Dict
from .player import Player
from .role import Role

class Team:
    """
    Class to represent a Fantacalcio team with 25 players and formation management.
    """
    
    def __init__(self, name: str, player_codes: List[int] = None):
        self.name = name
        self.players: List[Player] = []
        self.lineup: Dict[int, List[Player]] = {}  # matchday -> selected players
        self.total_scores: Dict[int, float] = {}  # matchday -> total team score
        
        if player_codes:
            self.player_codes = player_codes
    
    def add_player(self, player: Player):
        """Add a player to the team"""
        if len(self.players) >= 25:
            raise ValueError("Team cannot have more than 25 players")
        self.players.append(player)
    
    def validate_team_composition(self) -> bool:
        """
        Validate that the team has the correct number of players per role:
        - 3 goalkeepers
        - 8 defenders  
        - 8 midfielders
        - 6 forwards
        """
        role_counts = {
            Role.GOALKEEPER: 0,
            Role.DEFENDER: 0,
            Role.MIDFIELDER: 0,
            Role.FORWARD: 0
        }
        
        for player in self.players:
            if player.role in role_counts:
                role_counts[player.role] += 1
        
        return (role_counts[Role.GOALKEEPER] == 3 and
                role_counts[Role.DEFENDER] == 8 and
                role_counts[Role.MIDFIELDER] == 8 and
                role_counts[Role.FORWARD] == 6)
    
    def get_players_by_role(self, role: Role) -> List[Player]:
        """
        Get all players of a specific role
        """
        return [player for player in self.players if player.role == role]
    
    def select_lineup(self, matchday: int) -> List[Player]:
        """
        Select the best lineup for a matchday using 4-3-3 formation.
        Selects players with highest fantavoto, respecting positional requirements.
        If a player hasn't played (fantavoto = 0), they can still be selected.
        """
        lineup = []
        
        goalkeepers = self.get_players_by_role(Role.GOALKEEPER)
        goalkeepers.sort(key=lambda p: p.matchday_fantavoto.get(matchday, 0), reverse=True)
        lineup.extend(goalkeepers[:1])
        
        defenders = self.get_players_by_role(Role.DEFENDER)
        defenders.sort(key=lambda p: p.matchday_fantavoto.get(matchday, 0), reverse=True)
        lineup.extend(defenders[:4])

        midfielders = self.get_players_by_role(Role.MIDFIELDER)
        midfielders.sort(key=lambda p: p.matchday_fantavoto.get(matchday, 0), reverse=True)
        lineup.extend(midfielders[:3])

        forwards = self.get_players_by_role(Role.FORWARD)
        forwards.sort(key=lambda p: p.matchday_fantavoto.get(matchday, 0), reverse=True)
        lineup.extend(forwards[:3])
        
        self.lineup[matchday] = lineup
        return lineup
    
    def calculate_defense_modifier(self, matchday: int) -> float:
        """
        Calculate defense modifier based on average rating of 4 defenders.
        Only applied if exactly 4 defenders are fielded.
        """
        if matchday not in self.lineup:
            return 0.0
        
        defenders = [p for p in self.lineup[matchday] if p.role == Role.DEFENDER]
        
        if len(defenders) != 4:
            return 0.0

        ratings = []
        for defender in defenders:
            stats = defender.get_stats(matchday)
            if stats and stats.rating > 0:
                ratings.append(stats.rating)
        
        if not ratings:
            return 0.0
        
        avg_rating = sum(ratings) / len(ratings)

        if avg_rating < 6:
            return 1.0
        elif avg_rating < 6.25:
            return 2.0
        elif avg_rating < 6.5:
            return 3.0
        elif avg_rating < 6.75:
            return 4.0
        elif avg_rating < 7:
            return 5.0
        elif avg_rating < 7.25:
            return 6.0
        else:
            return 7.0
    
    def calculate_total_score(self, matchday: int, defense_modifier: bool = True) -> float:
        """
        Calculate total team score for a matchday, optionally including defense modifier.
        
        Args:
            matchday: The matchday number (1-38)
            defense_modifier: Whether to apply defense modifier bonus (default: True)
            
        Returns:
            Total team score including optional defense modifier
        """
        if matchday not in self.lineup:
            self.select_lineup(matchday)
        
        total_score = 0.0

        for player in self.lineup[matchday]:
            fantavoto = player.matchday_fantavoto.get(matchday, 0)
            total_score += fantavoto

        if defense_modifier:
            defense_bonus = self.calculate_defense_modifier(matchday)
            total_score += defense_bonus
        
        self.total_scores[matchday] = total_score
        return total_score
    
    def get_lineup_summary(self, matchday: int, defense_modifier: bool = True) -> str:
        """
        Get a formatted summary of the lineup for a matchday
        Args:
            matchday: The matchday number (1-38)
            defense_modifier: Whether to show defense modifier bonus (default: True)
        Returns:
            Formatted string summary of the lineup and scores
        """
        if matchday not in self.lineup:
            return "No lineup selected for this matchday"
        
        summary = f"\n=== {self.name} - Matchday {matchday} ===\n"

        lineup_by_role = {
            Role.GOALKEEPER: [],
            Role.DEFENDER: [],
            Role.MIDFIELDER: [],
            Role.FORWARD: []
        }
        
        for player in self.lineup[matchday]:
            lineup_by_role[player.role].append(player)

        for role, players in lineup_by_role.items():
            if players:
                summary += f"\n{role.value}:\n"
                for player in players:
                    fantavoto = player.matchday_fantavoto.get(matchday, 0)
                    summary += f"  {player.name} ({player.real_team}): {fantavoto}\n"
        
        if defense_modifier:
            defense_bonus = self.calculate_defense_modifier(matchday)
            summary += f"\nDefense Modifier: +{defense_bonus}"
        else:
            summary += f"\nDefense Modifier: Disabled"
        
        total_score = self.total_scores.get(matchday, 0)
        summary += f"\nTotal Score: {total_score}\n"
        
        return summary
    
    def get_team_stats(self) -> Dict:
        """
        Get overall team statistics
        """
        return {
            'name': self.name,
            'total_players': len(self.players),
            'goalkeepers': len(self.get_players_by_role(Role.GOALKEEPER)),
            'defenders': len(self.get_players_by_role(Role.DEFENDER)),
            'midfielders': len(self.get_players_by_role(Role.MIDFIELDER)),
            'forwards': len(self.get_players_by_role(Role.FORWARD)),
            'valid_composition': self.validate_team_composition(),
            'matchdays_played': len(self.lineup)
        }
    
    def __str__(self):
        return f"Team {self.name} ({len(self.players)} players)"
    
    def __repr__(self):
        return f"Team(name='{self.name}', players={len(self.players)})"