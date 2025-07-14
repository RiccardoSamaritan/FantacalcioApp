import sys
import time
from pathlib import Path
from src.loader import setup_complete_teams
from src.season import Season

def print_banner():
    """
    Print the welcome banner for the Fantacalcio Season Simulator.
    """
    print("=" * 60)
    print("FANTACALCIO SEASON SIMULATOR")
    print("=" * 60)
    print()

def print_loading_message(message: str, delay: float = 0.5):
    """
    Print a loading message with a delay to simulate processing.
    """
    print(f"{message}...")
    time.sleep(delay)

def main():
    
    print_banner()
    
    try:
        teams_file = "test_teams.json"
        data_dir = "data"
        season_name = "Serie A Fantacalcio 2024/25"
        
        if not Path(teams_file).exists():
            print(f"Error: {teams_file} not found!")
            sys.exit(1)
        
        if not Path(data_dir).exists():
            print(f"Error: directory {data_dir} not found!")
            sys.exit(1)
        
        print_loading_message("Loading teams configuration", 1)
        print_loading_message("Reading players data from file", 2)
        print_loading_message("Calculating statistics and fantavoti", 1)
        
        teams = setup_complete_teams(teams_file, data_dir)
        
        print(f"Successfully loaded {len(teams)} teams")
        
        print("\n LOADED TEAMS:")
        for i, team in enumerate(teams, 1):
            stats = team.get_team_stats()
            composition_status = "✅" if stats['valid_composition'] else "❌"
            print(f"  {i:2d}. {team.name:<20} {composition_status} "
                  f"({stats['goalkeepers']}P-{stats['defenders']}D-"
                  f"{stats['midfielders']}C-{stats['forwards']}A)")
        
        invalid_teams = [t for t in teams if not t.validate_team_composition()]
        if invalid_teams:
            print(f"\n Attention: {len(invalid_teams)} teams don't have a valid composition!")
            for team in invalid_teams:
                print(f"   - {team.name}")

        print_loading_message("\nInitializing season", 1)
        
        season = Season(teams, season_name)
        
        print(f"Season created with {len(season.teams)} teams")
        
        print(f"\nReady to simulate {season_name}!")
        
        user_input = input("\nDo you want to proceed with the simulation? (y/N): ").strip().lower()
        if user_input not in ['y', 'yes']:
            print("Simulation annulled.")
            sys.exit(0)
        
        print("\n" + "=" * 60)
        print("🚀 AVVIO SIMULAZIONE STAGIONE")
        print("=" * 60)
        
        start_time = time.time()
        season_summary = season.process_complete_season()
        end_time = time.time()
        
        print("\n" + "=" * 60)
        print("THE SEASON IT'S OVER!")
        print("=" * 60)
        
        print(f"Processing time: {end_time - start_time:.2f} seconds")
        print(f"Processed matchdays: {season_summary['total_matchdays_processed'] // len(teams)}")
        print(f"Average score per matchday: {season_summary['average_score_per_matchday']}")
        
        print(season.get_formatted_table())
        
        champion = season_summary['champion']
        final_table = season_summary['final_table']
        print(f"\nCHAMPION: {champion} ({season_summary['champion_points']} points)")
        print(f"2nd: {final_table[1]['team']} ({final_table[1]['total_points']} points)")
        print(f"3rd: {final_table[2]['team']} ({final_table[2]['total_points']} points)")
        
        print(f"\nSEASON STATISTICS:")
        print(f"   Highest single score: {season_summary['highest_single_score']} ({season_summary['highest_score_team']})")
        print(f"   Most consistent team: {season_summary['most_consistent_team']}")
        
        save_results = input("\nDo you want to save detailed results on file ? (y/N): ").strip().lower()
        if save_results in ['y', 'yes', 'si', 's']:
            save_season_results(season, season_summary)
        
        show_progression = input("\nDo you want to visualize single team's progression? (y/N): ").strip().lower()
        if show_progression in ['y', 'yes', 'si', 's']:
            show_team_progression(season)
        
        print(f"\n Thank your for using Fantacalcio Season Simulator!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"FIle error: {e}")
        print("Be sure that every needed file exists.")
        sys.exit(1)
    
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    

    
    except Exception as e:
        print(f"❌ Errore imprevisto: {e}")
        print("Controlla i file di dati e riprova.")
        sys.exit(1)

def save_season_results(season: Season, summary: dict):
    """
    Save the season results to a text file.
    """
    try:
        filename = f"season_results_{int(time.time())}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"FANTACALCIO SEASON RESULTS\n")
            f.write(f"Season: {summary['season_name']}\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("FINAL LEADERBOARD\n")
            f.write("=" * 80 + "\n")
            f.write(season.get_formatted_table())
            f.write("\n\n")
            
            f.write("SEASON STATISTICS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Champion: {summary['champion']} ({summary['champion_points']} points)\n")
            f.write(f"Partecipating teams: {summary['teams']}\n")
            f.write(f"Processed matchdays: {summary['total_matchdays_processed'] // summary['teams']}\n")
            f.write(f"Average score per matchday: {summary['average_score_per_matchday']}\n")
            f.write(f"Highest single score: {summary['highest_single_score']} ({summary['highest_score_team']})\n")
            f.write(f"Most consistent team: {summary['most_consistent_team']}\n")
            f.write("\n\n")
            
            f.write("SCORES PER MATCHDAY\n")
            f.write("=" * 80 + "\n")
            for matchday in range(1, 39):
                f.write(season.get_matchday_scores(matchday))
                f.write("\n")
            
            f.write("\nTEAMS PROGRESSION\n")
            f.write("=" * 80 + "\n")
            for team_name in [t.name for t in season.teams]:
                progression = season.get_team_progression(team_name)
                f.write(f"\n{team_name}:\n")
                f.write("Matchday | Score | Cumulative Score\n")
                f.write("-" * 35 + "\n")
                for match in progression['progression']:
                    f.write(f"   {match['matchday']:2d}    |   {match['score']:6.1f}  |   {match['cumulative_points']:8.1f}\n")
        
        print(f"Results saved to {filename}")
        
    except Exception as e:
        print(f"Failed to save the file: {e}")

def show_team_progression(season: Season):
    """
    Show the progression of a single team.
    """
    try:
        print("\nTeams available:")
        for i, team in enumerate(season.teams, 1):
            print(f"  {i}. {team.name}")
        
        choice = input("\nChoose the number of the team (or 0 to skip): ").strip()
        
        if choice == "0":
            return
        
        team_index = int(choice) - 1
        if 0 <= team_index < len(season.teams):
            team_name = season.teams[team_index].name
            progression = season.get_team_progression(team_name)
            
            print(f"\n=== Progression {team_name} ===")
            print("Matchday | Score | Cumulative Score")
            print("-" * 35)
            
            recent_matches = progression['progression'][-10:]
            for match in recent_matches:
                print(f"   {match['matchday']:2d}    |   {match['score']:6.1f}  |   {match['cumulative_points']:8.1f}")
            
            print(f"\nFinal score: {progression['final_total']} points")
        else:
            print("Unvalid choice.")
    
    except (ValueError, IndexError):
        print("Unvalid choice.")

if __name__ == "__main__":
    main()