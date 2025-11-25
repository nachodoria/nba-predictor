from flask import Flask, request, jsonify
from flask_cors import CORS
from model import NBAPredictor
from data_collector import NBADataCollector
from nba_data_service import NBADataService
import os
from dotenv import load_dotenv
import google.generativeai as genai
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize predictor and data service
predictor = NBAPredictor()
nba_data_service = NBADataService()

# Configure Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro-latest')
    print("Gemini API configured successfully")
else:
    print("Warning: GOOGLE_API_KEY not found in environment variables")
    gemini_model = None

# Load model if it exists
try:
    predictor.load_model()
    print("Model loaded successfully") 
except FileNotFoundError:
    print("No trained model found. Please train the model first.")

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat queries with Gemini AI and NBA predictions"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        # Use Gemini to generate response
        if gemini_model:
            response = generate_gemini_response(query)
        else:
            response = process_query_fallback(query)
        
        return jsonify({
            'success': True,
            'query': query,
            'response': response
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def extract_player_names_from_query(query):
    """Extract potential player names from query (simple heuristic)"""
    # Common player names to look for
    common_players = [
        'scottie barnes', 'lebron james', 'giannis', 'luka doncic', 'stephen curry',
        'kevin durant', 'nikola jokic', 'joel embiid', 'jayson tatum', 'donovan mitchell',
        'anthony edwards', 'shai gilgeous-alexander', 'devin booker', 'damian lillard',
        'kawhi leonard', 'paul george', 'jimmy butler', 'bam adebayo', 'tyrese haliburton',
        'ja morant', 'zion williamson', 'trae young', 'deandre ayton', 'pascal siakam'
    ]
    
    query_lower = query.lower()
    found_players = []
    
    for player in common_players:
        if player in query_lower:
            found_players.append(player)
    
    # Also check for first/last name patterns (2-3 consecutive capitalized words)
    import re
    # Match patterns like "Scottie Barnes" or "LeBron James"
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
    matches = re.findall(name_pattern, query)
    for match in matches:
        if match.lower() not in [p.lower() for p in found_players]:
            found_players.append(match)
    
    return found_players[:2]  # Limit to 2 players

import json

def analyze_query_with_ai(query):
    """Analyze user query intent using Gemini"""
    try:
        prompt = f"""Analyze this NBA user query and return a strict JSON object (no markdown formatting).
        
        Query: "{query}"
        
        Return JSON with this structure:
        {{
            "intent": "schedule" | "prediction" | "stats" | "standings" | "general",
            "teams": ["Team A", "Team B"],
            "players": ["Player Name"],
            "is_temporal": boolean (true if asking about time/schedule/upcoming)
        }}
        
        Examples:
        "Lakers vs Warriors prediction" -> {{"intent": "prediction", "teams": ["Lakers", "Warriors"], "players": [], "is_temporal": false}}
        "Who plays tonight?" -> {{"intent": "schedule", "teams": [], "players": [], "is_temporal": true}}
        "LeBron stats" -> {{"intent": "stats", "teams": [], "players": ["LeBron James"], "is_temporal": false}}
        """
        
        response = gemini_model.generate_content(prompt)
        text = response.text.strip()
        # Clean up any markdown code blocks if present
        if text.startswith('```json'):
            text = text[7:-3]
        elif text.startswith('```'):
            text = text[3:-3]
            
        return json.loads(text)
    except Exception as e:
        print(f"Error analyzing query: {e}")
        # Fallback to basic extraction
        return {
            "intent": "general",
            "teams": extract_teams_from_query(query),
            "players": extract_player_names_from_query(query),
            "is_temporal": any(word in query.lower() for word in ['tonight', 'today', 'upcoming', 'schedule', 'games'])
        }

def generate_gemini_response(query): 
    """Generate response using Gemini AI with real-time NBA data and ML predictions"""
    try:
        # 1. Analyze intent with AI
        analysis = analyze_query_with_ai(query)
        
        team_names = analysis.get('teams', [])
        player_names = analysis.get('players', [])
        intent = analysis.get('intent', 'general')
        is_future_query = analysis.get('is_temporal', False) or intent == 'schedule'
        
        # Gather relevant NBA data
        nba_context = ""
        ml_prediction_context = ""
        
        # 2. Handle Schedule/Upcoming Games
        if is_future_query or intent == 'schedule':
            todays_games = nba_data_service.get_todays_games()
            
            if todays_games:
                nba_context += nba_data_service.format_todays_games_for_prompt(todays_games)
                
                # Check for specific team predictions in today's games
                if team_names:
                    for team_name in team_names[:2]:
                        team = nba_data_service.search_team_by_name(team_name)
                        if team:
                            game_info = nba_data_service.find_team_game_today(team['id'])
                            
                            if game_info:
                                game, opponent = game_info
                                is_home = game['home_team']['id'] == team['id']
                                opponent_id = opponent['id']
                                
                                # Get stats and predict
                                team_stats = nba_data_service.get_team_stats(team['id'])
                                opp_stats = nba_data_service.get_team_stats(opponent_id)
                                
                                if team_stats and opp_stats:
                                    model_input = {
                                        'AVG_PTS': team_stats.get('avg_pts', 0) / team_stats.get('games_played', 1),
                                        'AVG_FG_PCT': team_stats.get('avg_fg_pct', 0),
                                        'AVG_REB': team_stats.get('avg_reb', 0) / team_stats.get('games_played', 1),
                                        'AVG_AST': team_stats.get('avg_ast', 0) / team_stats.get('games_played', 1),
                                        'HOME': 1 if is_home else 0
                                    }
                                    
                                    prediction = predictor.predict_game(model_input)
                                    
                                    opp_name = f"{opponent['city']} {opponent['name']}"
                                    ml_prediction_context += f"\n\nML MODEL PREDICTION for {team['full_name']} vs {opp_name}:\n"
                                    ml_prediction_context += f"- Win Probability: {prediction['win_probability']:.1%}\n"
                                    ml_prediction_context += f"- Location: {'Home' if is_home else 'Away'}\n"
                                    
                                    nba_context += nba_data_service.format_team_stats_for_prompt(team_stats, team['full_name'])
                                    nba_context += nba_data_service.format_team_stats_for_prompt(opp_stats, opp_name)
                            else:
                                nba_context += f"\n{team['full_name']} does not have a game scheduled for today.\n"
            else:
                nba_context += "\nNo NBA games scheduled for today.\n"
        
        # 3. Handle General Team Stats/Info
        if team_names and not ml_prediction_context:
            for team_name in team_names[:2]:
                team = nba_data_service.search_team_by_name(team_name)
                if team:
                    stats = nba_data_service.get_team_stats(team['id'])
                    nba_context += nba_data_service.format_team_stats_for_prompt(stats, team['full_name'])
                    
                    recent_games = nba_data_service.get_team_recent_games(team['id'], n=5)
                    nba_context += nba_data_service.format_recent_games_for_prompt(recent_games, team['full_name'])
                    nba_context += "\n"
        
        # 4. Handle Player Stats
        if player_names:
            for player_name in player_names:
                player = nba_data_service.search_player_by_name(player_name)
                if player:
                    stats = nba_data_service.get_player_season_stats(player['id'])
                    nba_context += nba_data_service.format_player_stats_for_prompt(stats, player['full_name'])
                    
                    recent_games = nba_data_service.get_player_recent_games(player['id'], n=5)
                    nba_context += nba_data_service.format_player_recent_games_for_prompt(recent_games, player['full_name'])
                    nba_context += "\n"
        
        # 5. Handle Standings (if explicitly asked or if context is empty)
        if intent == 'standings' or (not nba_context and not ml_prediction_context):
            standings = nba_data_service.get_team_standings()
            if not standings.empty:
                east = standings[standings['Conference'] == 'East'].head(5)
                west = standings[standings['Conference'] == 'West'].head(5)
                nba_context += "\nTop 5 Eastern Conference:\n"
                nba_context += nba_data_service.format_standings_for_prompt(east)
                nba_context += "\nTop 5 Western Conference:\n"
                nba_context += nba_data_service.format_standings_for_prompt(west)
        
        # Create enhanced prompt
        prompt = f"""You are an NBA prediction AI assistant with access to real-time NBA data and machine learning models.

REAL-TIME NBA DATA:
{nba_context if nba_context else 'No specific team data requested.'}

{ml_prediction_context}

User query: {query}

Provide a helpful, data-driven response using the real-time NBA data and ML predictions above. Reference specific stats, trends, and the ML model's prediction when available. Keep responses concise (3-4 sentences) and basketball-focused."""

        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return process_query_fallback(query)

def extract_teams_from_query(query):
    """Extract team names from user query"""
    return extract_teams(query)

def process_query_fallback(query):
    """Fallback response if Gemini fails"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['predict', 'win', 'vs', 'versus', 'against', 'beat']):
        teams = extract_teams(query)
        if len(teams) >= 2:
            return f"I can analyze the matchup between {teams[0]} and {teams[1]}. My ML model considers recent performance, home advantage, and key stats. Would you like a detailed prediction?"
        else:
            return "To predict a game, please specify both teams. For example: 'Lakers vs Celtics prediction'"
    
    elif any(word in query_lower for word in ['hi', 'hello', 'hey']):
        return "Hi! I'm your NBA prediction assistant powered by AI. Ask me about any NBA matchup or team statistics!"
    
    else:
        return "Gemini might not be functioning as usual, try again later."

def extract_teams(query):
    """Extract team names from query"""
    nba_teams = [
        'lakers', 'celtics', 'warriors', 'heat', 'bucks', 'nets', 'suns',
        'nuggets', 'clippers', 'mavericks', 'sixers', '76ers', 'knicks',
        'bulls', 'cavaliers', 'cavs', 'raptors', 'grizzlies', 'hawks',
        'wizards', 'hornets', 'magic', 'pistons', 'pacers', 'spurs',
        'thunder', 'blazers', 'kings', 'pelicans', 'timberwolves', 'jazz',
        'rockets', 'trail blazers'
    ]
    
    query_lower = query.lower()
    found_teams = []
    
    for team in nba_teams:
        if team in query_lower:
            found_teams.append(team.capitalize())
    
    return found_teams

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict game outcome with detailed stats"""
    try:
        data = request.json
        team_stats = data.get('team_stats', {})
        
        if not team_stats:
            return jsonify({
                'success': False,
                'error': 'Team stats are required'
            }), 400
        
        if predictor.model is None:
            return jsonify({
                'success': False,
                'error': 'Model not trained. Please train the model first.'
            }), 400
        
        result = predictor.predict_game(team_stats)
        
        # Generate AI explanation using Gemini
        if gemini_model:
            explanation_prompt = f"""Explain this NBA game prediction in 2-3 sentences:
            
Win Probability: {result['win_probability']:.1%}
Team Stats:
- Average Points: {team_stats.get('AVG_PTS', 'N/A')}
- Field Goal %: {team_stats.get('AVG_FG_PCT', 'N/A')}
- Rebounds: {team_stats.get('AVG_REB', 'N/A')}
- Assists: {team_stats.get('AVG_AST', 'N/A')}
- Home Game: {'Yes' if team_stats.get('HOME', 0) == 1 else 'No'}

Provide a brief analysis of why this prediction makes sense."""

            try:
                explanation = gemini_model.generate_content(explanation_prompt)
                result['ai_explanation'] = explanation.text
            except:
                result['ai_explanation'] = "Prediction based on recent team performance and statistical trends."
        
        return jsonify({
            'success': True,
            'prediction': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/train', methods=['POST'])
def train_model():
    """Trigger model training"""
    try:
        accuracy = predictor.train()
        return jsonify({
            'success': True,
            'accuracy': accuracy,
            'message': 'Model trained successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upcoming-games', methods=['GET'])
def upcoming_games():
    """Get upcoming games"""
    try:
        collector = NBADataCollector()
        games = collector.get_upcoming_games()
        return jsonify({
            'success': True,
            'games': games
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/collect-data', methods=['POST'])
def collect_data():
    """Collect latest NBA data"""
    try:
        collector = NBADataCollector()
        # Collect last 3 seasons
        games = collector.collect_game_data(seasons=["2022-23", "2023-24", "2024-25"])
        games_with_stats = collector.get_teams_stats(games)
        collector.save_data(games_with_stats)
        
        return jsonify({
            'success': True,
            'games_collected': len(games),
            'message': 'Data collected successfully for seasons 2022-25'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': predictor.model is not None,
        'gemini_configured': gemini_model is not None
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')