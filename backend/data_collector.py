#   Collect data from nba_api
#   Link to API: https://github.com/swar/nba_api

from nba_api.stats.endpoints import leaguegamefinder, teamestimatedmetrics, scoreboardv2
from nba_api.stats.static import teams
import pandas as pd
from datetime import datetime

class NBADataCollector:
    #Constructor: fetch teams metadata from nba_api static stats
    def __init__(self):
        self.teams = teams.get_teams()
        self.teams_df = pd.DataFrame(self.teams)

    # Get upcoming games for today
    def get_upcoming_games(self):
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get scoreboard for today
        board = scoreboardv2.ScoreboardV2(game_date=today)
        games = board.game_header.get_data_frame()
        
        upcoming = []
        for _, game in games.iterrows():
            home_team_id = game['HOME_TEAM_ID']
            visitor_team_id = game['VISITOR_TEAM_ID']
            
            home_team = self.teams_df[self.teams_df['id'] == home_team_id]['full_name'].values[0]
            visitor_team = self.teams_df[self.teams_df['id'] == visitor_team_id]['full_name'].values[0]
            
            upcoming.append({
                'game_id': game['GAME_ID'],
                'date': today,
                'time': game['GAME_STATUS_TEXT'],
                'home_team': home_team,
                'home_team_id': int(home_team_id),
                'visitor_team': visitor_team,
                'visitor_team_id': int(visitor_team_id)
            })
            
        return upcoming

    # Collect game data for specific seasons
    def collect_game_data(self, seasons=["2022-23", "2023-24", "2024-25"]):
        all_games = []
        
        for season in seasons:
            print(f"Collecting data for {season} season... ")
            #Creates a LeagueGameFinder object that targets the specific regular season
            gamefinder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season,
                season_type_nullable="Regular Season"
            )
            season_games = gamefinder.get_data_frames()[0]
            season_games['SEASON_ID'] = season
            all_games.append(season_games)
            
        games = pd.concat(all_games, ignore_index=True)
        games['WIN'] = games['WL'].apply(lambda x: 1 if x == 'W' else 0) # New column: 1 if win else 0
        games['HOME'] = games['MATCHUP'].str.contains('vs.').astype(int) # If vs. that means it's home game, if it's @ that means it's away

        return games
    
    #Get team's stats aka Metadata
    def get_teams_stats(self, games_df):   
        team_stats = [] #Create empty list to store data

        #Loop through every team in dataset
        for team_id in games_df['TEAM_ID'].unique():
            team_games = games_df[games_df['TEAM_ID'] == team_id].sort_values('GAME_DATE') #Sort by date
            #Creates a 10 game average 
            team_games['AVG_PTS'] = round(team_games['PTS'].rolling(10, min_periods=1).mean().shift(1), 1)
            team_games['AVG_FG_PCT'] = round(team_games['FG_PCT'].rolling(10, min_periods=1).mean().shift(1), 3)
            team_games['AVG_FG3_PCT'] = round(team_games['FG3_PCT'].rolling(10, min_periods=1).mean().shift(1), 3)
            team_games['AVG_FT_PCT'] = round(team_games['FT_PCT'].rolling(10, min_periods=1).mean().shift(1), 3)
            team_games['AVG_REB'] = round(team_games['REB'].rolling(10, min_periods=1).mean().shift(1), 1)
            team_games['AVG_AST'] = round(team_games['AST'].rolling(10, min_periods=1).mean().shift(1), 1)
            team_games['AVG_STL'] = round(team_games['STL'].rolling(10, min_periods=1).mean().shift(1), 1)
            team_games['AVG_BLK'] = round(team_games['BLK'].rolling(10, min_periods=1).mean().shift(1), 1)
            team_games['AVG_TOV'] = round(team_games['TOV'].rolling(10, min_periods=1).mean().shift(1), 1)
            team_games['AVG_PLUS_MINUS'] = round(team_games['PLUS_MINUS'].rolling(10, min_periods=1).mean().shift(1), 1)

            team_stats.append(team_games)
        
        return pd.concat(team_stats) #Combines all team data into one data frame 

    #Save data into csv file
    def save_data(self, df, filename=None):
        import os
        if filename is None:
            # Get directory containing this script (backend/)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to project root
            project_root = os.path.dirname(current_dir)
            filename = os.path.join(project_root, 'nba_games.csv')
            
        df.to_csv(filename,index=False);
        print(f"Saved {len(df)} games to {filename}")
    
if __name__ == '__main__':
    collector = NBADataCollector()
    games = collector.collect_game_data()
    games_with_stats = collector.get_teams_stats(games)
    collector.save_data(games_with_stats)