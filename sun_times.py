"""
Simple sun times module for visualization
"""
from datetime import datetime, timedelta
import math

def fetch_sun_times():
    """Return mock sunrise and sunset times"""
    # Mock data - in real implementation this would fetch actual sun data
    now = datetime.now()
    sunrise = now.replace(hour=6, minute=30, second=0, microsecond=0)
    sunset = now.replace(hour=18, minute=45, second=0, microsecond=0)
    return sunrise.strftime("%H:%M"), sunset.strftime("%H:%M")

def get_sun_position_fraction(sunrise, sunset):
    """Calculate sun position as fraction of day (0.0 = midnight, 0.5 = noon)"""
    now = datetime.now()
    # Calculate fraction of day passed
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    seconds_in_day = 24 * 60 * 60
    fraction = seconds_since_midnight / seconds_in_day
    
    # Add some variation to make it more interesting
    variation = 0.1 * math.sin(seconds_since_midnight / 3600)  # Hourly variation
    return min(1.0, max(0.0, fraction + variation))