import threading
import time
import numpy as np

class RenderThread(threading.Thread):
    def __init__(self, command_bus, sequencer, engine, ringbuffer, quantum=128, preroll_blocks=4):
        super().__init__(daemon=True)
        self.command_bus = command_bus
        self.sequencer = sequencer
        self.engine = engine
        self.ringbuffer = ringbuffer
        self.quantum = quantum
        self.preroll_blocks = preroll_blocks
        self.running = True

    def run(self) -> None:
        scratch = np.zeros((self.quantum, self.ringbuffer.channels), dtype=np.float32)

        while self.running:
            while not self.command_bus.empty():
                cmd = self.command_bus.get_nowait()
                if cmd[0] == "quit":
                    self.running = False
                    return
                if self.engine:
                    self.engine.apply_command(cmd)

            target_frames = self.preroll_blocks * self.quantum

            while self.ringbuffer.free_frames() > self.quantum and self.ringbuffer.available_frames() < target_frames:
                if self.sequencer:
                    self.sequencer.advance(self.quantum)
                if self.engine:
                    self.engine.render_into(scratch)
                else:
                     # just fill with noise if no engine
                     scratch[:] = (np.random.rand(self.quantum, self.ringbuffer.channels) * 2 - 1) * 0.1
                self.ringbuffer.write(scratch)

            time.sleep(0.001)
