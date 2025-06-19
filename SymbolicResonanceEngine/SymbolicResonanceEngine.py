import numpy as np
import sounddevice as sd
import threading
import time
from datetime import datetime

# === THEMATIC PATTERNS WITH SYMBOLIC CONFIG ===
harmonic_patterns = {
    "awakening": {
        "frequencies": [111, 222, 369],
        "config": dict(amplitude=0.369, mod_freq=3.0, fade_time=9.0, hold_duration=18.0)
    },
    "healing": {
        "frequencies": [417, 432, 528],
        "config": dict(amplitude=0.432, mod_freq=6.0, fade_time=12.96, hold_duration=43.2)
    },
    "power": {
        "frequencies": [777, 888, 963],
        "config": dict(amplitude=0.777, mod_freq=7.77, fade_time=14.4, hold_duration=28.8)
    },
    "return": {
        "frequencies": [369, 528, 888],
        "config": dict(amplitude=0.528, mod_freq=3.0, fade_time=10.0, hold_duration=21.0)
    },
    "master_33": {
        "frequencies": [111, 528, 963],
        "config": dict(amplitude=0.33, mod_freq=3.3, fade_time=11.0, hold_duration=33.0)
    }
}

# === USER MENU SELECTION ===
def select_pattern():
    print("🌐 Select a Resonator Pattern:")
    for i, key in enumerate(harmonic_patterns.keys(), start=1):
        print(f"{i}. {key}")
    while True:
        try:
            choice = int(input("\nEnter the number of your choice: "))
            pattern_keys = list(harmonic_patterns.keys())
            if 1 <= choice <= len(pattern_keys):
                return pattern_keys[choice - 1]
            else:
                print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# === SETUP BASED ON SELECTION ===
active_pattern_name = select_pattern()
active_pattern = harmonic_patterns[active_pattern_name]
frequencies = active_pattern["frequencies"]
config = active_pattern["config"]

# === AUDIO CONFIGURATION ===
sample_rate = 44100
amplitude = config["amplitude"]
mod_freq = config["mod_freq"]
fade_time = config["fade_time"]
hold_duration = config["hold_duration"]

# === AUDIO STATE ===
current_freq = frequencies[0]
target_freq = frequencies[0]
pattern_index = 0
phase = 0.0
mod_phase = 0.0
should_run = True

# === LOGGING FUNCTION ===
def log_transition(pattern_name, freq, config):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] Pattern: {pattern_name.upper()} | Frequency: {freq} Hz")
    print(f"   → Amplitude: {config['amplitude']}")
    print(f"   → Modulation Frequency: {config['mod_freq']} Hz")
    print(f"   → Fade Time: {config['fade_time']} s")
    print(f"   → Hold Duration: {config['hold_duration']} s\n")

# === AUDIO CALLBACK FOR CLEAN REAL-TIME STREAMING ===
def audio_callback(outdata, frames, time_info, status):
    global phase, mod_phase, current_freq, target_freq

    freq_diff = target_freq - current_freq
    freq_step = freq_diff / (sample_rate * fade_time)
    max_step = 1.0 / sample_rate  # limit frequency stepping

    left = np.zeros(frames)
    right = np.zeros(frames)

    for i in range(frames):
        # Smooth frequency step limit
        freq_step = np.clip(freq_step, -max_step, max_step)
        current_freq += freq_step

        # Smoothed amplitude modulation
        mod = 0.75 + 0.25 * np.sin(2 * np.pi * mod_freq * mod_phase)

        # Stereo output with slight binaural offset
        left[i] = amplitude * mod * np.sin(2 * np.pi * current_freq * phase)
        right[i] = amplitude * mod * np.sin(2 * np.pi * (current_freq + 0.05) * phase)

        # Continuous phase accumulation (no wrap)
        phase += 1 / sample_rate
        mod_phase += 1 / sample_rate

    outdata[:] = np.column_stack((left, right))

# === PATTERN CYCLE THREAD ===
def pattern_control():
    global pattern_index, target_freq, amplitude, mod_freq, fade_time, hold_duration
    while should_run:
        freq = frequencies[pattern_index]
        target_freq = freq
        log_transition(active_pattern_name, freq, config)

        amplitude = config["amplitude"]
        mod_freq = config["mod_freq"]
        fade_time = config["fade_time"]
        hold_duration = config["hold_duration"]

        pattern_index = (pattern_index + 1) % len(frequencies)
        time.sleep(hold_duration)

# === MAIN LOOP ===
def main():
    global should_run
    print(f"\n🔊 Starting symbolic resonance engine in pattern: {active_pattern_name.upper()}...\n")

    stream = sd.OutputStream(callback=audio_callback, samplerate=sample_rate, channels=2)
    stream.start()

    thread = threading.Thread(target=pattern_control, daemon=True)
    thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        should_run = False
        stream.stop()
        stream.close()

if __name__ == "__main__":
    main()
