import numpy as np
import keyboard
import sounddevice as sd  # Add this import

class Oscillator:
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.phase_accumulators = {}

    def generate_sine_wave(self, freq, t, note, vel, envelope):
        if note not in self.phase_accumulators:
            self.phase_accumulators[note] = 0
        phase = self.phase_accumulators[note]
        sine_wave = np.sin(2 * np.pi * freq * t + phase) * vel * 0.5 * envelope
        self.phase_accumulators[note] += 2 * np.pi * freq * len(t) / self.sample_rate
        self.phase_accumulators[note] %= 2 * np.pi  # Keep phase within 0 to 2*pi
        return sine_wave

    def remove_note_phase(self, note):
        if note in self.phase_accumulators:
            del self.phase_accumulators[note]

    def stop(self):
        self.phase_accumulators.clear()

    def play_sine_wave(self, freq, duration):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        sine_wave = self.generate_sine_wave(freq, t, 'C', 1, 1)
        sd.play(sine_wave, self.sample_rate)
        sd.wait()

oscillator = Oscillator(sample_rate=44100)

# Play a continuous C note (MIDI note 60) for 5 seconds
oscillator.play_sine_wave(261.63, 5)

def stop_oscillator():
    oscillator.stop()

def on_key_event(event):
    if event.event_type == 'down':
        # Generate sound for the key press
        # ...code to generate sound...
    elif event.event_type == 'up':
        # Stop sound for the key release
        stop_oscillator()

keyboard.hook(on_key_event)


