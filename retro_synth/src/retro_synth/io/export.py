import numpy as np
import soundfile as sf
from retro_synth.synth.mixer import HybridEngine
from retro_synth.engine.sequencer import Sequencer
from retro_synth.engine.commands import CommandBus
from retro_synth.io.project import ProjectModel

def export_wav(project: ProjectModel, output_path: str, sr: int = 48000, bit_depth: int = 16):
    bus = CommandBus()
    engine = HybridEngine(sr=sr)
    sequencer = Sequencer(bus, sr=sr)
    sequencer.set_project(project)

    # Pre-calculate exact number of samples based on orders and patterns length
    # For offline render, we'll just render until sequencer stops playing
    sequencer.play()

    chunk_size = 4096
    frames = []
    max_duration_seconds = 600 # safety limit 10 mins
    max_chunks = (sr * max_duration_seconds) // chunk_size

    scratch = np.zeros((chunk_size, 2), dtype=np.float32)

    for _ in range(max_chunks):
        if not sequencer.playing:
            # Let the final envelopes decay slightly
            for i in range(sr // chunk_size):
                scratch.fill(0.0)
                engine.render_into(scratch)
                frames.append(scratch.copy())
            break

        while not bus.empty():
            cmd = bus.get_nowait()
            engine.apply_command(cmd)

        scratch.fill(0.0)
        sequencer.advance(chunk_size)
        engine.render_into(scratch)
        frames.append(scratch.copy())

    if not frames:
        return

    audio_data = np.concatenate(frames, axis=0)

    # Save as 16-bit PCM WAV
    subtype = 'PCM_16' if bit_depth == 16 else 'PCM_24'
    sf.write(output_path, audio_data, sr, subtype=subtype)
