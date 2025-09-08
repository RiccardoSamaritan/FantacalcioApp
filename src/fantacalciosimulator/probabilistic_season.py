from typing import List, Dict, Tuple
from .team import Team

class ProbabilisticSeasonTable:
    """
    Class to manage the probabilistic season table for a team.
    """
    
    def __init__(self, team: Team):
        self.team = team
        self.total_points = 0.0  
        self.matchday_scores: Dict[int, float] = {}  # actual fantasy scores
        self.matchday_league_points: Dict[int, float] = {}  # probabilistic league points
        self.matchdays_played = 0
        self.wins = 0.0
        self.draws = 0.0
        self.losses = 0.0
    
    def add_matchday_data(self, matchday: int, fantasy_score: float, league_points: float):
        """
        Add data for a specific matchday.
        
        Args:
            matchday: The matchday number
            fantasy_score: Actual fantasy score for the matchday
            league_points: Probabilistic league points earned
        """
        if matchday not in self.matchday_scores:
            self.matchdays_played += 1
        
        self.matchday_scores[matchday] = fantasy_score
        self.matchday_league_points[matchday] = league_points
        self.total_points = sum(self.matchday_league_points.values())
    
    def get_stats(self) -> Dict:
        """
        Get team statistics.
        """
        avg_fantasy_score = sum(self.matchday_scores.values()) / max(self.matchdays_played, 1)
        avg_league_points = self.total_points / max(self.matchdays_played, 1)
        
        return {
            'team': self.team.name,
            'total_league_points': round(self.total_points, 2),
            'matchdays_played': self.matchdays_played,
            'average_fantasy_score': round(avg_fantasy_score, 1),
            'average_league_points': round(avg_league_points, 2),
            'best_fantasy_score': max(self.matchday_scores.values()) if self.matchday_scores else 0.0,
            'worst_fantasy_score': min(self.matchday_scores.values()) if self.matchday_scores else 0.0
        }


