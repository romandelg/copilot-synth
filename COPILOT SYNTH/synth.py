import mido
import time
import pygame
import pygame.midi
import numpy as np
import pygame._sdl2.audio as sdl2_audio
from adsr import ADSR  # Changed this line

class SimpleSynth:
    def __init__(self, sample_rate=44100, buffer_size=2048):  # Increased buffer size
        pygame.mixer.init(sample_rate, -16, 2, buffer_size)
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.active_notes = {}
        self.envelopes = {}
        self.time_index = 0
        self.poll_interval = buffer_size / sample_rate
        self.adsr_params = {'attack': 0.01, 'decay': 0.1, 'sustain': 0.7, 'release': 0.2}
        self.adsr_enabled = True  # Add this line
        # Initialize with silence
        self.current_sound = pygame.sndarray.make_sound(
            np.zeros((self.buffer_size, 2), dtype=np.int16))
        self.current_sound.play(-1)  # Start playing immediately and loop
        
    def generate_audio_buffer(self):
        if not self.active_notes:
            return np.zeros((self.buffer_size, 2), dtype=np.int16)
        
        t = np.linspace(self.time_index, 
                       self.time_index + self.buffer_size/self.sample_rate,
                       self.buffer_size, False)
        
        mixed_audio = np.zeros(len(t))
        # Process each active note with its envelope
        for note, (freq, vel) in list(self.active_notes.items()):
            if note in self.envelopes:
                env = self.envelopes[note]
                if env.is_active():
                    envelope = env.get_amplitude() if self.adsr_enabled else 1  # Modify this line
                    sine_wave = np.sin(2 * np.pi * freq * t) * vel * 0.5 * envelope
                    mixed_audio += sine_wave
                else:
                    del self.active_notes[note]
                    del self.envelopes[note]
        
        # Normalize and convert to stereo
        mixed_audio = np.clip(mixed_audio, -1, 1)
        stereo = np.tile(mixed_audio, (2, 1)).T
        samples = (stereo * 32767).astype(np.int16)
        self.time_index += self.buffer_size/self.sample_rate
        
        return samples

    def note_on(self, note, velocity):
        freq = 440 * (2 ** ((note - 69) / 12.0))
        self.active_notes[note] = (freq, velocity / 127.0)
        # Create and trigger new envelope with current ADSR parameters
        self.envelopes[note] = ADSR(**self.adsr_params)
        self.envelopes[note].trigger()
        self.update_audio()  # Update immediately when a note changes
    
    def note_off(self, note):
        if note in self.active_notes and note in self.envelopes:
            self.envelopes[note].release_note()  # Changed this line
            self.update_audio()  # Update immediately when a note changes
    
    def handle_control_change(self, control, value):
        if control == 14:
            self.adsr_params['attack'] = value / 127.0
            self.print_adsr_param('Attack', value)
        elif control == 15:
            self.adsr_params['decay'] = value / 127.0
            self.print_adsr_param('Decay', value)
        elif control == 16:
            self.adsr_params['sustain'] = value / 127.0
            self.print_adsr_param('Sustain', value)
        elif control == 17:
            self.adsr_params['release'] = value / 127.0
            self.print_adsr_param('Release', value)

    def print_adsr_param(self, param_name, value):
        bar_length = 50
        filled_length = int(bar_length * value / 127)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f"\r{param_name}: |{bar}| {value / 127:.2f}", end="")

    def update_audio(self):
        buffer = self.generate_audio_buffer()
        # Update the currently playing sound buffer
        pygame.sndarray.samples(self.current_sound)[:] = buffer
    
    def toggle_adsr(self):  # Modify this method
        self.adsr_enabled = not self.adsr_enabled
        status = 'enabled' if self.adsr_enabled else 'disabled'
        print(f"\nADSR {status}")

    def cleanup(self):
        self.current_sound.stop()
        self.active_notes.clear()
        self.envelopes.clear()
        pygame.mixer.quit()

def main():
    try:
        # Initialize pygame and MIDI
        pygame.init()
        pygame.midi.init()
        
        # List MIDI devices
        print("\n🎹 === MIDI DEVICE SCANNER ===")
        device_count = pygame.midi.get_count()
        if device_count == 0:
            print("⚠️  No MIDI devices found!")
            return
        
        print(f"Found {device_count} MIDI device(s)")
        print("-" * 50)
        
        # Find first input device
        input_id = None
        for i in range(device_count):
            info = pygame.midi.get_device_info(i)
            if info[2]:  # is_input
                print(f"📌 Device {i}:")
                print(f"   • Name: {info[1].decode()}")
                print(f"   • Interface: {info[0].decode()}")
                print(f"   • Type: MIDI Input")
                print(f"   • Status: Available")
                print("-" * 50)
                if input_id is None:
                    input_id = i
        
        if input_id is None:
            print("⚠️  No MIDI input devices found!")
            return
        
        # Initialize synth and MIDI input
        synth = SimpleSynth()
        midi_input = pygame.midi.Input(input_id)
        
        print("\n✅ === CONNECTION SUCCESSFUL ===")
        print(f"🎹 Active MIDI Input:")
        print(f"   • Device: {pygame.midi.get_device_info(input_id)[1].decode()}")
        print(f"   • Port: {input_id}")
        print(f"   • Status: Ready")
        print("-" * 50)
        
        print("\nListening for MIDI input... (Press Ctrl+C to exit)")
        print("Press 'Ctrl+A' to toggle ADSR")
        print("-" * 50)
        
        # Remove the continuous C note (MIDI note 60)
        # synth.note_on(60, 127)
        
        # Main loop
        last_update = time.time()
        while True:
            current_time = time.time()
            
            # Update audio buffer
            if current_time - last_update >= synth.poll_interval:
                synth.update_audio()
                last_update = current_time
            
            if midi_input.poll():
                events = midi_input.read(10)
                for event in events:
                    status = event[0][0]
                    note = event[0][1]
                    velocity = event[0][2]
                    control = event[0][1]
                    value = event[0][2]
                    
                    if status == 0x90:  # Note On
                        if velocity > 0:
                            print(f"\rPlaying note: {note} velocity: {velocity}   ", end="")
                            synth.note_on(note, velocity)
                        else:
                            print(f"\rStopped note: {note}   ", end="")
                            synth.note_off(note)
                    elif status == 0x80:  # Note Off
                        print(f"\rStopped note: {note}   ", end="")
                        synth.note_off(note)
                    elif status == 0xB0:  # Control Change
                        synth.handle_control_change(control, value)
            
            # Check for key press to toggle ADSR
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        synth.toggle_adsr()
            
            time.sleep(0.001)
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if 'midi_input' in locals():
            midi_input.close()
        if 'synth' in locals():
            synth.cleanup()
        pygame.midi.quit()
        pygame.quit()

if __name__ == "__main__":
    main()