from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import pandas as pd
import matplotlib.pyplot as plt

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

player_name = input("Enter player name: ")
player_id = get_player_id(player_name)

if player_id:
    print(f"Found player ID: {player_id}")
    career = playercareerstats.PlayerCareerStats(player_id=str(player_id))
    df = career.season_totals_regular_season.get_data_frame()
    print(df[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'REB', 'AST']])
else:
    print(f"Player '{player_name}' not found.")