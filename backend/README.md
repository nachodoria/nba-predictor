# NBA Predictor Backend

AI-powered NBA game prediction API using Machine Learning and Google Gemini AI.

## Features

- 🤖 **Gemini AI Integration** - Natural language responses powered by Google's Gemini 1.5 Flash
- 📊 **Machine Learning Predictions** - Random Forest model trained on historical NBA data
- 🏀 **Real NBA Data** - Live statistics from official NBA API
- 🔮 **Win Probability** - Calculate win/loss probabilities based on team stats
- 💬 **Conversational Interface** - Chat with the AI about NBA predictions

## Tech Stack

- **Python 3.8+**
- **Flask** - Web framework for REST API
- **Google Generative AI** - Gemini AI for intelligent responses
- **scikit-learn** - Machine Learning (Random Forest Classifier)
- **nba_api** - Official NBA statistics API
- **pandas & numpy** - Data processing and analysis

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Setup

1. **Clone the repository** (if not already done)
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # macOS/Linux
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create `.env` file**
   ```bash
   touch .env
   ```
   
   Add your Google Gemini API key:
   ```env
   GOOGLE_API_KEY=your-gemini-api-key-here
   ```

## Usage

### 1. Collect NBA Data

Fetch the latest NBA game statistics:

```bash
python data_collector.py
```

This will:
- Collect games from the 2024-25 season
- Calculate rolling averages (last 10 games)
- Save data to `../data/nba_games.csv`

### 2. Train the Model

Train the machine learning model:

```bash
python model.py
```

This will:
- Load NBA game data
- Train Random Forest classifier
- Display accuracy metrics
- Save model to `../nba_model.pkl`

### 3. Start the API Server

Run the Flask application:

```bash
python app.py
```

Server will start at: `http://localhost:5000`

You should see:
```
Gemini API configured successfully with gemini-1.5-flash
Model loaded successfully
* Running on http://0.0.0.0:5000
```

## API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "gemini_configured": true
}
```

---

### Chat with AI
```http
POST /api/chat
```

**Request Body:**
```json
{
  "query": "Will the Lakers beat the Celtics?"
}
```

**Response:**
```json
{
  "success": true,
  "query": "Will the Lakers beat the Celtics?",
  "response": "Based on recent performance data and statistical analysis..."
}
```

---

### Predict Game Outcome
```http
POST /api/predict
```

**Request Body:**
```json
{
  "team_stats": {
    "AVG_PTS": 112.5,
    "AVG_FG_PCT": 0.475,
    "AVG_REB": 45.2,
    "AVG_AST": 25.8,
    "HOME": 1,
    "PLUS_MINUS": 5.2
  }
}
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "win_prediction": true,
    "win_probability": 0.68,
    "loss_probability": 0.32,
    "ai_explanation": "The team shows strong offensive metrics..."
  }
}
```

---

### Train Model
```http
POST /api/train
```

**Response:**
```json
{
  "success": true,
  "accuracy": 0.72,
  "message": "Model trained successfully"
}
```

---

### Collect NBA Data
```http
POST /api/collect-data
```

**Response:**
```json
{
  "success": true,
  "games_collected": 2460,
  "message": "Data collected successfully"
}
```

## Project Structure

```
backend/
├── app.py              # Flask API server (main application)
├── model.py            # ML model training and prediction
├── data_collector.py   # NBA data collection from nba_api
├── .env                # Environment variables (API keys)
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── venv/               # Virtual environment (not in git)
```

## Model Features

The ML model uses these features for predictions:

- **AVG_PTS** - Average points scored (last 10 games)
- **AVG_FG_PCT** - Average field goal percentage
- **AVG_REB** - Average rebounds
- **AVG_AST** - Average assists
- **HOME** - Home court advantage (1 or 0)
- **PLUS_MINUS** - Point differential

## Dependencies

```
Flask==3.0.0
flask-cors==4.0.0
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
nba_api==1.4.1
joblib==1.3.2
python-dotenv==1.0.0
google-generativeai==0.3.0
```

## Troubleshooting

### "No module named 'google.generativeai'"
```bash
source venv/bin/activate
pip install google-generativeai
```

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "Port 5000 is already in use"
```bash
# Find and kill process
lsof -ti :5000 | xargs kill -9

# Or change port in app.py
app.run(debug=True, port=5001)
```

### "Model file not found"
```bash
# Train the model first
python model.py
```

### Gemini API Error 404
Make sure you're using the correct model name:
```python
gemini_model = genai.GenerativeModel('gemini-1.5-flash')
```

### "GOOGLE_API_KEY not found"
Create `.env` file with:
```
GOOGLE_API_KEY=your-actual-api-key
```

## Development

### Running in Debug Mode

The Flask app runs in debug mode by default, which provides:
- Hot reload on code changes
- Detailed error messages
- Interactive debugger

### Testing API Endpoints

Use curl or tools like Postman:

```bash
# Health check
curl http://localhost:5000/health

# Chat
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Predict Lakers vs Warriors"}'

# Prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "team_stats": {
      "AVG_PTS": 115.0,
      "AVG_FG_PCT": 0.48,
      "AVG_REB": 44.0,
      "AVG_AST": 26.0,
      "HOME": 1,
      "PLUS_MINUS": 6.5
    }
  }'
```

## Model Performance

The Random Forest classifier typically achieves:
- **Accuracy**: 70-75%
- **Precision**: 0.72
- **Recall**: 0.71
- **F1-Score**: 0.71

Performance may vary based on:
- Quality and quantity of training data
- Recent NBA season dynamics
- Feature engineering improvements

## Future Improvements

- [ ] Add player injury data
- [ ] Include team head-to-head records
- [ ] Implement XGBoost or Neural Network models
- [ ] Add real-time game predictions
- [ ] Integrate betting odds data
- [ ] Add more advanced statistics (PER, TS%, etc.)
- [ ] Cache predictions to reduce API calls
- [ ] Add authentication for API endpoints

## License

MIT License

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review API documentation
3. Open an issue on GitHub

---

**Note**: This project is for educational purposes. Always gamble responsibly if using predictions for betting.