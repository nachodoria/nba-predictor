from flask import Flask, request, jsonify
from flask_cors import CORS
from model import NBAPredictor
from data_collector import NBADataCollector
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize predictor
predictor = NBAPredictor()

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

def generate_gemini_response(query):
    """Generate response using Gemini AI"""
    try:
        # Create context-aware prompt for Gemini
        prompt = f"""You are an NBA prediction AI assistant with access to machine learning models trained on NBA game data.

Your capabilities:
- Predict NBA game outcomes based on team statistics
- Analyze team performance metrics (points, field goal %, rebounds, assists)
- Consider home court advantage in predictions
- Provide win probability estimates

User query: {query}

Provide a helpful, informative response about NBA predictions. If the user asks about a specific matchup, explain what factors would influence the prediction. Keep responses concise (2-3 sentences) and basketball-focused."""

        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return process_query_fallback(query)

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
        return "I can help predict NBA games! Try asking: 'Will the Lakers beat the Warriors?' or 'Predict Celtics vs Heat'"

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

@app.route('/api/collect-data', methods=['POST'])
def collect_data():
    """Collect latest NBA data"""
    try:
        collector = NBADataCollector()
        games = collector.collect_game_data()
        games_with_stats = collector.get_team_stats(games)
        collector.save_data(games_with_stats)
        
        return jsonify({
            'success': True,
            'games_collected': len(games),
            'message': 'Data collected successfully'
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