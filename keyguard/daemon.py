import time
import psutil
from .keyboard_hook import TypingMonitor
from .ml_engine import MLEngine
from .challenge_ui import prompt_challenge
from .config import MODEL_FILE, DATASET_FILE

class Daemon:
    def __init__(self):
        self.ml = MLEngine(MODEL_FILE, DATASET_FILE)
        self.monitor = TypingMonitor(
            chunk_callback=self.on_chunk_ready,
            shortcut_callback=self.on_suspicious_shortcut
        )
        self.anomaly_count = 0
        self.recent_chunks = []
        self.is_running = False

    def is_system_loaded(self):
        cpu = psutil.cpu_percent(interval=0.1)
        return cpu > 80.0

    def on_chunk_ready(self, chunk):
        if self.is_system_loaded():
            return

        prediction = self.ml.predict(chunk)
        if prediction == -1:
            self.anomaly_count += 1
            self.recent_chunks.append(chunk)
            
            if self.anomaly_count >= 1:
                self.trigger_challenge()
        else:
            self.anomaly_count = max(0, self.anomaly_count - 1)
            if len(self.recent_chunks) > 10:
                self.recent_chunks.pop(0)

    def on_suspicious_shortcut(self, shortcut):
        print(f"Suspicious shortcut detected: {shortcut}. Triggering challenge.")
        self.trigger_challenge()

    def trigger_challenge(self):
        self.monitor.stop()
        
        success = prompt_challenge()
        if success:
            print("Challenge passed.")
            if self.recent_chunks:
                self.ml.append_to_dataset(self.recent_chunks)
            self.anomaly_count = 0
            self.recent_chunks = []
            self.monitor.start()
        else:
            print("Challenge failed or focus lost. Workstation locked.")
            self.anomaly_count = 0
            self.recent_chunks = []
            self.monitor.start()

    def run(self):
        self.is_running = True
        self.monitor.start()
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.is_running = False
        self.monitor.stop()

def run_daemon():
    d = Daemon()
    d.run()
