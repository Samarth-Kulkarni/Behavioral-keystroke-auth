import argparse
import sys
import subprocess
import os
import psutil
from .config import load_state, save_state, load_config
from .daemon import run_daemon
from .challenge_ui import setup_passphrase
from .ml_engine import MLEngine
from .config import MODEL_FILE, DATASET_FILE
from .keyboard_hook import TypingMonitor

def start_daemon():
    config = load_config()
    if 'passphrase' not in config:
        print("Please run 'keyguard train' or set a passphrase first.")
        return

    state = load_state()
    if 'pid' in state and psutil.pid_exists(state['pid']):
        print("Daemon is already running.")
        return

    # In windows, CREATE_NO_WINDOW is 0x08000000
    CREATE_NO_WINDOW = 0x08000000
    
    cmd = [sys.executable, '-m', 'keyguard.cli', '--run-daemon']
    
    process = subprocess.Popen(cmd, creationflags=CREATE_NO_WINDOW, close_fds=True)
    state['pid'] = process.pid
    save_state(state)
    print(f"KeyGuard started in background (PID: {process.pid}).")

def stop_daemon():
    state = load_state()
    if 'pid' in state:
        pid = state['pid']
        if psutil.pid_exists(pid):
            p = psutil.Process(pid)
            p.terminate()
            print("Daemon stopped.")
        else:
            print("Daemon was not running.")
        del state['pid']
        save_state(state)
    else:
        print("Daemon is not running.")

def status():
    state = load_state()
    if 'pid' in state:
        pid = state['pid']
        if psutil.pid_exists(pid):
            p = psutil.Process(pid)
            print(f"KeyGuard is running (PID: {pid}). CPU: {p.cpu_percent()}% Mem: {p.memory_info().rss / 1024 / 1024:.2f} MB")
            return
    print("KeyGuard is NOT running.")

def train():
    import getpass
    print("Welcome to KeyGuard Training Phase.")
    
    config = load_config()
    if 'passphrase' not in config:
        pwd = getpass.getpass("Set a passphrase for the challenge prompt: ")
        setup_passphrase(pwd)
        print("Passphrase saved.")
        
    print("\nTo calibrate KeyGuard, we need to record a baseline of your typing rhythm.")
    print("You can type whatever you want here! A stream of consciousness, some code,")
    print("an email, or you can just copy the sample text below.")
    print("-" * 50)
    print("SAMPLE TEXT:")
    print("The quick brown fox jumps over the lazy dog. Continuous authentication is a ")
    print("security mechanism that monitors user behavior to ensure that the user who ")
    print("initially logged into the system is the same user currently operating it.")
    print("-" * 50)
    
    chunks = []
    
    def on_chunk(chunk):
        chunks.append(chunk)
        print(f"\rCollected {len(chunks)*30} keystrokes...", end='', flush=True)
            
    monitor = TypingMonitor(chunk_callback=on_chunk, chunk_size=30)
    monitor.start()
    
    print("\nStart typing below. Keep typing until you reach at least 150 keystrokes.")
    print("(Press ENTER to submit lines as you type)")
    
    try:
        while len(chunks) < 5: # Need at least 5 chunks (150 keystrokes)
            input("> ")
            if len(chunks) < 5:
                print(f"\rStill need more data... (Current: {len(chunks)*30}/150 keystrokes). Keep typing!")
    except KeyboardInterrupt:
        pass
        
    monitor.stop()
    print(f"\nTraining data collected. Training model...")
    
    ml = MLEngine(MODEL_FILE, DATASET_FILE)
    if ml.train(chunks):
        print("Model trained successfully.")
    else:
        print("Failed to train model. Not enough data collected.")

def retrain():
    print("Retraining model on collected background data...")
    ml = MLEngine(MODEL_FILE, DATASET_FILE)
    if ml.train():
        print("Model retrained successfully.")
    else:
        print("Failed to retrain model. Dataset might be empty.")

def main():
    parser = argparse.ArgumentParser(description="KeyGuard - Behavioral Biometrics Continuous Authentication")
    parser.add_argument('command', nargs='?', choices=['start', 'stop', 'train', 'status', 'retrain'], help='Command to run')
    parser.add_argument('--run-daemon', action='store_true', help=argparse.SUPPRESS)
    
    args = parser.parse_args()
    
    if args.run_daemon:
        run_daemon()
        return

    if args.command == 'start':
        start_daemon()
    elif args.command == 'stop':
        stop_daemon()
    elif args.command == 'train':
        train()
    elif args.command == 'status':
        status()
    elif args.command == 'retrain':
        retrain()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
