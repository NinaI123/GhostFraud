from flask import Flask, render_template, request, jsonify
from model import FraudDetector
from data_processor import preprocess_behavior
import logging
from datetime import datetime

app = Flask(__name__)
fraud_detector = FraudDetector()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory store with session expiration
flagged_sessions = []
MAX_SESSIONS = 1000
SESSION_EXPIRE_HOURS = 24

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/behavior', methods=['POST'])
def behavior():
    try:
        raw_data = request.get_json(force=True)
        if not raw_data:
            logger.warning("Empty request received")
            return jsonify({"error": "No data received"}), 400
        
        logger.info(f"Behavior data received for session: {raw_data.get('session_id', 'unknown')}")

        # Preprocess and validate
        features = preprocess_behavior(raw_data)
        if not features or len(features) < 3:  # Ensure minimum features
            return jsonify({"error": "Insufficient behavioral data"}), 400

        # Predict risk
        risk_score = fraud_detector.predict_risk(features)
        risk_level = "low"
        
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"

        # Store risky sessions
        if risk_level in ("medium", "high"):
            clean_expired_sessions()
            if len(flagged_sessions) < MAX_SESSIONS:
                flagged_sessions.append({
                    "session_id": raw_data.get("session_id", str(datetime.now())),
                    "behavior": raw_data,
                    "features": features,
                    "risk_score": round(risk_score, 3),
                    "risk_level": risk_level,
                    "timestamp": datetime.now().isoformat()
                })

        return jsonify({
            "status": "success",
            "risk_score": round(risk_score, 3),
            "risk_level": risk_level,
            "feedback": "Continue normal behavior" if risk_level == "low" else "Additional verification required"
        })

    except Exception as e:
        logger.error(f"Error processing behavior: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

def clean_expired_sessions():
    global flagged_sessions
    now = datetime.now()
    flagged_sessions = [
        s for s in flagged_sessions 
        if (now - datetime.fromisoformat(s["timestamp"])).total_seconds() < SESSION_EXPIRE_HOURS * 3600
    ]

@app.route('/get_flagged_sessions')
def get_flagged_sessions():
    clean_expired_sessions()
    return jsonify({
        "count": len(flagged_sessions),
        "flagged_sessions": flagged_sessions[-100:]  # Return last 100 only
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)