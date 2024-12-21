import numpy as np
import time

class ADSR:
    def __init__(self, attack, decay, sustain, release):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.state = 'idle'
        self.amplitude = 0.0
        self.start_time = None

    def trigger(self):
        self.state = 'attack'
        self.start_time = time.time()

    def release_note(self):  # Changed this line
        self.state = 'release'
        self.start_time = time.time()

    def is_active(self):
        return self.state != 'idle'

    def get_amplitude(self):
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        if self.state == 'attack':
            if elapsed_time < self.attack:
                self.amplitude = elapsed_time / self.attack
            else:
                self.state = 'decay'
                self.start_time = current_time
                self.amplitude = 1.0

        if self.state == 'decay':
            if elapsed_time < self.decay:
                self.amplitude = 1.0 - (1.0 - self.sustain) * (elapsed_time / self.decay)
            else:
                self.state = 'sustain'
                self.amplitude = self.sustain

        if self.state == 'sustain':
            self.amplitude = self.sustain

        if self.state == 'release':
            if elapsed_time < self.release:
                self.amplitude = self.sustain * (1.0 - elapsed_time / self.release)
            else:
                self.state = 'idle'
                self.amplitude = 0.0

        return self.amplitude
