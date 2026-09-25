# KeyGuard — Behavioral Biometrics Continuous Authentication

KeyGuard is a lightweight CLI tool and background security daemon for **Windows 10/11** that continuously monitors your typing rhythm to detect unauthorized access on unlocked laptops.

It learns *how* you type — not *what* you type — and challenges anyone whose typing pattern doesn't match yours.

---

## How It Works

```
You type normally → KeyGuard silently monitors in the background
                          ↓
              Typing rhythm matches yours? → Nothing happens
                          ↓
              Rhythm looks different? → Challenge modal appears
                          ↓
              Correct passphrase → Resume monitoring
              Wrong passphrase / Alt+Tab → Laptop locks instantly
```

### Metrics Captured
| Metric | Description |
|--------|-------------|
| **Dwell Time** | How long you hold each key down (press → release) |
| **Flight Time** | The gap between releasing one key and pressing the next |

### Detection
- **30 keystrokes** (~5-6 words) per analysis window
- A single anomalous window triggers the challenge prompt
- **Ctrl+V / Ctrl+X / Win+R** immediately trigger the challenge (anti-paste protection)

---

## Installation

```powershell
git clone https://github.com/YOUR_USERNAME/keyguard.git
cd keyguard
pip install -e .
```

### Dependencies
- Python 3.10+
- Windows 10/11
- `scikit-learn`, `joblib`, `psutil`, `pynput`, `bcrypt`

---

## Usage

### 1. Train your typing profile
```powershell
keyguard train
```
You'll set a passphrase and type naturally until ~150+ keystrokes are captured. Type whatever you want — emails, thoughts, anything.

### 2. Start background monitoring
```powershell
keyguard start
```
KeyGuard launches as a **detached background process**. You can close the terminal — it keeps running silently.

### 3. Check status
```powershell
keyguard status
```
Shows PID, CPU, and memory usage.

### 4. Stop monitoring
```powershell
keyguard stop
```

### 5. Retrain with expanded data
```powershell
keyguard retrain
```
Rebuilds the model using all collected data (including data from successful challenge validations).

---

## Architecture

```
keyguard/
├── cli.py              # CLI entry point (start, stop, train, status, retrain)
├── daemon.py           # Background process loop, anomaly counting
├── keyboard_hook.py    # Low-level keystroke capture via pynput
├── ml_engine.py        # IsolationForest training & inference
├── challenge_ui.py     # Fullscreen tkinter challenge modal
├── config.py           # Settings, state, and passphrase storage
├── __init__.py
```

### ML Model
- **Algorithm**: `sklearn.ensemble.IsolationForest`
- **Features per 30-keystroke chunk**: mean/median/std of dwell time, mean/median/std of flight time, special character ratio
- **Inference**: < 1ms
- **Model size**: < 1 MB

### Two-Phase Learning
1. **Phase 1 — Calibration**: Guided 150+ keystroke session via `keyguard train`
2. **Phase 2 — Passive Expansion**: When you successfully pass a challenge, your recent "anomalous" typing gets auto-tagged as valid and added to the dataset

### Edge Case Handling
| Scenario | Solution |
|----------|----------|
| Slow typing / thinking | Flight time capped at 2 seconds |
| Copy/paste attack | Ctrl+V / Ctrl+X instantly trigger challenge |
| Win+R (Run dialog) | Immediately triggers challenge |
| High CPU / gaming | Auto-pauses monitoring when CPU > 80% |
| Alt+Tab from challenge | Locks workstation after 2s grace period |

---

## Security Notes

- KeyGuard does **not** log what you type — only the timing between keystrokes
- Your passphrase is stored as a **bcrypt hash** in `%APPDATA%/KeyGuard/config.json`
- The trained model and dataset are stored locally in `%APPDATA%/KeyGuard/`
- KeyGuard **cannot** monitor the Windows Lock Screen (Secure Desktop blocks all user-level hooks)

---

## License

MIT License — see [LICENSE](LICENSE)
