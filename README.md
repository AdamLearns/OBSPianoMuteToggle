# OBS Piano Mute Toggle

Automatically toggle your OBS mic mute by playing the highest F-major triad on your 88-key digital piano.

## Features

- **MIDI detection** of F7 + A7 + C8 (the highest F-major triad in root position)
- **Generous timing window** (200ms default) — you don't need to hit all three keys at once
- **OBS WebSocket integration** — directly toggles the "Mic/Aux" input mute state
- **Auto-reconnect** to OBS if the connection drops

## Requirements

- Python 3.8+
- 88-key digital piano with MIDI output connected via USB
- OBS with WebSocket server enabled (port 4455 by default)
- OBS WebSocket password set

## Setup

### 1. Clone and Install Dependencies

```bash
cd OBSPianoMuteToggle
pip install -r requirements.txt
```

### 2. Configure OBS WebSocket

In OBS:
1. **Tools** → **WebSocket Server Settings**
2. Enable the server (default port 4455)
3. Set a password and copy it
4. Make note of the source/input name for your mic (default: "Mic/Aux")

### 3. Create `.env` File

```bash
cp .env.example .env
```

Then edit `.env` and fill in:

```ini
OBS_PASSWORD=your_password_here
OBS_INPUT_NAME=Mic/Aux           # change if your mic source has a different name
MIDI_PORT=                         # leave blank to auto-detect, or name your port
CHORD_WINDOW_MS=200               # how long (ms) to wait for all 3 notes
COOLDOWN_MS=1000                  # minimum time between toggles
```

**Finding your MIDI port name:**

```bash
python main.py --list-ports
```

This will show all connected MIDI inputs. Copy the exact port name into `.env` if it's not the first one listed.

### 4. Test the Connection

```bash
python main.py
```

You should see:
```
Listening on MIDI port: [your port name]
Target chord: F7+A7+C8 (MIDI [101, 105, 108])
Timing window: 200ms  |  Cooldown: 1000ms
OBS: localhost:4455  |  Input: 'Mic/Aux'
Connected to OBS WebSocket.
```

Press **Ctrl+C** to stop.

## Usage

1. **Start the script:**
   ```bash
   python main.py
   ```

2. **Toggle mic mute:**
   Play the highest F-major triad on your piano (F7, A7, C8 keys). The timing doesn't need to be perfect — as long as all three notes arrive within 200ms, it will detect the chord.

3. **Stop:**
   Press **Ctrl+C** in the terminal.

## MIDI Note Reference

For an 88-key piano (A0 to C8):

| Note | MIDI | Key on Piano |
|------|------|---|
| F7   | 101  | 7th F from the right |
| A7   | 105  | 7th A from the right |
| C8   | 108  | Highest key (rightmost) |

On a standard 88-key piano, these are the three rightmost white keys in the F-major triad.

## Troubleshooting

### "No MIDI input ports found"
- Make sure your piano is connected via USB
- Check your OS device manager or `Audio MIDI Setup` (macOS)

### "Could not connect to OBS"
- Verify OBS is running
- Check that WebSocket server is enabled in OBS settings
- Verify the password in `.env` is correct
- Ensure port 4455 is not blocked by a firewall

### Chord not detecting
- Run `python main.py --list-ports` to verify your piano is connected
- Try increasing `CHORD_WINDOW_MS` in `.env` (e.g., 300ms)
- Make sure you're playing the correct notes (F7, A7, C8)
- Check that the velocity (how hard you press) is above 0 (some pianos require minimum velocity)

### Input name not found in OBS
- In OBS, check the exact name of your microphone input
- It may not be called "Mic/Aux" — it could be "Microphone", "Mic", etc.
- Update `OBS_INPUT_NAME` in `.env` to match exactly

## Configuration Options

| Option | Default | Description |
|--------|---------|---|
| `OBS_HOST` | `localhost` | OBS WebSocket server address |
| `OBS_PORT` | `4455` | OBS WebSocket server port |
| `OBS_PASSWORD` | (empty) | OBS WebSocket password |
| `OBS_INPUT_NAME` | `Mic/Aux` | Name of the mic input to toggle |
| `MIDI_PORT` | (auto) | MIDI input port name; blank = first available |
| `CHORD_WINDOW_MS` | `200` | Time window (ms) for detecting the chord |
| `COOLDOWN_MS` | `1000` | Minimum time (ms) between successive toggles |

## License

MIT
