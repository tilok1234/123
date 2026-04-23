import numpy as np
import threading

class RingBuffer:
    def __init__(self, channels: int = 2, capacity_frames: int = 4096):
        self.channels = channels
        self.capacity = capacity_frames
        self.buffer = np.zeros((self.capacity, self.channels), dtype=np.float32)
        self.read_pos = 0
        self.write_pos = 0
        self.size = 0
        self.lock = threading.Lock()

    def write(self, data: np.ndarray) -> int:
        frames = data.shape[0]
        with self.lock:
            free_space = self.capacity - self.size
            if frames > free_space:
                frames = free_space # don't overflow
            if frames == 0:
                return 0

            end_idx = (self.write_pos + frames) % self.capacity
            if end_idx > self.write_pos:
                self.buffer[self.write_pos:end_idx] = data[:frames]
            else:
                part1 = self.capacity - self.write_pos
                self.buffer[self.write_pos:] = data[:part1]
                self.buffer[:end_idx] = data[part1:frames]

            self.write_pos = end_idx
            self.size += frames
            return frames

    def read_into(self, outdata: np.ndarray) -> int:
        frames = outdata.shape[0]
        with self.lock:
            if frames > self.size:
                frames = self.size # don't underflow
            if frames == 0:
                return 0

            end_idx = (self.read_pos + frames) % self.capacity
            if end_idx > self.read_pos:
                outdata[:frames] = self.buffer[self.read_pos:end_idx]
            else:
                part1 = self.capacity - self.read_pos
                outdata[:part1] = self.buffer[self.read_pos:]
                outdata[part1:frames] = self.buffer[:end_idx]

            self.read_pos = end_idx
            self.size -= frames
            return frames

    def available_frames(self) -> int:
        with self.lock:
            return self.size

    def free_frames(self) -> int:
         with self.lock:
             return self.capacity - self.size
