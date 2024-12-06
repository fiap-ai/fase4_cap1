import os
from datetime import datetime, timedelta
import random
import numpy as np
from database import DatabaseManager
from dotenv import load_dotenv

def generate_realistic_data(start_date, end_date, readings_per_hour=3):
    """
    Generate realistic sensor data with daily patterns and weather variations.
    
    Args:
        start_date: Starting date for data generation
        end_date: Ending date for data generation
        readings_per_hour: Number of readings per hour (default: 3, meaning every 20 minutes)
    """
    data = []
    
    # Base values and seasonal patterns
    base_temp = 25  # Base temperature in Celsius
    base_humidity = 60  # Base humidity percentage
    
    # Generate data for each day
    current_date = start_date
    while current_date <= end_date:
        print(f"Generating data for {current_date.date()}")
        
        # Add some day-to-day variation (weather patterns)
        daily_temp_offset = random.uniform(-3, 3)
        daily_humidity_offset = random.uniform(-10, 10)
        
        # Simulate weather events (e.g., rainy days)
        is_rainy_day = random.random() < 0.3  # 30% chance of a rainy day
        if is_rainy_day:
            daily_humidity_offset += random.uniform(10, 20)
            daily_temp_offset -= random.uniform(2, 5)
        
        # Generate readings throughout the day
        for hour in range(24):
            for reading in range(readings_per_hour):
                # Calculate exact timestamp
                minutes = (reading * 60) // readings_per_hour
                timestamp = current_date.replace(hour=hour, minute=minutes, second=0, microsecond=0)
                
                # Temperature variation
                # Daily cycle: coolest at 4AM, warmest at 2PM
                hour_temp_offset = -5 * np.cos((hour - 14) * 2 * np.pi / 24)
                temperature = base_temp + daily_temp_offset + hour_temp_offset
                # Add some random noise
                temperature += random.uniform(-0.5, 0.5)
                
                # Humidity variation (inverse to temperature)
                # Higher at night, lower during day
                hour_humidity_offset = 15 * np.cos((hour - 14) * 2 * np.pi / 24)
                humidity = base_humidity + daily_humidity_offset + hour_humidity_offset
                # Add some random noise
                humidity += random.uniform(-2, 2)
                
                # Light level based on time of day
                if 6 <= hour < 18:  # Daytime
                    if 6 <= hour < 10:  # Morning ramp up
                        light = np.interp(hour + reading/readings_per_hour, [6, 10], [50, 600])
                    elif 10 <= hour < 15:  # Mid-day
                        light = random.uniform(500, 700)
                    else:  # Afternoon ramp down
                        light = np.interp(hour + reading/readings_per_hour, [15, 18], [500, 50])
                    # Add cloud coverage variation
                    if is_rainy_day:
                        light *= random.uniform(0.3, 0.6)  # Heavy cloud coverage
                    else:
                        light *= random.uniform(0.7, 1.0)  # Light cloud coverage
                else:  # Night time
                    light = random.uniform(0, 50)
                
                # Button states (P and K sensors)
                # More likely to be active during daytime and when not raining
                daytime_factor = 0.7 if 6 <= hour < 18 else 0.3
                weather_factor = 0.5 if is_rainy_day else 1.0
                btn_p = 1 if random.random() < (daytime_factor * weather_factor) else 0
                btn_k = 1 if random.random() < (daytime_factor * weather_factor * 0.8) else 0
                
                # Ensure values are within valid ranges
                temperature = max(10, min(50, temperature))
                humidity = max(30, min(80, humidity))
                light = max(0, min(700, light))
                
                # Determine relay status based on conditions
                relay_status = 1 if (
                    30 <= humidity <= 80 and
                    10 <= temperature <= 50 and
                    0 <= light <= 700 and
                    (btn_p == 1 or btn_k == 1) and
                    not is_rainy_day  # Don't irrigate on rainy days
                ) else 0
                
                data.append({
                    'timestamp': timestamp,
                    'temperature': round(temperature, 2),
                    'humidity': round(humidity, 2),
                    'light': round(light, 2),
                    'btn_p': btn_p,
                    'btn_k': btn_k,
                    'relay_status': relay_status
                })
        
        current_date += timedelta(days=1)
    
    # Sort data by timestamp
    data.sort(key=lambda x: x['timestamp'])
    return data

def main():
    # Load environment variables
    load_dotenv()
    
    try:
        # Connect to database
        print("Connecting to database...")
        db = DatabaseManager()
        db.connect()
        
        # Delete existing data
        print("Deleting existing data...")
        db.delete_all_readings()
        
        # Generate data from December 1st to December 6th, 2024
        print("Generating mock data...")
        start_date = datetime(2024, 12, 1, 0, 0, 0)
        end_date = datetime(2024, 12, 6, 23, 59, 59)
        mock_data = generate_realistic_data(start_date, end_date, readings_per_hour=3)
        
        # Insert mock data
        print(f"Inserting {len(mock_data)} readings...")
        for reading in mock_data:
            timestamp = reading.pop('timestamp')  # Remove timestamp from dict
            db.insert_sensor_data(timestamp=timestamp, **reading)
        
        print("Mock data generation complete!")
        print(f"Generated {len(mock_data)} readings over {(end_date - start_date).days + 1} days")
        print(f"Date range: {start_date} to {end_date}")
        print(f"Readings per hour: 3 (every 20 minutes)")
        print(f"Total readings per day: {3 * 24}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    main()
