import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class NBAPredictor:
    def __init__(self):
        self.model = None
        self.feature_columns = [
            'AVG_PTS', 'AVG_FG_PCT', 'AVG_REB', 'AVG_AST', 
            'HOME', 'PLUS_MINUS'
        ]
        
    def prepare_features(self, df):
        """Prepare features for training"""
        # Fill NaN values
        df = df.fillna(df.mean(numeric_only=True))
        
        X = df[self.feature_columns] #Input data
        y = df['WIN'] # Output data
        
        return X, y
    
    def train(self, data_path='../nba-predictor/nba_games.csv'):
        """Train the model"""
        print("Loading data...")
        df = pd.read_csv(data_path)
        
        print("Preparing features...")
        X, y = self.prepare_features(df)
        
        """80% for training 20% for testing"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print("Training model...")
        self.model = RandomForestClassifier(
            n_estimators=200, # 200 decision trees
            max_depth=15, # 15 level max
            min_samples_split=10, # needs 10 samples to split a node
            random_state=42 # reproducible result
        )
        self.model.fit(X_train, y_train) # model learn patterns between x_train and y_train
        
        # Evaluate
        y_pred = self.model.predict(X_test) # predicts based on test data
        accuracy = accuracy_score(y_test, y_pred) # gives accuracy score
        
        print(f"\nModel Accuracy: {accuracy:.2%}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Save model
        self.save_model()
        
        return accuracy
    
    def predict_game(self, team_stats):
        """Predict outcome for a single game"""
        if self.model is None:
            self.load_model()
        
        # Ensure correct feature order
        features = [team_stats.get(col, 0) for col in self.feature_columns]
        prediction = self.model.predict([features])[0]
        probability = self.model.predict_proba([features])[0]
        
        return {
            'win_prediction': bool(prediction),
            'win_probability': float(probability[1]),
            'loss_probability': float(probability[0])
        }
    
    def save_model(self, filepath='nba_model.pkl'):
        """Save trained model"""
        joblib.dump(self.model, filepath) # replaces old model with newest trained model
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='nba_model.pkl'):
        """Load trained model"""
        if os.path.exists(filepath):
            self.model = joblib.load(filepath)
            print("Model loaded successfully")
        else:
            raise FileNotFoundError("Model file not found. Train the model first.")

if __name__ == '__main__':
    predictor = NBAPredictor()
    predictor.train()