from typing import List, Dict
from team import Team

class SeasonTable:
    """
    Class to manage the season table for a team.
    """
    
    def __init__(self, team: Team):
        self.team = team
        self.total_points = 0.0  
        self.matchday_scores: Dict[int, float] = {} 
        self.matchdays_played = 0
    
    def add_matchday_score(self, matchday: int, score: float):
        """
        Add a score for a specific matchday.
        """
        if matchday not in self.matchday_scores:
            self.matchdays_played += 1
        
        self.matchday_scores[matchday] = score
        self.total_points = sum(self.matchday_scores.values())
    
    def get_stats(self) -> Dict:
        """
        Getter function to retrieve team statistics.
        """
        avg_score = self.total_points / max(self.matchdays_played, 1)
        
        return {
            'team': self.team.name,
            'total_points': round(self.total_points, 1),
            'matchdays_played': self.matchdays_played,
            'average_score': round(avg_score, 1),
            'best_score': max(self.matchday_scores.values()) if self.matchday_scores else 0.0,
            'worst_score': min(self.matchday_scores.values()) if self.matchday_scores else 0.0
        }

class Season:
    """
    Class to manage the Fantacalcio season, including teams and matchdays.
    """
    
    def __init__(self, teams: List[Team], name: str = "Fantacalcio Season"):
        self.name = name
        self.teams = teams
        self.table: Dict[str, SeasonTable] = {}
        self.current_matchday = 1
        self.season_completed = False
        
        for team in teams:
            self.table[team.name] = SeasonTable(team)
    
    def process_matchday(self, matchday: int) -> Dict[str, float]:
        """
        Calculate scores for all teams for a specific matchday.
        
        Args:
            matchday: Matchday number (1-38)
            
        Returns:
            Dictonary with team names and their scores for this matchday
        """
        if matchday > 38 or matchday < 1:
            raise ValueError("Matchday must be between 1 and 38")
        
        matchday_scores = {}
        
        for team in self.teams:
            score = team.calculate_total_score(matchday)
            matchday_scores[team.name] = score
            self.table[team.name].add_matchday_score(matchday, score)
        
        if matchday == self.current_matchday:
            self.current_matchday += 1
        
        return matchday_scores
    
    def process_complete_season(self) -> Dict:
        """
        Process the entire season, calculating scores for all matchdays.
        
        Returns:
            Dictionary with season summary including final table and statistics
        """
        print(f"Start processing {self.name}...")
        
        for matchday in range(1, 39):
            print(f"Processing matchday {matchday}...")
            self.process_matchday(matchday)
        
        self.season_completed = True
        print("Season completed !")
        
        return self.get_season_summary()
    
    def get_season_table(self) -> List[Dict]:
        """
        Get the current season table with team statistics.
        Returns:
            List of dictionaries with team statistics sorted by total points.
        """
        table_data = [entry.get_stats() for entry in self.table.values()]
  
        table_data.sort(key=lambda x: x['total_points'], reverse=True)

        for i, team_data in enumerate(table_data):
            team_data['position'] = i + 1
        
        return table_data
    
    def get_formatted_table(self) -> str:
        """
        Get a formatted string representation of the season table.
        """
        table = self.get_season_table()
        
        output = f"\n=== {self.name} - Final Leaderboard ===\n"
        output += "Pos | Team           | Matchdays | Tot Points | Avg. | Best Score | Worst score\n"
        output += "-" * 80 + "\n"
        
        for team_data in table:
            output += f"{team_data['position']:2d}  | "
            output += f"{team_data['team']:<17} | "
            output += f"{team_data['matchdays_played']:8d} | "
            output += f"{team_data['total_points']:9.1f} | "
            output += f"{team_data['average_score']:6.1f} | "
            output += f"{team_data['best_score']:7.1f} | "
            output += f"{team_data['worst_score']:7.1f}\n"
        
        return output
    
    def get_matchday_scores(self, matchday: int) -> str:
        """
        Get scores for a specific matchday.
        """
        if matchday < 1 or matchday > 38:
            return f"Unvalid matchday: {matchday}"
        
        scores = []
        for team_name, season_table in self.table.items():
            if matchday in season_table.matchday_scores:
                scores.append((team_name, season_table.matchday_scores[matchday]))
        
        if not scores:
            return f"No scores available for matchday {matchday}"
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        output = f"\n=== Scores for matchday {matchday} ===\n"
        for i, (team_name, score) in enumerate(scores, 1):
            output += f"{i:2d}. {team_name:<20} {score:6.1f}\n"
        
        return output
    
    def get_season_summary(self) -> Dict:
        """
        Get a summary of the season including final table and statistics.
        """
        final_table = self.get_season_table()

        all_scores = []
        for season_table in self.table.values():
            all_scores.extend(season_table.matchday_scores.values())
        
        total_matchdays = sum(st.matchdays_played for st in self.table.values())
        
        highest_score_team = max(final_table, key=lambda x: x['best_score'])
        most_consistent_team = min(final_table, key=lambda x: x['best_score'] - x['worst_score'])
        
        return {
            'season_name': self.name,
            'teams': len(self.teams),
            'total_matchdays_processed': total_matchdays,
            'average_score_per_matchday': round(sum(all_scores) / len(all_scores), 1) if all_scores else 0,
            'final_table': final_table,
            'champion': final_table[0]['team'] if final_table else None,
            'champion_points': final_table[0]['total_points'] if final_table else 0,
            'highest_single_score': highest_score_team['best_score'],
            'highest_score_team': highest_score_team['team'],
            'most_consistent_team': most_consistent_team['team'],
            'season_completed': self.season_completed
        }
    
    def get_team_progression(self, team_name: str) -> Dict:
        """
        Get the progression of a specific team throughout the season.
        """
        if team_name not in self.table:
            return {}
        
        season_table = self.table[team_name]
        progression = []
        cumulative_points = 0
        
        for matchday in range(1, 39):
            if matchday in season_table.matchday_scores:
                score = season_table.matchday_scores[matchday]
                cumulative_points += score
                progression.append({
                    'matchday': matchday,
                    'score': score,
                    'cumulative_points': round(cumulative_points, 1)
                })
        
        return {
            'team': team_name,
            'progression': progression,
            'final_total': cumulative_points
        }
    
    def __str__(self):
        return f"{self.name} ({len(self.teams)} teams, Matchday {self.current_matchday})"
    
    def __repr__(self):
        return f"Season(name='{self.name}', teams={len(self.teams)}, matchday={self.current_matchday})"