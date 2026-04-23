import numpy as np

class WavetableVoice:
    def __init__(self, sr=48000):
        self.sr = sr
        self.active = False
        self.table = None
        self.pos = 0.0
        self.note = None
        self.freq = 440.0

    def note_on(self, note: int, table: np.ndarray):
        self.active = True
        self.note = note
        self.table = table
        self.freq = 440.0 * (2.0 ** ((note - 69.0) / 12.0))

    def note_off(self):
        self.active = False

    def render(self, frames: int) -> np.ndarray:
        if not self.active or self.table is None:
            return np.zeros(frames)

        out = np.zeros(frames)
        table_len = len(self.table)
        step = table_len * self.freq / self.sr

        for i in range(frames):
            idx = int(self.pos) % table_len
            next_idx = (idx + 1) % table_len
            frac = self.pos - int(self.pos)

            # Linear interpolation
            out[i] = self.table[idx] * (1 - frac) + self.table[next_idx] * frac

            self.pos += step

        return out * 0.2

class WavetableEngine:
    def __init__(self, max_voices=8, sr=48000):
        self.voices = [WavetableVoice(sr) for _ in range(max_voices)]

    def note_on(self, note: int, vel: int, table: np.ndarray):
        for voice in self.voices:
            if not voice.active:
                voice.note_on(note, table)
                break

    def note_off(self, note: int):
        for voice in self.voices:
            if voice.active and voice.note == note:
                voice.note_off()

    def render_into(self, buf: np.ndarray):
        frames = buf.shape[0]
        mixed = np.zeros(frames)
        for voice in self.voices:
            if voice.active:
                mixed += voice.render(frames)
        buf[:, 0] += mixed
        buf[:, 1] += mixed
