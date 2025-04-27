import numpy as np
from statistics import median, stdev

def safe_average(values, default=0):
    """Robust average calculation with outlier removal"""
    if not values:
        return default
    
    clean = [x for x in values if x is not None and not np.isnan(x)]
    if not clean:
        return default
    
    # Remove outliers beyond 2 standard deviations
    if len(clean) > 5:
        avg = np.mean(clean)
        std = stdev(clean)
        clean = [x for x in clean if abs(x - avg) < 2 * std]
    
    return sum(clean) / len(clean)

def preprocess_behavior(data):
    """Convert raw behavior data to model features"""
    # Basic features
    typing_speeds = data.get('typing_speed', [])
    mouse_speeds = data.get('mouse_speed', [])
    click_accuracies = data.get('click_accuracy', [])
    
    # Derived features
    features = [
        safe_average(typing_speeds),  # Mean typing interval
        safe_average(mouse_speeds),   # Mean mouse speed
        safe_average(click_accuracies),  # Click consistency
        min(typing_speeds, default=0),  # Minimum typing interval
        max(mouse_speeds, default=0),    # Maximum mouse speed
        len(typing_speeds),              # Number of keystrokes
        len(mouse_speeds)                # Number of mouse movements
    ]
    
    return [float(f) for f in features]  # Ensure all are floats