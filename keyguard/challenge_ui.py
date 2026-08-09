import tkinter as tk
import ctypes
import bcrypt
from .config import load_config, save_config

def lock_workstation():
    ctypes.windll.user32.LockWorkStation()

def prompt_challenge():
    config = load_config()
    hashed_passphrase = config.get('passphrase')
    
    if not hashed_passphrase:
        lock_workstation()
        return False
        
    root = tk.Tk()
    root.title("KeyGuard - Authentication Required")
    
    result = [False]
    focus_protection_active = [False]
    
    def on_submit(event=None):
        password = entry.get()
        if bcrypt.checkpw(password.encode('utf-8'), hashed_passphrase.encode('utf-8')):
            result[0] = True
            root.destroy()
        else:
            lock_workstation()
            root.destroy()
    
    def block_key(event):
        # Block Alt+Tab, Alt+F4, etc.
        return "break"
    
    def on_focus_out(event):
        if not focus_protection_active[0]:
            return
        if event.widget == root:
            lock_workstation()
            root.destroy()
    
    def enable_focus_protection():
        # Give the window 2 seconds to fully render before arming focus-out detection
        focus_protection_active[0] = True
        root.bind('<FocusOut>', on_focus_out)
    
    # Make it a borderless topmost window that covers the screen
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    
    # Cover the entire screen
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root.geometry(f"{screen_w}x{screen_h}+0+0")
    root.configure(bg='#1a1a2e')
    
    # Block common escape shortcuts
    root.bind('<Alt-F4>', block_key)
    root.bind('<Alt-Tab>', block_key)
    root.bind('<Escape>', block_key)
    
    frame = tk.Frame(root, bg='#1a1a2e')
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    # Warning icon
    warning_label = tk.Label(frame, text="⚠", fg='#e94560', bg='#1a1a2e', font=('Segoe UI Emoji', 64))
    warning_label.pack(pady=(0, 10))
    
    label = tk.Label(frame, text="Unusual Typing Rhythm Detected", fg='#e94560', bg='#1a1a2e', font=('Segoe UI', 28, 'bold'))
    label.pack(pady=(0, 5))
    
    sub_label = tk.Label(frame, text="Enter your passphrase to continue", fg='#aaaaaa', bg='#1a1a2e', font=('Segoe UI', 14))
    sub_label.pack(pady=(0, 30))
    
    entry = tk.Entry(frame, show='●', font=('Segoe UI', 22), justify='center', width=30,
                     bg='#16213e', fg='white', insertbackground='white',
                     relief='flat', bd=0, highlightthickness=2, highlightcolor='#e94560')
    entry.pack(pady=10, ipady=10)
    entry.bind('<Return>', on_submit)
    
    btn = tk.Button(frame, text="Unlock", command=on_submit, font=('Segoe UI', 16, 'bold'),
                    bg='#e94560', fg='white', activebackground='#c23152', activeforeground='white',
                    relief='flat', bd=0, padx=40, pady=10, cursor='hand2')
    btn.pack(pady=20)
    
    # Force focus after a short delay to ensure window is fully visible
    def force_focus():
        root.focus_force()
        entry.focus_set()
    
    root.after(200, force_focus)
    
    # Arm focus-out protection after 2 seconds (window is fully settled by then)
    root.after(2000, enable_focus_protection)
    
    root.mainloop()
    return result[0]

def setup_passphrase(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    config = load_config()
    config['passphrase'] = hashed
    save_config(config)
