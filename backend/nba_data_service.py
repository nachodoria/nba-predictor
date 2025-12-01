"""
NBA Data Service - Provides real-time NBA data for enhanced predictions
"""

from nba_api.stats.endpoints import leaguestandingsv3, teamgamelog, leaguegamefinder, teamdashboardbygeneralsplits, playergamelog, playercareerstats
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.static import teams, players
from datetime import datetime
import pandas as pd
from typing import Optional, Dict, List, Tuple
import difflib


def get_current_nba_season() -> str:
    """
    Determine current NBA season based on today's date.
    NBA seasons run from October to June.
    
    Returns:
        Season string like "2025-26"
    """
    now = datetime.now()
    year = now.year
    month = now.month
    
    # NBA season starts in October
    # If we're in Oct-Dec, season is YEAR-YEAR+1
    # If we're in Jan-Sep, season is YEAR-1-YEAR
    if month >= 10:  # October or later
        return f"{year}-{str(year + 1)[-2:]}"
    else:  # January to September
        return f"{year - 1}-{str(year)[-2:]}"


class NBADataService:
    def __init__(self):
        """Initialize the NBA data service with team metadata"""
        self.teams = teams.get_teams()
        self.team_name_map = {team['full_name'].lower(): team for team in self.teams}
        self.team_abbr_map = {team['abbreviation'].lower(): team for team in self.teams}
        
    def search_team_by_name(self, name: str) -> Optional[Dict]:
        """
        Fuzzy search for a team by name or abbreviation
        
        Args:
            name: Team name or abbreviation (e.g., "Lakers", "LAL", "Los Angeles Lakers")
            
        Returns:
            Team dict with id, full_name, abbreviation, etc. or None if not found
        """
        name_lower = name.lower().strip()
        
        # Direct match on abbreviation
        if name_lower in self.team_abbr_map:
            return self.team_abbr_map[name_lower]
        
        # Direct match on full name
        if name_lower in self.team_name_map:
            return self.team_name_map[name_lower]
        
        # Partial match on full name
        for team_name, team in self.team_name_map.items():
            if name_lower in team_name or team_name in name_lower:
                return team
        
        # Fuzzy match on full names
        team_names = list(self.team_name_map.keys())
        matches = difflib.get_close_matches(name_lower, team_names, n=1, cutoff=0.6)
        if matches:
            return self.team_name_map[matches[0]]
        
        return None
    
    def search_player_by_name(self, name: str) -> Optional[Dict]:
        """
        Fuzzy search for a player by name
        
        Args:
            name: Player name (e.g., "Scottie Barnes", "LeBron")
            
        Returns:
            Player dict with id, full_name, etc. or None if not found
        """
        name_lower = name.lower().strip()
        all_players = players.get_players()
        
        # Direct match on full name
        for player in all_players:
            if player['full_name'].lower() == name_lower:
                return player
        
        # Partial match on full name
        for player in all_players:
            if name_lower in player['full_name'].lower() or player['full_name'].lower() in name_lower:
                return player
        
        # Fuzzy match
        player_names = [p['full_name'].lower() for p in all_players]
        matches = difflib.get_close_matches(name_lower, player_names, n=1, cutoff=0.6)
        if matches:
            for player in all_players:
                if player['full_name'].lower() == matches[0]:
                    return player
        
        return None
    
    def get_player_season_stats(self, player_id: int, season: str = None) -> Dict:
        """
        Get current season statistics for a player
        
        Args:
            player_id: NBA player ID
            season: NBA season
            
        Returns:
            Dictionary with player statistics
        """
        if season is None:
            season = get_current_nba_season()
        
        try:
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            df = career.get_data_frames()[0]
            
            # Filter for the specific season
            season_stats = df[df['SEASON_ID'] == season]
            
            if season_stats.empty:
                return {}
            
            stats = season_stats.iloc[0].to_dict()
            
            # Return key stats
            return {
                'games_played': stats.get('GP', 0),
                'games_started': stats.get('GS', 0),
                'minutes': stats.get('MIN', 0),
                'points': stats.get('PTS', 0),
                'rebounds': stats.get('REB', 0),
                'assists': stats.get('AST', 0),
                'steals': stats.get('STL', 0),
                'blocks': stats.get('BLK', 0),
                'turnovers': stats.get('TOV', 0),
                'fg_pct': stats.get('FG_PCT', 0),
                'fg3_pct': stats.get('FG3_PCT', 0),
                'ft_pct': stats.get('FT_PCT', 0)
            }
        except Exception as e:
            print(f"Error fetching player stats for player {player_id}: {e}")
            return {}
    
    def get_player_recent_games(self, player_id: int, n: int = 10, season: str = None) -> pd.DataFrame:
        """
        Get the last N games for a specific player
        
        Args:
            player_id: NBA player ID
            n: Number of recent games to fetch
            season: NBA season
            
        Returns:
            DataFrame with recent game results
        """
        if season is None:
            season = get_current_nba_season()
        
        try:
            game_log = playergamelog.PlayerGameLog(
                player_id=player_id,
                season=season,
                season_type_all_star="Regular Season"
            )
            df = game_log.get_data_frames()[0]
            
            # Get most recent N games
            recent = df.head(n)
            
            # Select relevant columns
            columns = ['GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'PTS', 'REB', 'AST', 'FG_PCT']
            available_cols = [col for col in columns if col in recent.columns]
            
            return recent[available_cols] if available_cols else recent
        except Exception as e:
            print(f"Error fetching recent games for player {player_id}: {e}")
            return pd.DataFrame()
    
    def get_team_standings(self, season: str = None) -> pd.DataFrame:
        """
        Get current season standings for all teams
        
        Args:
            season: NBA season (e.g., "2025-26"). If None, uses current season
            
        Returns:
            DataFrame with team standings including wins, losses, win%, etc.
        """
        if season is None:
            season = get_current_nba_season()
        
        try:
            standings = leaguestandingsv3.LeagueStandingsV3(
                season=season,
                season_type="Regular Season"
            )
            df = standings.get_data_frames()[0]
            
            # Select relevant columns
            columns = ['TeamID', 'TeamCity', 'TeamName', 'Conference', 
                      'Record', 'HOME', 'ROAD', 'L10', 'strCurrentStreak']
            available_cols = [col for col in columns if col in df.columns]
            
            return df[available_cols] if available_cols else df
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return pd.DataFrame()
    
    def get_team_recent_games(self, team_id: int, n: int = 5, season: str = None) -> pd.DataFrame:
        """
        Get the last N games for a specific team
        
        Args:
            team_id: NBA team ID
            n: Number of recent games to fetch
            season: NBA season
            
        Returns:
            DataFrame with recent game results
        """
        if season is None:
            season = get_current_nba_season()
        
        try:
            game_log = teamgamelog.TeamGameLog(
                team_id=team_id,
                season=season,
                season_type_all_star="Regular Season"
            )
            df = game_log.get_data_frames()[0]
            
            # Get most recent N games
            recent = df.head(n)
            
            # Select relevant columns
            columns = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'OPP_PTS', 'FG_PCT', 'REB', 'AST']
            available_cols = [col for col in columns if col in recent.columns]
            
            return recent[available_cols] if available_cols else recent
        except Exception as e:
            print(f"Error fetching recent games for team {team_id}: {e}")
            return pd.DataFrame()
    
    def get_team_stats(self, team_id: int, season: str = None) -> Dict:
        """
        Get current season statistics for a team
        
        Args:
            team_id: NBA team ID
            season: NBA season
            
        Returns:
            Dictionary with team statistics
        """
        if season is None:
            season = get_current_nba_season()
        
        try:
            dashboard = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(
                team_id=team_id,
                season=season,
                season_type_all_star="Regular Season"
            )
            df = dashboard.get_data_frames()[0]
            
            if df.empty:
                return {}
            
            # Extract first row (overall stats)
            stats = df.iloc[0].to_dict()
            
            # Return key stats
            return {
                'games_played': stats.get('GP', 0),
                'wins': stats.get('W', 0),
                'losses': stats.get('L', 0),
                'win_pct': stats.get('W_PCT', 0),
                'avg_pts': stats.get('PTS', 0),
                'avg_fg_pct': stats.get('FG_PCT', 0),
                'avg_fg3_pct': stats.get('FG3_PCT', 0),
                'avg_reb': stats.get('REB', 0),
                'avg_ast': stats.get('AST', 0),
                'avg_stl': stats.get('STL', 0),
                'avg_blk': stats.get('BLK', 0),
                'avg_tov': stats.get('TOV', 0),
                'plus_minus': stats.get('PLUS_MINUS', 0),
                'streak': self._get_team_streak(team_id, season)
            }
        except Exception as e:
            print(f"Error fetching team stats for team {team_id}: {e}")
            return {}

    def _get_team_streak(self, team_id: int, season: str = None) -> str:
        """Helper to get just the streak for a team"""
        try:
            standings = self.get_team_standings(season)
            if not standings.empty:
                team_data = standings[standings['TeamID'] == team_id]
                if not team_data.empty:
                    return team_data.iloc[0]['strCurrentStreak']
            return "N/A"
        except:
            return "N/A"
    
    def get_matchup_history(self, team1_id: int, team2_id: int, n: int = 5, season: str = None) -> pd.DataFrame:
        """
        Get head-to-head matchup history between two teams
        
        Args:
            team1_id: First team ID
            team2_id: Second team ID
            n: Number of recent matchups to fetch
            season: NBA season
            
        Returns:
            DataFrame with matchup history
        """
        if season is None:
            season = get_current_nba_season()
        
        try:
            # Get games for team1
            gamefinder = leaguegamefinder.LeagueGameFinder(
                team_id_nullable=team1_id,
                season_nullable=season,
                season_type_nullable="Regular Season"
            )
            games = gamefinder.get_data_frames()[0]
            
            # Filter for games against team2
            matchups = games[games['TEAM_ID'] == team2_id]
            
            # Get most recent N matchups
            recent_matchups = matchups.head(n)
            
            columns = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'FG_PCT', 'REB', 'AST']
            available_cols = [col for col in columns if col in recent_matchups.columns]
            
            return recent_matchups[available_cols] if available_cols else recent_matchups
        except Exception as e:
            print(f"Error fetching matchup history: {e}")
            return pd.DataFrame()
    
    def get_todays_games(self) -> List[Dict]:
        """
        Get today's NBA games schedule
        
        Returns:
            List of game dictionaries with teams, time, and status
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            board = scoreboard.ScoreBoard()
            
            games = []
            if hasattr(board, 'games') and board.games:
                for game in board.games.get_dict():
                    games.append({
                        'game_id': game.get('gameId'),
                        'home_team': {
                            'id': game.get('homeTeam', {}).get('teamId'),
                            'name': game.get('homeTeam', {}).get('teamName'),
                            'city': game.get('homeTeam', {}).get('teamCity'),
                            'score': game.get('homeTeam', {}).get('score', 0)
                        },
                        'away_team': {
                            'id': game.get('awayTeam', {}).get('teamId'),
                            'name': game.get('awayTeam', {}).get('teamName'),
                            'city': game.get('awayTeam', {}).get('teamCity'),
                            'score': game.get('awayTeam', {}).get('score', 0)
                        },
                        'game_time': game.get('gameTimeUTC'),
                        'game_status': game.get('gameStatus'),
                        'game_status_text': game.get('gameStatusText')
                    })
            
            return games
        except Exception as e:
            print(f"Error fetching today's games: {e}")
            return []
    
    def find_team_game_today(self, team_id: int) -> Optional[Tuple[Dict, Dict]]:
        """
        Check if a team has a game today and return game details
        
        Args:
            team_id: NBA team ID
            
        Returns:
            Tuple of (game_info, opponent_info) or None if no game today
        """
        todays_games = self.get_todays_games()
        
        for game in todays_games:
            if game['home_team']['id'] == team_id:
                return (game, game['away_team'])
            elif game['away_team']['id'] == team_id:
                return (game, game['home_team'])
        
        return None
    
    def format_todays_games_for_prompt(self, games: List[Dict] = None) -> str:
        """
        Format today's games for Gemini prompt
        
        Args:
            games: List of game dicts (if None, fetches today's games)
            
        Returns:
            Formatted string with today's games
        """
        if games is None:
            games = self.get_todays_games()
        
        if not games:
            return "No NBA games scheduled for today."
        
        output = f"\nToday's NBA Games ({len(games)} games):\n"
        for game in games:
            away = f"{game['away_team']['city']} {game['away_team']['name']}"
            home = f"{game['home_team']['city']} {game['home_team']['name']}"
            status = game.get('game_status_text', 'Scheduled')
            output += f"- {away} @ {home} ({status})\n"
        
        return output
    
    def format_standings_for_prompt(self, standings_df: pd.DataFrame, team_names: List[str] = None) -> str:
        """
        Format standings data for inclusion in Gemini prompt
        
        Args:
            standings_df: Standings DataFrame
            team_names: Optional list of team names to filter for
            
        Returns:
            Formatted string with standings info
        """
        if standings_df.empty:
            return "Standings data not available."
        
        # Filter for specific teams if provided
        if team_names:
            filtered = standings_df[standings_df['TeamName'].isin(team_names)]
            if not filtered.empty:
                standings_df = filtered
        
        output = "Current NBA Standings:\n"
        for _, row in standings_df.iterrows():
            team = f"{row.get('TeamCity', '')} {row.get('TeamName', '')}".strip()
            record = row.get('Record', 'N/A')
            streak = row.get('strCurrentStreak', 'N/A')
            l10 = row.get('L10', 'N/A')
            output += f"- {team}: {record} (Last 10: {l10}, Streak: {streak})\n"
        
        return output
    
    def format_recent_games_for_prompt(self, games_df: pd.DataFrame, team_name: str) -> str:
        """
        Format recent games for inclusion in Gemini prompt
        
        Args:
            games_df: Recent games DataFrame
            team_name: Name of the team
            
        Returns:
            Formatted string with recent games
        """
        if games_df.empty:
            return f"Recent games for {team_name} not available."
        
        output = f"\n{team_name} Recent Games:\n"
        for _, game in games_df.iterrows():
            date = game.get('GAME_DATE', 'N/A')
            matchup = game.get('MATCHUP', 'N/A')
            result = game.get('WL', 'N/A')
            pts = game.get('PTS', 'N/A')
            opp_pts = game.get('OPP_PTS', 'N/A')
            output += f"- {date}: {matchup} ({result}) {pts}-{opp_pts}\n"
        
        return output
    
    def format_team_stats_for_prompt(self, stats: Dict, team_name: str) -> str:
        """
        Format team stats for inclusion in Gemini prompt
        
        Args:
            stats: Team statistics dictionary
            team_name: Name of the team
            
        Returns:
            Formatted string with team stats
        """
        if not stats:
            return f"Statistics for {team_name} not available."
        
        output = f"\n{team_name} Season Averages:\n"
        output += f"- Record: {stats.get('wins', 0)}-{stats.get('losses', 0)} ({stats.get('win_pct', 0):.1%})\n"
        output += f"- Points: {stats.get('avg_pts', 0):.1f} PPG\n"
        output += f"- FG%: {stats.get('avg_fg_pct', 0):.1%}\n"
        output += f"- 3P%: {stats.get('avg_fg3_pct', 0):.1%}\n"
        output += f"- Rebounds: {stats.get('avg_reb', 0):.1f} RPG\n"
        output += f"- Assists: {stats.get('avg_ast', 0):.1f} APG\n"
        output += f"- Steals: {stats.get('avg_stl', 0):.1f} SPG\n"
        output += f"- Blocks: {stats.get('avg_blk', 0):.1f} BPG\n"
        output += f"- Current Streak: {stats.get('streak', 'N/A')}\n"
        
        return output
    
    def format_player_stats_for_prompt(self, stats: Dict, player_name: str) -> str:
        """
        Format player stats for inclusion in Gemini prompt
        
        Args:
            stats: Player statistics dictionary
            player_name: Name of the player
            
        Returns:
            Formatted string with player stats
        """
        if not stats:
            return f"Statistics for {player_name} not available."
        
        gp = stats.get('games_played', 0)
        if gp == 0:
            return f"{player_name} has not played this season yet."
        
        output = f"\n{player_name} Season Averages:\n"
        output += f"- Games Played: {gp}\n"
        output += f"- Points: {stats.get('points', 0) / gp:.1f} PPG\n"
        output += f"- Rebounds: {stats.get('rebounds', 0) / gp:.1f} RPG\n"
        output += f"- Assists: {stats.get('assists', 0) / gp:.1f} APG\n"
        output += f"- FG%: {stats.get('fg_pct', 0):.1%}\n"
        output += f"- 3P%: {stats.get('fg3_pct', 0):.1%}\n"
        output += f"- FT%: {stats.get('ft_pct', 0):.1%}\n"
        output += f"- Steals: {stats.get('steals', 0) / gp:.1f} SPG\n"
        output += f"- Blocks: {stats.get('blocks', 0) / gp:.1f} BPG\n"
        
        return output
    
    def format_player_recent_games_for_prompt(self, games_df: pd.DataFrame, player_name: str) -> str:
        """
        Format player recent games for inclusion in Gemini prompt
        
        Args:
            games_df: Recent games DataFrame
            player_name: Name of the player
            
        Returns:
            Formatted string with recent games
        """
        if games_df.empty:
            return f"Recent games for {player_name} not available."
        
        output = f"\n{player_name} Recent Games:\n"
        for _, game in games_df.iterrows():
            date = game.get('GAME_DATE', 'N/A')
            matchup = game.get('MATCHUP', 'N/A')
            result = game.get('WL', 'N/A')
            pts = game.get('PTS', 'N/A')
            reb = game.get('REB', 'N/A')
            ast = game.get('AST', 'N/A')
            output += f"- {date}: {matchup} ({result}) {pts} PTS, {reb} REB, {ast} AST\n"
        
        return output


if __name__ == '__main__':
    # Test the service
    service = NBADataService()
    
    # Test team search
    print("Testing team search...")
    lakers = service.search_team_by_name("Lakers")
    print(f"Found: {lakers['full_name']} (ID: {lakers['id']})")
    
    # Test standings
    print("\nTesting standings...")
    standings = service.get_team_standings()
    print(f"Fetched standings for {len(standings)} teams")
    
    # Test team stats
    if lakers:
        print(f"\nTesting team stats for {lakers['full_name']}...")
        stats = service.get_team_stats(lakers['id'])
        print(service.format_team_stats_for_prompt(stats, lakers['full_name']))
