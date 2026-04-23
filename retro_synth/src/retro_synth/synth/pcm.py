import numpy as np

class PCMVoice:
    def __init__(self, sr=48000):
        self.sr = sr
        self.active = False
        self.sample_data = None
        self.pos = 0.0
        self.pitch_ratio = 1.0
        self.note = None

    def trigger(self, sample_data: np.ndarray, note: int, base_note: int = 60):
        self.active = True
        self.sample_data = sample_data
        self.pos = 0.0
        self.note = note
        self.pitch_ratio = 2.0 ** ((note - base_note) / 12.0)

    def render(self, frames: int) -> np.ndarray:
        if not self.active or self.sample_data is None:
            return np.zeros(frames)

        out = np.zeros(frames)
        for i in range(frames):
            if int(self.pos) >= len(self.sample_data):
                self.active = False
                break

            # Simple nearest neighbor interpolation
            idx = int(self.pos)
            out[i] = self.sample_data[idx]
            self.pos += self.pitch_ratio

        return out

class PCMEngine:
    def __init__(self, max_voices=16, sr=48000):
        self.voices = [PCMVoice(sr) for _ in range(max_voices)]
        self.samples = {} # id -> numpy array

    def load_sample(self, sample_id: str, data: np.ndarray):
        self.samples[sample_id] = data

    def trigger(self, sample_id: str, note: int, vel: int):
        if sample_id not in self.samples:
            return

        for voice in self.voices:
            if not voice.active:
                voice.trigger(self.samples[sample_id], note)
                break

    def render_into(self, buf: np.ndarray):
        frames = buf.shape[0]
        mixed = np.zeros(frames)
        for voice in self.voices:
            if voice.active:
                mixed += voice.render(frames)
        buf[:, 0] += mixed
        buf[:, 1] += mixed
