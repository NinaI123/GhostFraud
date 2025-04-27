from sklearn.ensemble import IsolationForest
import numpy as np
import joblib
import os

class AnomalyDetector:
    def __init__(self):
        self.model_path = "models/isolation_forest_model.pkl"
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            self.model = IsolationForest(contamination=0.05)
            dummy_data = np.random.rand(1000, 8)  # 8 features
            self.model.fit(dummy_data)
            joblib.dump(self.model, self.model_path)

    def predict(self, features):
        features = np.array(features).reshape(1, -1)
        score = -self.model.decision_function(features)[0]
        return score
