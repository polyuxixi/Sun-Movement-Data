"""
Simple data fetcher module for visualization
"""
import pandas as pd
from datetime import datetime, timedelta
import random

class DataFetcher:
    """Mock data fetcher for sun movement visualization"""
    
    def __init__(self):
        self.data = self._generate_mock_data()
    
    def _generate_mock_data(self):
        """Generate mock sun movement data"""
        # Create 24 hours of mock data
        data = []
        base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for hour in range(24):
            for minute in range(0, 60, 15):  # Every 15 minutes
                time_point = base_time + timedelta(hours=hour, minutes=minute)
                
                # Mock sun elevation (0-90 degrees, peak at noon)
                hour_fraction = (hour + minute/60) / 24
                elevation = max(0, 90 * abs(0.5 - abs(hour_fraction - 0.5)) * 2)
                
                # Mock azimuth (0-360 degrees, east to west)
                azimuth = 90 + 180 * hour_fraction  # Starts east, moves to west
                
                # Add some random variation
                elevation += random.uniform(-5, 5)
                azimuth += random.uniform(-10, 10)
                
                data.append({
                    'time': time_point,
                    'elevation': max(0, min(90, elevation)),
                    'azimuth': azimuth % 360,
                    'intensity': max(0, elevation / 90)  # Brightness based on elevation
                })
        
        return pd.DataFrame(data)
    
    def get_current_sun_data(self):
        """Get current sun position data"""
        now = datetime.now()
        # Find closest time in our mock data
        time_diffs = abs(self.data['time'] - now)
        closest_idx = time_diffs.idxmin()
        return self.data.iloc[closest_idx].to_dict()
    
    def get_sun_data_for_time(self, target_time):
        """Get sun data for specific time"""
        time_diffs = abs(self.data['time'] - target_time)
        closest_idx = time_diffs.idxmin()
        return self.data.iloc[closest_idx].to_dict()