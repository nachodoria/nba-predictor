#   Collect data from nba_api
#   Link to API: https://github.com/swar/nba_api

from nba_api.stats.endpoints import leaguegamefinder, teamestimatedmetrics
from nba_api.stats.static import teams
import pandas as pd
from datetime import datetime


class NBADataCollector:
    def __init__(self):
        self.teams = teams.get_teams()
