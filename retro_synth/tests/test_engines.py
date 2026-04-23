import numpy as np
from retro_synth.synth.mixer import HybridEngine
from retro_synth.engine.commands import CommandBus

def test_hybrid_engine():
    bus = CommandBus()
    engine = HybridEngine(sr=48000)

    # Send commands
    patch = {"algorithm": 0, "operators": [{"mul": 1.0}]}
    engine.apply_command(("fm_note_on", 60, 100, patch))

    sample_data = np.random.rand(1000) * 2 - 1
    engine.apply_command(("load_sample", "noise_drum", sample_data))
    engine.apply_command(("pcm_trigger", "noise_drum", 60, 100))

    table = np.sin(np.linspace(0, 2*np.pi, 2048, endpoint=False))
    engine.apply_command(("wt_note_on", 60, 100, table))

    # Render
    buf = np.zeros((128, 2), dtype=np.float32)
    engine.render_into(buf)

    assert np.any(buf != 0.0), "Buffer should contain synthesized audio"
    print("Hybrid engine render test passed.")

if __name__ == "__main__":
    test_hybrid_engine()
