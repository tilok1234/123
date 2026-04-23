import os
from retro_synth.io.project import ProjectModel
from retro_synth.io.export import export_wav

def test_export():
    proj = ProjectModel()
    proj.orders = [0]
    proj.instruments["bass_fm"] = {
        "version": 1,
        "engine": "fm4op",
        "name": "Bass FM",
        "algorithm": 0,
        "operators": [{"mul": 1.0}]
    }
    proj.patterns["pattern_00"] = {
        "rows": 16,
        "channels": 8,
        "events": [
            {"row": 0, "ch": 0, "note": "C-4", "inst": "bass_fm", "vol": 100},
            {"row": 8, "ch": 0, "note": "G-4", "inst": "bass_fm", "vol": 100}
        ]
    }

    output_path = "test_export.wav"
    export_wav(proj, output_path)

    assert os.path.exists(output_path), "WAV file was not created"

    import soundfile as sf
    data, sr = sf.read(output_path)
    assert sr == 48000
    assert len(data.shape) == 2 # Stereo
    assert data.shape[1] == 2

    os.remove(output_path)
    print("Export WAV test passed.")

if __name__ == "__main__":
    test_export()
