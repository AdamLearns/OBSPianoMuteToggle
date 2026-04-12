#!/usr/bin/env python3
"""
OBS Piano Mute Toggle
Detects the highest F-major triad (F7+A7+C8, MIDI 101+105+108) and toggles
the mic mute in OBS via WebSocket.
"""

import argparse
import os
import signal
import sys
import time

import mido
from dotenv import load_dotenv
from obsws_python import ReqClient

load_dotenv()

OBS_HOST = os.getenv("OBS_HOST", "localhost")
OBS_PORT = int(os.getenv("OBS_PORT", "4455"))
OBS_PASSWORD = os.getenv("OBS_PASSWORD", "")
OBS_INPUT_NAME = os.getenv("OBS_INPUT_NAME", "Mic/Aux")
MIDI_PORT = os.getenv("MIDI_PORT", "").strip()
CHORD_WINDOW = float(os.getenv("CHORD_WINDOW_MS", "200")) / 1000.0
COOLDOWN = float(os.getenv("COOLDOWN_MS", "1000")) / 1000.0

# Highest F-major triad in root position on an 88-key piano: F7, A7, C8
TARGET = {101, 105, 108}

note_times: dict[int, float] = {}
last_trigger: list[float] = [0.0]
obs_client: ReqClient | None = None


def connect_obs() -> ReqClient:
    return ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD)


def toggle_mute() -> None:
    global obs_client
    try:
        if obs_client is None:
            obs_client = connect_obs()
        obs_client.toggle_input_mute(name=OBS_INPUT_NAME)
        mute_status = obs_client.get_input_mute(name=OBS_INPUT_NAME)
        state = "muted" if mute_status.input_muted else "unmuted"
        print(f"Toggled: {OBS_INPUT_NAME} is now {state}")
    except Exception as e:
        print(f"OBS error: {e} — reconnecting next attempt")
        obs_client = None


def handle_midi(msg: mido.Message) -> None:
    now = time.monotonic()

    if msg.type == "note_on" and msg.velocity > 0:
        note_times[msg.note] = now
    elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
        note_times.pop(msg.note, None)

    # Prune notes outside the timing window
    cutoff = now - CHORD_WINDOW
    stale = [n for n, t in note_times.items() if t < cutoff]
    for n in stale:
        del note_times[n]

    # Trigger if all target notes are active within the window
    if TARGET.issubset(note_times):
        if now - last_trigger[0] >= COOLDOWN:
            last_trigger[0] = now
            toggle_mute()


def list_ports() -> None:
    ports = mido.get_input_names()
    if not ports:
        print("No MIDI input ports found.")
    else:
        print("Available MIDI input ports:")
        for i, name in enumerate(ports):
            print(f"  [{i}] {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Toggle OBS mic mute via piano chord.")
    parser.add_argument("--list-ports", action="store_true", help="List MIDI input ports and exit")
    args = parser.parse_args()

    if args.list_ports:
        list_ports()
        return

    ports = mido.get_input_names()
    if not ports:
        print("Error: No MIDI input ports found. Is your piano connected?")
        sys.exit(1)

    port_name = MIDI_PORT if MIDI_PORT else ports[0]
    if port_name not in ports:
        print(f"Error: MIDI port '{port_name}' not found. Available ports:")
        for p in ports:
            print(f"  {p}")
        sys.exit(1)

    print(f"Listening on MIDI port: {port_name}")
    print(f"Target chord: F7+A7+C8 (MIDI {sorted(TARGET)})")
    print(f"Timing window: {CHORD_WINDOW * 1000:.0f}ms  |  Cooldown: {COOLDOWN * 1000:.0f}ms")
    print(f"OBS: {OBS_HOST}:{OBS_PORT}  |  Input: '{OBS_INPUT_NAME}'")
    print("Press Ctrl+C to quit.\n")

    # Pre-connect to OBS so the first toggle is fast
    global obs_client
    try:
        obs_client = connect_obs()
        print("Connected to OBS WebSocket.")
        print("Don't forget to disable auto-lock on the iPad (for chat) and turn on Focus Mode (DND)!")
    except Exception as e:
        print(f"Warning: Could not connect to OBS ({e}). Will retry on first trigger.")

    with mido.open_input(port_name, callback=handle_midi):
        signal.pause()


if __name__ == "__main__":
    main()
