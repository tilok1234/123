import numpy as np
from retro_synth.synth.fm4op import FM4OpEngine
from retro_synth.synth.pcm import PCMEngine
from retro_synth.synth.wavetable import WavetableEngine

class HybridEngine:
    def __init__(self, sr=48000):
        self.fm = FM4OpEngine(sr=sr)
        self.pcm = PCMEngine(sr=sr)
        self.wavetable = WavetableEngine(sr=sr)
        self.master_vol = 0.8

    def apply_command(self, cmd: tuple):
        if cmd[0] == "fm_note_on":
            self.fm.note_on(cmd[1], cmd[2], cmd[3])
        elif cmd[0] == "fm_note_off":
            self.fm.note_off(cmd[1])
        elif cmd[0] == "pcm_trigger":
            self.pcm.trigger(cmd[1], cmd[2], cmd[3])
        elif cmd[0] == "wt_note_on":
            self.wavetable.note_on(cmd[1], cmd[2], cmd[3])
        elif cmd[0] == "wt_note_off":
            self.wavetable.note_off(cmd[1])
        elif cmd[0] == "load_sample":
            self.pcm.load_sample(cmd[1], cmd[2])

    def render_into(self, buf: np.ndarray):
        buf.fill(0.0)
        self.fm.render_into(buf)
        self.pcm.render_into(buf)
        self.wavetable.render_into(buf)
        buf *= self.master_vol

        # Soft clipping
        np.clip(buf, -1.0, 1.0, out=buf)
