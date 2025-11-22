#   Collect data from nba_api
#   Link to API: https://github.com/swar/nba_api

from nba_api.stats.endpoints import leaguegamefinder, teamestimatedmetrics
from nba_api.stats.static import teams
import pandas as pd
from datetime import datetime


class NBADataCollector:
    #Constructor: fetch teams metadata from nba_api static stats
    def __init__(self):
        self.teams = teams.get_teams()

    # Collect game data for a specific season, default is set to 2024-25 season
    def collect_game_data(self, season="2024-25"):
        print(f"Collecting data for {season} season... ")

        #Creates a LeagueGameFinder object that targets 2024-25 regular season
        gamefinder = leaguegamefinder.LeagueGameFinder(
            season_nullable=season,
            season_type_nullable="Regular Season"
        )
        
        
        games = gamefinder.get_data_frames()[0] #Turns into a panda dataframe and [0] gets the game data
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
            team_games['AVG_PTS'] = round(team_games['PTS'].rolling(10, min_periods=1).mean(), 1)
            team_games['AVG_FG_PCT'] = round(team_games['FG_PCT'].rolling(10, min_periods=1).mean(), 1)
            team_games['AVG_REB'] = round(team_games['REB'].rolling(10, min_periods=1).mean(), 1)
            team_games['AVG_AST'] = round(team_games['AST'].rolling(10, min_periods=1).mean(), 1)

            team_stats.append(team_games)
        
        return pd.concat(team_stats) #Combines all team data into one data frame 

    #Save data into csv file
    def save_data(self, df, filename="../nba-predictor/nba_games.csv"):
        df.to_csv(filename,index=False);
        print(f"Saved {len(df)} games to {filename}")
    
if __name__ == '__main__':
    collector = NBADataCollector()
    games = collector.collect_game_data()
    games_with_stats = collector.get_teams_stats(games)
    collector.save_data(games_with_stats)

    