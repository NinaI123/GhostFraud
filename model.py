import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os
from datetime import datetime

MODEL_PATH = "model/isolation_forest.pkl"
MODEL_VERSION = "1.0.0"

class FraudDetector:
    def __init__(self):
        # More realistic synthetic patterns
        self.normal_patterns = {
            'typing': (180, 30),  # (mean_ms, std_dev)
            'mouse': (0.8, 0.2),
            'clicks': (3, 1)
        }
        self.model = self._train_model()
    
    def _train_model(self):
        # Generate realistic normal behavior
        n_samples = 1000
        typing = np.random.normal(*self.normal_patterns['typing'], n_samples)
        mouse = np.random.normal(*self.normal_patterns['mouse'], n_samples)
        clicks = np.clip(np.random.normal(*self.normal_patterns['clicks'], n_samples), 1, None)
        
        X_train = np.column_stack([typing, mouse, clicks])
        
        # Adjust contamination for more sensitivity
        model = IsolationForest(
            n_estimators=200,
            contamination=0.15,  # Increased from 0.05
            random_state=42
        )
        model.fit(X_train)
        return model

    def predict_risk(self, features):
        """Returns score between 0 (normal) and 1 (anomalous)"""
        if len(features) < 3:  # Ensure enough features
            return 0.5
            
        # Convert to numpy array
        X = np.array(features[:3]).reshape(1, -1)  # Use first 3 features
        
        # Get anomaly score (-1 to 1 where -1 is anomalous)
        score = self.model.decision_function(X)[0]
        
        # Normalize to 0-1 range (1 is anomalous)
        return float((1 - (score + 1) / 2))  # Convert -1:1 → 1:0 → 0:1