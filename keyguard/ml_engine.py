import os

# Heavy libraries will be lazy-loaded in the methods
# pandas, numpy, sklearn, joblib
class MLEngine:
    def __init__(self, model_file, dataset_file):
        self.model_file = model_file
        self.dataset_file = dataset_file
        self.model = None
        self.load_model()
    
    def extract_features(self, chunk):
        import numpy as np
        # chunk is a list of dicts: [{'dwell_time': X, 'flight_time': Y, 'is_special': Z}, ...]
        dwell_times = [k['dwell_time'] for k in chunk]
        flight_times = [k['flight_time'] for k in chunk]
        specials = [k['is_special'] for k in chunk]
        
        # Add small epsilon to avoid zero division or nan in std
        return {
            'dwell_mean': np.mean(dwell_times),
            'dwell_median': np.median(dwell_times),
            'dwell_std': np.std(dwell_times) + 1e-6,
            'flight_mean': np.mean(flight_times),
            'flight_median': np.median(flight_times),
            'flight_std': np.std(flight_times) + 1e-6,
            'special_ratio': np.mean(specials)
        }
        
    def train(self, data_chunks=None):
        import pandas as pd
        from sklearn.ensemble import IsolationForest
        import joblib
        df = None
        
        # Load existing dataset if it exists
        if os.path.exists(self.dataset_file):
            df = pd.read_csv(self.dataset_file)
            
        if data_chunks:
            features = [self.extract_features(chunk) for chunk in data_chunks]
            new_df = pd.DataFrame(features)
            
            if df is not None:
                df = pd.concat([df, new_df], ignore_index=True)
            else:
                df = new_df
                
            # Save combined dataset
            df.to_csv(self.dataset_file, index=False)
            
        if df is None or len(df) == 0:
            return False
            
        # Train Isolation Forest on the entire dataset
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.model.fit(df)
        
        # Save model
        joblib.dump(self.model, self.model_file)
        return True
        
    def append_to_dataset(self, data_chunks):
        import pandas as pd
        if not data_chunks:
            return
        features = [self.extract_features(chunk) for chunk in data_chunks]
        df = pd.DataFrame(features)
        
        if not os.path.exists(self.dataset_file):
            df.to_csv(self.dataset_file, index=False)
        else:
            df.to_csv(self.dataset_file, mode='a', header=False, index=False)

        
    def load_model(self):
        import joblib
        if os.path.exists(self.model_file):
            self.model = joblib.load(self.model_file)
            
    def predict(self, chunk):
        import pandas as pd
        if self.model is None:
            return 1 # If no model, assume it's valid (1)
            
        features = self.extract_features(chunk)
        df = pd.DataFrame([features])
        prediction = self.model.predict(df)
        return prediction[0] # 1 for normal, -1 for anomaly
