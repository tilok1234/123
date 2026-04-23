import numpy as np
from typing import Dict, Any

class Operator:
    def __init__(self, sr=48000):
        self.sr = sr
        self.phase = 0.0
        self.freq = 0.0
        self.mul = 1.0

    def render(self, frames: int, freq_mod: np.ndarray = None) -> np.ndarray:
        t = np.arange(frames) / self.sr
        base_freq = self.freq * self.mul

        if freq_mod is None:
            phase_inc = 2 * np.pi * base_freq * t
        else:
            phase_inc = 2 * np.pi * base_freq * t + freq_mod

        wave = np.sin(phase_inc + self.phase)
        self.phase += 2 * np.pi * base_freq * (frames / self.sr)
        return wave

class FM4OpVoice:
    def __init__(self, sr=48000):
        self.sr = sr
        self.ops = [Operator(sr) for _ in range(4)]
        self.active = False
        self.note = None
        self.algorithm = 0

    def note_on(self, note: int, patch: Dict[str, Any]):
        self.active = True
        self.note = note
        self.algorithm = patch.get("algorithm", 0)
        freq = 440.0 * (2.0 ** ((note - 69.0) / 12.0))

        ops_data = patch.get("operators", [])
        for i in range(4):
            self.ops[i].freq = freq
            if i < len(ops_data):
                self.ops[i].mul = ops_data[i].get("mul", 1.0)

    def note_off(self):
        self.active = False
        self.note = None

    def render(self, frames: int) -> np.ndarray:
        if not self.active:
            return np.zeros(frames)

        # Simplified Algorithm 0: Op1 -> Op2 -> Op3 -> Op4
        if self.algorithm == 0:
            out1 = self.ops[0].render(frames)
            out2 = self.ops[1].render(frames, out1 * 2.0)
            out3 = self.ops[2].render(frames, out2 * 2.0)
            out4 = self.ops[3].render(frames, out3 * 2.0)
            return out4 * 0.25
        # Simplified Algorithm 4: (Op1, Op2) -> Op3 -> Op4
        elif self.algorithm == 4:
            out1 = self.ops[0].render(frames)
            out2 = self.ops[1].render(frames)
            out3 = self.ops[2].render(frames, (out1 + out2) * 2.0)
            out4 = self.ops[3].render(frames, out3 * 2.0)
            return out4 * 0.25
        # Fallback parallel
        else:
            out1 = self.ops[0].render(frames)
            out2 = self.ops[1].render(frames)
            out3 = self.ops[2].render(frames)
            out4 = self.ops[3].render(frames)
            return (out1 + out2 + out3 + out4) * 0.1

class FM4OpEngine:
    def __init__(self, max_voices=16, sr=48000):
        self.voices = [FM4OpVoice(sr) for _ in range(max_voices)]

    def note_on(self, note: int, vel: int, patch: Dict[str, Any]):
        for voice in self.voices:
            if not voice.active:
                voice.note_on(note, patch)
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
