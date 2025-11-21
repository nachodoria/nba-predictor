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
    