class ProbabilisticSeason:
    """
    Class to manage a probabilistic Fantacalcio season where each team plays
    against all possible opponents for each matchday and earns points based
    on win probability.
    """
    
    def __init__(self, teams: List[Team], name: str = "Probabilistic Fantacalcio Season", defense_modifier: bool = True):
        self.name = name
        self.teams = teams
        self.defense_modifier = defense_modifier
        self.table: Dict[str, ProbabilisticSeasonTable] = {}
        self.current_matchday = 1
        self.season_completed = False
        
        # Goal thresholds (traditional fantasy football)
        self.goal_thresholds = [66, 72, 78, 84, 90, 96, 102, 108, 114, 120]
        
        for team in teams:
            self.table[team.name] = ProbabilisticSeasonTable(team)
    
    def calculate_goals(self, score: float) -> int:
        """
        Calculate number of goals based on fantasy score using traditional thresholds.
        
        Args:
            score: Fantasy score
            
        Returns:
            Number of goals scored
        """
        goals = 0
        for threshold in self.goal_thresholds:
            if score >= threshold:
                goals += 1
            else:
                break
        return goals
    
    def determine_match_result(self, team_a_score: float, team_b_score: float) -> Tuple[str, int, int]:
        """
        Determine match result based on goal scoring system.
        
        Args:
            team_a_score: Fantasy score of team A
            team_b_score: Fantasy score of team B
            
        Returns:
            Tuple of (result, goals_a, goals_b) where result is 'win', 'draw', or 'loss' for team A
        """
        goals_a = self.calculate_goals(team_a_score)
        goals_b = self.calculate_goals(team_b_score)
        
        if goals_a > goals_b:
            return 'win', goals_a, goals_b
        elif goals_a < goals_b:
            return 'loss', goals_a, goals_b
        else:
            return 'draw', goals_a, goals_b
    
    def process_matchday(self, matchday: int) -> Dict[str, Dict]:
        """
        Process a matchday by calculating all possible pairings and determining
        probabilistic points for each team.
        
        Args:
            matchday: Matchday number (1-38)
            
        Returns:
            Dictionary with team results for this matchday
        """
        if matchday > 38 or matchday < 1:
            raise ValueError("Matchday must be between 1 and 38")
        
        team_scores = {}
        for team in self.teams:
            score = team.calculate_total_score(matchday, self.defense_modifier)
            team_scores[team.name] = score
        
        matchday_results = {}
        
        for team in self.teams:
            team_name = team.name
            team_score = team_scores[team_name]
            
            wins = 0
            draws = 0
            losses = 0
            total_matches = 0
            
            for opponent in self.teams:
                if opponent.name == team_name:
                    continue
                
                opponent_score = team_scores[opponent.name]
                result, _, _ = self.determine_match_result(team_score, opponent_score)
                
                if result == 'win':
                    wins += 1
                elif result == 'draw':
                    draws += 1
                else:
                    losses += 1
                
                total_matches += 1
            
            # Calculate probabilistic league points
            win_rate = wins / total_matches if total_matches > 0 else 0
            draw_rate = draws / total_matches if total_matches > 0 else 0
            loss_rate = losses / total_matches if total_matches > 0 else 0
            
            league_points = (wins * 3.0 + draws * 1.0) / total_matches
            
            matchday_results[team_name] = {
                'fantasy_score': team_score,
                'league_points': league_points,
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'win_rate': win_rate,
                'draw_rate': draw_rate,
                'loss_rate': loss_rate,
                'total_matches': total_matches
            }
            
            self.table[team_name].add_matchday_data(matchday, team_score, league_points)
        
        if matchday == self.current_matchday:
            self.current_matchday += 1
        
        return matchday_results
    
    def process_complete_season(self) -> Dict:
        """
        Process the entire season, calculating probabilistic results for all matchdays.
        
        Returns:
            Dictionary with season summary including final table and statistics
        """
        print(f"Starting probabilistic processing of {self.name}...")
        
        for matchday in range(1, 39):
            print(f"Processing matchday {matchday}...")
            self.process_matchday(matchday)
        
        self.season_completed = True
        print("Probabilistic season completed!")
        
        return self.get_season_summary()
    
    def get_season_table(self) -> List[Dict]:
        """
        Get the current probabilistic season table with team statistics.
        
        Returns:
            List of dictionaries with team statistics sorted by total league points.
        """
        table_data = [entry.get_stats() for entry in self.table.values()]
        
        table_data.sort(key=lambda x: x['total_league_points'], reverse=True)
        
        for i, team_data in enumerate(table_data):
            team_data['position'] = i + 1
        
        return table_data
    
    def get_formatted_table(self) -> str:
        """
        Get a formatted string representation of the probabilistic season table.
        """
        table = self.get_season_table()
        
        output = f"\n=== {self.name} - Final Leaderboard ===\n"
        output += "Pos | Team              | Matchdays | League Pts | Avg League | Avg Fantasy | Best Fantasy\n"
        output += "-" * 95 + "\n"
        
        for team_data in table:
            output += f"{team_data['position']:2d}  | "
            output += f"{team_data['team']:<17} | "
            output += f"{team_data['matchdays_played']:8d} | "
            output += f"{team_data['total_league_points']:9.2f} | "
            output += f"{team_data['average_league_points']:9.2f} | "
            output += f"{team_data['average_fantasy_score']:10.1f} | "
            output += f"{team_data['best_fantasy_score']:11.1f}\n"
        
        return output
    
    def get_matchday_details(self, matchday: int) -> str:
        """
        Get detailed results for a specific matchday.
        """
        if matchday < 1 or matchday > 38:
            return f"Invalid matchday: {matchday}"
        
        if matchday >= self.current_matchday:
            return f"Matchday {matchday} not yet processed"
        
        results = []
        for team_name, season_table in self.table.items():
            if matchday in season_table.matchday_league_points:
                fantasy_score = season_table.matchday_scores[matchday]
                league_points = season_table.matchday_league_points[matchday]
                results.append((team_name, fantasy_score, league_points))
        
        if not results:
            return f"No results available for matchday {matchday}"
        
        results.sort(key=lambda x: x[2], reverse=True)  # Sort by league points
        
        output = f"\n=== Probabilistic Results for Matchday {matchday} ===\n"
        output += "Pos | Team              | Fantasy Score | League Points | Win Rate\n"
        output += "-" * 70 + "\n"
        
        for i, (team_name, fantasy_score, league_points) in enumerate(results, 1):
            win_rate = (league_points / 3.0) if league_points > 0 else 0.0
            output += f"{i:2d}  | {team_name:<17} | {fantasy_score:11.1f} | {league_points:11.2f} | {win_rate:7.1%}\n"
        
        return output
    
    def get_season_summary(self) -> Dict:
        """
        Get a summary of the probabilistic season including final table and statistics.
        """
        final_table = self.get_season_table()
        
        all_fantasy_scores = []
        all_league_points = []
        for season_table in self.table.values():
            all_fantasy_scores.extend(season_table.matchday_scores.values())
            all_league_points.extend(season_table.matchday_league_points.values())
        
        total_matchdays = sum(st.matchdays_played for st in self.table.values())
        
        highest_fantasy_team = max(final_table, key=lambda x: x['best_fantasy_score'])
        most_consistent_team = min(final_table, key=lambda x: x['best_fantasy_score'] - x['worst_fantasy_score'])
        
        return {
            'season_name': self.name,
            'season_type': 'Probabilistic',
            'teams': len(self.teams),
            'total_matchdays_processed': total_matchdays,
            'average_fantasy_score': round(sum(all_fantasy_scores) / len(all_fantasy_scores), 1) if all_fantasy_scores else 0,
            'average_league_points': round(sum(all_league_points) / len(all_league_points), 2) if all_league_points else 0,
            'final_table': final_table,
            'champion': final_table[0]['team'] if final_table else None,
            'champion_points': final_table[0]['total_league_points'] if final_table else 0,
            'highest_fantasy_score': highest_fantasy_team['best_fantasy_score'],
            'highest_fantasy_team': highest_fantasy_team['team'],
            'most_consistent_team': most_consistent_team['team'],
            'season_completed': self.season_completed
        }
    
    def get_team_progression(self, team_name: str) -> Dict:
        """
        Get the progression of a specific team throughout the probabilistic season.
        """
        if team_name not in self.table:
            return {}
        
        season_table = self.table[team_name]
        progression = []
        cumulative_points = 0
        
        for matchday in range(1, 39):
            if matchday in season_table.matchday_league_points:
                fantasy_score = season_table.matchday_scores[matchday]
                league_points = season_table.matchday_league_points[matchday]
                cumulative_points += league_points
                progression.append({
                    'matchday': matchday,
                    'fantasy_score': fantasy_score,
                    'league_points': league_points,
                    'cumulative_points': round(cumulative_points, 2)
                })
        
        return {
            'team': team_name,
            'progression': progression,
            'final_total': cumulative_points
        }
    
    def __str__(self):
        return f"{self.name} ({len(self.teams)} teams, Matchday {self.current_matchday})"
    
    def __repr__(self):
        return f"ProbabilisticSeason(name='{self.name}', teams={len(self.teams)}, matchday={self.current_matchday})"