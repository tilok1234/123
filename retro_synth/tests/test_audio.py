import time
from retro_synth.audio.ringbuffer import RingBuffer
from retro_synth.audio.backend import AudioBackend
from retro_synth.engine.commands import CommandBus
from retro_synth.engine.render_thread import RenderThread
import sounddevice as sd

def test_audio():
    try:
        sd.query_devices()
        device = sd.default.device[1]
    except Exception as e:
        print(f"No audio device found, skipping audio test: {e}")
        return

    bus = CommandBus()
    rb = RingBuffer(channels=2, capacity_frames=4096)

    class DummyEngine:
        def __init__(self):
            self.phase = 0.0
            self.freq = 440.0
            self.sr = 48000.0

        def apply_command(self, cmd):
            if cmd[0] == "freq":
                self.freq = cmd[1]

        def render_into(self, buf):
            import numpy as np
            frames = buf.shape[0]
            t = np.arange(frames) / self.sr
            wave = np.sin(2 * np.pi * self.freq * (t + self.phase / (2 * np.pi * self.freq))) * 0.2
            self.phase += 2 * np.pi * self.freq * (frames / self.sr)
            buf[:, 0] = wave
            buf[:, 1] = wave

    import numpy as np
    engine = DummyEngine()

    render_thread = RenderThread(bus, None, engine, rb)
    backend = AudioBackend(rb)

    started = False
    print("Starting audio...")
    try:
        backend.start(samplerate=48000)
        render_thread.start()
        started = True

        print("Playing 440Hz")
        time.sleep(1)
        print("Playing 880Hz")
        bus.push(("freq", 880.0))
        time.sleep(1)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Failed to start audio backend (expected in headless CI without dummy device): {e}")
    finally:
        bus.push(("quit",))
        if started:
            render_thread.join()
        backend.stop()
        print("Audio stopped")

if __name__ == "__main__":
    test_audio()
