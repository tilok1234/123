import numpy as np
import sounddevice as sd

class AudioBackend:
    def __init__(self, ringbuffer):
        self.ringbuffer = ringbuffer
        self.xruns = 0
        self.stream = None

    def callback(self, outdata: np.ndarray, frames: int, time_info, status) -> None:
        if status:
            self.xruns += 1

        written = self.ringbuffer.read_into(outdata)
        if written < frames:
            outdata[written:frames].fill(0.0)  # underrun protection

    def start(self, samplerate: int = 48000, device=None) -> sd.OutputStream:
        self.stream = sd.OutputStream(
            samplerate=samplerate,
            channels=self.ringbuffer.channels,
            dtype="float32",
            latency="low",
            blocksize=0,
            device=device,
            callback=self.callback,
        )
        self.stream.start()
        return self.stream

    def stop(self) -> None:
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
