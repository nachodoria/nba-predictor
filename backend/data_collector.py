#   Collect data from nba_api
#   Link to API: https://github.com/swar/nba_api

from nba_api.stats.endpoints import leaguegamefinder, teamestimatedmetrics
from nba_api.stats.static import teams
import pandas as pd
from datetime import datetime


def get_current_nba_season() -> str:
    """Determine current NBA season based on today's date."""
    now = datetime.now()
    year = now.year
    month = now.month
    if month >= 10:  # October or later
        return f"{year}-{str(year + 1)[-2:]}"
    else:  # January to September
        return f"{year - 1}-{str(year)[-2:]}"


class NBADataCollector:
    #Constructor: fetch teams metadata from nba_api static stats
    def __init__(self):
        self.teams = teams.get_teams()

    # Collect game data for a specific season, defaults to current season
    def collect_game_data(self, season=None):
        if season is None:
            season = get_current_nba_season()
        
        print(f"Collecting data for {season} season... ")

        #Creates a LeagueGameFinder object that targets the specified regular season
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
            team_games['AVG_PTS'] = round(team_games['PTS'].rolling(10, min_periods=1).mean().shift(1), 1)
            team_games['AVG_FG_PCT'] = round(team_games['FG_PCT'].rolling(10, min_periods=1).mean().shift(1), 1)
            team_games['AVG_REB'] = round(team_games['REB'].rolling(10, min_periods=1).mean().shift(1), 1)
            team_games['AVG_AST'] = round(team_games['AST'].rolling(10, min_periods=1).mean().shift(1), 1)

            team_stats.append(team_games)
        
        return pd.concat(team_stats) #Combines all team data into one data frame 

    #Save data into csv file
    def save_data(self, df, filename="../nba_games.csv"):
        df.to_csv(filename,index=False);
        print(f"Saved {len(df)} games to {filename}")
    
if __name__ == '__main__':
    collector = NBADataCollector()
    games = collector.collect_game_data()
    games_with_stats = collector.get_teams_stats(games)
    collector.save_data(games_with_stats)

    