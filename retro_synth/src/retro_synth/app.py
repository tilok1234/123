import sys
import argparse
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from retro_synth.gui.main_window import MainWindow
from retro_synth.engine.commands import CommandBus
from retro_synth.audio.ringbuffer import RingBuffer
from retro_synth.audio.backend import AudioBackend
from retro_synth.synth.mixer import HybridEngine
from retro_synth.engine.sequencer import Sequencer
from retro_synth.engine.render_thread import RenderThread
from retro_synth.io.project import ProjectModel
import sounddevice as sd

class AudioAppWrapper:
    def __init__(self, use_audio=True):
        self.bus = CommandBus()
        self.project = ProjectModel()

        self.use_audio = use_audio
        if self.use_audio:
            try:
                sd.query_devices()
            except Exception as e:
                print(f"Disabling audio, no devices: {e}")
                self.use_audio = False

        if self.use_audio:
            self.rb = RingBuffer(channels=2, capacity_frames=4096)
            self.engine = HybridEngine(sr=48000)
            self.sequencer = Sequencer(self.bus, sr=48000)
            self.sequencer.set_project(self.project)

            self.backend = AudioBackend(self.rb)
            self.render_thread = RenderThread(self.bus, self.sequencer, self.engine, self.rb)

    def start(self):
        if self.use_audio:
            self.backend.start(samplerate=48000)
            self.render_thread.start()

    def stop(self):
        self.bus.push(("quit",))
        if self.use_audio:
            self.render_thread.join()
            self.backend.stop()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-audio", action="store_true", help="Disable audio backend")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    audio_app = AudioAppWrapper(use_audio=not args.no_audio)
    audio_app.start()

    window = MainWindow(audio_app.bus)
    window.show()

    # Qt Timer to pull commands back to GUI if needed
    def tick():
        # Handle GUI bound messages here if any
        pass
    timer = QTimer()
    timer.timeout.connect(tick)
    timer.start(16) # ~60fps

    ret = app.exec()

    audio_app.stop()
    sys.exit(ret)

if __name__ == "__main__":
    main()
