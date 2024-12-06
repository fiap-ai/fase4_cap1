import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from datetime import datetime, timedelta

class IrrigationPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.features = ['humidity', 'temperature', 'light', 'btn_p', 'btn_k']
        
    def prepare_data(self, data):
        """
        Prepare data for training or prediction.
        Handles missing values and converts boolean to integer.
        """
        df = pd.DataFrame(data)
        
        # Convert column names to lowercase
        df.columns = df.columns.str.lower()
        
        # Convert boolean/numeric strings to integers for button states and relay status
        for col in ['btn_p', 'btn_k', 'relay_status']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Handle missing values
        df = df.fillna(method='ffill')
        
        # Ensure all required columns exist
        for feature in self.features:
            if feature not in df.columns:
                raise ValueError(f"Missing required feature: {feature}")
        
        return df
        
    def train(self, data):
        """
        Train the model using historical sensor data.
        Returns training metrics.
        """
        try:
            df = self.prepare_data(data)
            
            # Prepare features and target
            X = df[self.features]
            y = df['relay_status']
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42
            )
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Feature importance
            importance = dict(zip(self.features, self.model.feature_importances_))
            
            return {
                'mse': mse,
                'r2': r2,
                'feature_importance': importance
            }
        except Exception as e:
            raise Exception(f"Error during training: {str(e)}")
    
    def predict(self, sensor_data):
        """
        Predict irrigation need based on current sensor readings.
        Returns probability of irrigation need (0-1).
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        try:
            df = self.prepare_data([sensor_data])
            X = df[self.features]
            X_scaled = self.scaler.transform(X)
            
            prediction = self.model.predict(X_scaled)[0]
            return float(prediction)
        except Exception as e:
            raise Exception(f"Error during prediction: {str(e)}")
    
    def save_model(self, filepath='models/irrigation_model.joblib'):
        """Save the trained model and scaler"""
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
            
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'features': self.features
        }
        joblib.dump(model_data, filepath)
        
    def load_model(self, filepath='models/irrigation_model.joblib'):
        """Load a trained model and scaler"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.features = model_data['features']

def generate_sample_data(n_samples=1000):
    """
    Generate synthetic data for testing the model.
    """
    np.random.seed(42)
    
    # Generate timestamps
    base = datetime.now()
    timestamps = [base + timedelta(minutes=i) for i in range(n_samples)]
    
    # Generate sensor data
    data = {
        'timestamp': timestamps,
        'humidity': np.random.uniform(30, 80, n_samples),
        'temperature': np.random.uniform(10, 50, n_samples),
        'light': np.random.uniform(0, 700, n_samples),
        'btn_p': np.random.choice([0, 1], n_samples),
        'btn_k': np.random.choice([0, 1], n_samples)
    }
    
    # Generate target (relay_status) based on conditions
    df = pd.DataFrame(data)
    df['relay_status'] = (
        (df['humidity'].between(30, 80)) &
        (df['temperature'].between(10, 50)) &
        (df['light'].between(0, 700)) &
        ((df['btn_p'] == 1) | (df['btn_k'] == 1))
    ).astype(int)
    
    return df

if __name__ == "__main__":
    # Example usage
    predictor = IrrigationPredictor()
    
    # Generate sample data
    sample_data = generate_sample_data()
    
    # Train model
    metrics = predictor.train(sample_data)
    print("\nTraining Metrics:")
    print(f"Mean Squared Error: {metrics['mse']:.4f}")
    print(f"R² Score: {metrics['r2']:.4f}")
    print("\nFeature Importance:")
    for feature, importance in metrics['feature_importance'].items():
        print(f"{feature}: {importance:.4f}")
    
    # Example prediction
    current_reading = {
        'humidity': 60.0,
        'temperature': 25.0,
        'light': 350.0,
        'btn_p': 1,
        'btn_k': 0
    }
    
    prediction = predictor.predict(current_reading)
    print(f"\nPrediction for current reading: {prediction:.4f}")
