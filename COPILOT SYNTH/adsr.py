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
        self.previous_amplitude = 0.0
        self.smoothing = 0.99  # Increased smoothing
        self.min_time = 0.001  # Minimum time for transitions
        self.last_update = time.time()

    def trigger(self):
        self.state = 'attack'
        self.start_time = time.time()

    def release_note(self):  # Changed this line
        self.state = 'release'
        self.start_time = time.time()

    def is_active(self):
        return self.state != 'idle'

    def get_amplitude(self):
        if not self.is_active():
            return 0.0
            
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        elapsed_time = current_time - self.start_time
        target = 0.0
        
        # Ensure minimum times for each stage
        attack = max(self.attack, self.min_time)
        decay = max(self.decay, self.min_time)
        release = max(self.release, self.min_time)
        
        if self.state == 'attack':
            target = min(elapsed_time / attack, 1.0)
            if elapsed_time >= attack:
                self.state = 'decay'
                self.start_time = current_time
                
        elif self.state == 'decay':
            target = 1.0 - (1.0 - self.sustain) * (min(elapsed_time / decay, 1.0))
            if elapsed_time >= decay:
                self.state = 'sustain'
                
        elif self.state == 'sustain':
            target = self.sustain
            
        elif self.state == 'release':
            target = self.sustain * (1.0 - min(elapsed_time / release, 1.0))
            if elapsed_time >= release:
                self.state = 'idle'
                
        # Time-based smoothing
        smooth_factor = np.exp(-dt / 0.005)  # 5ms smoothing time constant
        self.amplitude = smooth_factor * self.previous_amplitude + (1 - smooth_factor) * target
        self.previous_amplitude = self.amplitude
        
        return self.amplitude
