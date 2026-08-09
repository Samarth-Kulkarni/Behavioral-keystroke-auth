import os
import json
from pathlib import Path

# Base directory for KeyGuard data
APP_DIR = Path(os.environ.get('APPDATA', Path.home())) / 'KeyGuard'
CONFIG_FILE = APP_DIR / 'config.json'
DATASET_FILE = APP_DIR / 'typing_dataset.csv'
STATE_FILE = APP_DIR / 'state.json'
MODEL_FILE = APP_DIR / 'model.joblib'

def ensure_dirs():
    APP_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    ensure_dirs()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config_data):
    ensure_dirs()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

def load_state():
    ensure_dirs()
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state_data):
    ensure_dirs()
    with open(STATE_FILE, 'w') as f:
        json.dump(state_data, f, indent=4)
