import json

class Synth(object):
    """The wave channel can be used as a soft synthesizer to generate sounds."""
    def __init__(self, song, index):
        self.waves = song.song_data.wave_frames[index]
        self._params = song.song_data.softsynth_params[index]
        self.index = index

    def __getattr__(self, name):
        if name in ("_params", "index", "waves"):
            return super(Synth, self).__getattr__(name)
        else:
            return getattr(self._params, name)

    def __setattr__(self, name, value):
        if name in ("_params", "index", "waves"):
            super(Synth, self).__setattr__(name, value)
        else:
            setattr(self._params, name, value)

    def export(self):
        export_struct = {}

        export_struct["params"] = json.loads(self._params.as_json())
        export_struct["waves"] = []

        for wave in self.waves:
            export_struct["waves"].append(list(wave))

        return export_struct

    def import_lsdinst(self, synth_data):
        params_native = self._params.as_native()

        for key in params_native:
            if key[0] == '_':
                continue

            if key in ('start', 'end'):
                self._import_sound_params(
                    synth_data['params'][key], getattr(self, key))
            else:
                setattr(self._params, key, synth_data['params'][key])

        for i, wave in enumerate(synth_data['waves']):
            for j, frame in enumerate(wave):
                self.waves[i][j] = frame

    def _import_sound_params(self, params, dest):
        native_repr = dest.as_native()

        for key in native_repr:
            if key[0] == '_':
                continue

            setattr(dest, key, params[key])
