import time
from pynput import keyboard
import threading

class TypingMonitor:
    def __init__(self, chunk_callback, shortcut_callback=None, chunk_size=30, max_flight_time=2.0):
        self.chunk_callback = chunk_callback
        self.shortcut_callback = shortcut_callback
        self.chunk_size = chunk_size
        self.max_flight_time = max_flight_time
        
        self.current_chunk = []
        self.key_press_times = {}
        self.last_key_release_time = None
        
        self.modifiers_held = set()
        
        self.listener = None
        self.is_running = False

    def start(self):
        self.is_running = True
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def stop(self):
        self.is_running = False
        if self.listener:
            self.listener.stop()

    def on_press(self, key):
        if not self.is_running:
            return
            
        now = time.time()
        
        # Track modifiers
        if key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, 
                   keyboard.Key.alt_l, keyboard.Key.alt_r, 
                   keyboard.Key.alt_gr, keyboard.Key.cmd, keyboard.Key.cmd_r]:
            self.modifiers_held.add(key)
            return
            
        # Detect shortcuts like Ctrl+V, Ctrl+X, Win+R
        if self.modifiers_held:
            ctrl_held = (keyboard.Key.ctrl_l in self.modifiers_held or 
                         keyboard.Key.ctrl_r in self.modifiers_held)
            win_held = (keyboard.Key.cmd in self.modifiers_held or 
                        keyboard.Key.cmd_r in self.modifiers_held)
            
            # Get the virtual key code (works even when Ctrl mangles key.char)
            vk = getattr(key, 'vk', None) or getattr(key, 'value', None)
            if vk is None and hasattr(key, 'char') and key.char:
                vk = ord(key.char.upper()) if len(key.char) == 1 and key.char.isprintable() else None
            
            if self.shortcut_callback:
                # Ctrl+V (paste) — vk 0x56 = 'V'
                if ctrl_held and vk == 0x56:
                    self.shortcut_callback('ctrl+v')
                # Ctrl+X (cut) — vk 0x58 = 'X'
                elif ctrl_held and vk == 0x58:
                    self.shortcut_callback('ctrl+x')
                # Win+R (run dialog) — vk 0x52 = 'R'
                elif win_held and vk == 0x52:
                    self.shortcut_callback('win+r')
            
            return # Ignore keystrokes when modifiers are held

        if key not in self.key_press_times:
            self.key_press_times[key] = now

    def on_release(self, key):
        if not self.is_running:
            return
            
        now = time.time()
        
        if key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, 
                   keyboard.Key.alt_l, keyboard.Key.alt_r, 
                   keyboard.Key.alt_gr, keyboard.Key.cmd, keyboard.Key.cmd_r]:
            self.modifiers_held.discard(key)
            return

        if self.modifiers_held:
            return

        if key in self.key_press_times:
            press_time = self.key_press_times.pop(key)
            dwell_time = now - press_time
            
            flight_time = 0.0
            if self.last_key_release_time is not None:
                flight_time = press_time - self.last_key_release_time
                if flight_time > self.max_flight_time:
                    flight_time = self.max_flight_time
            
            self.last_key_release_time = now
            
            # Heuristic for special characters
            is_special = 1 if not hasattr(key, 'char') or key.char is None or not key.char.isalnum() else 0
            
            self.current_chunk.append({
                'dwell_time': dwell_time,
                'flight_time': flight_time,
                'is_special': is_special
            })
            
            if len(self.current_chunk) >= self.chunk_size:
                chunk = self.current_chunk.copy()
                self.current_chunk = []
                self.chunk_callback(chunk)
