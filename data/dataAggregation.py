from nba_api.stats.endpoints import playercareerstats, teamgamelog, leaguegamefinder
from nba_api.stats.static import players, teams
import pandas as pd
import json
from datetime import datetime

class NBADataCollector:
    """Collect NBA data for AI training"""
    
    def __init__(self):
        self.all_players = players.get_players()
        self.all_teams = teams.get_teams()

    def get_player_id(player_name):
        nba_players = players.get_players()

        # Finding player by full name
        player = [p for p in nba_players if p['full_name'].lower() == player_name.lower()]

        if player:
            return player[0]['id']
        else:
            partial = [p for p in nba_players if player_name.lower() in p['full_name'].lower()]
            if partial:
                print(f"Did you mean one of these? {[p['full_name'] for p in partial]}")
            return None
        
    def collect_player_career_data(self, limit=100):
        """Collect career stats for multiple players"""
        data = []
        for i, player in enumerate(self.all_players[:limit]):
            try:
                career = playercareerstats.PlayerCareerStats(player_id=str(player['id']), timeout = 60)
                df = career.season_totals_regular_season.get_data_frame()
                df['PLAYER_NAME'] = player['full_name']
                data.append(df)
                print(f"Collected data for {player['full_name']} ({i+1}/{limit})")
            except Exception as e:
                print(f"Error with {player['full_name']}: {e}")
        
        return pd.concat(data, ignore_index=True)
    
    def prepare_training_data(self, df):
        """Convert to format suitable for ML training"""
        # Example: Predict next season points based on previous seasons
        training_examples = []
        
        for player in df['PLAYER_NAME'].unique():
            player_data = df[df['PLAYER_NAME'] == player].sort_values('SEASON_ID')
            
            for i in range(len(player_data) - 1):
                current = player_data.iloc[i]
                next_season = player_data.iloc[i + 1]
                
                training_examples.append({
                    'player': player,
                    'season': current['SEASON_ID'],
                    'games_played': current['GP'],
                    'points': current['PTS'],
                    'rebounds': current['REB'],
                    'assists': current['AST'],
                    'fg_pct': current['FG_PCT'],
                    'target_next_points': next_season['PTS']  # What we want to predict
                })
        
        return pd.DataFrame(training_examples)

# Collect data
collector = NBADataCollector()
print("Collecting player data...")
raw_data = collector.collect_player_career_data(limit=10)  # Start small
raw_data.to_csv('nba_raw_data.csv', index=False)

print("Preparing training data...")
training_data = collector.prepare_training_data(raw_data)
training_data.to_csv('nba_training_data.csv', index=False)
print(f"Training data shape: {training_data.shape}")