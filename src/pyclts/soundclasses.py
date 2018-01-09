# coding: utf-8
from __future__ import unicode_literals
from functools import partial

from collections import defaultdict

from pyclts.util import pkg_path
from pyclts.transcriptionsystem import Sound, TranscriptionSystem
from pyclts.transcriptiondata import iterdata

def lingpy(sound_class):
    out = {}
    graphemes, names = [], []
    for sound_name, sound_bipa, grapheme in iterdata('lingpy.tsv', sound_class,
            folder='soundclasses'):
        out[sound_bipa] = out[sound_name] = grapheme
        graphemes += [sound_bipa]
        names += [sound_name]
    return out, graphemes, names


class SoundClasses(object):
    """
    Class for handling sound class models.
    """
    def __init__(self, data='sca', system=None):
        self.data, self.sounds, self.names = {
            "sca": lambda: lingpy('SCA_CLASS'),
            "dolgo": lambda: lingpy('DOLGOPOLSKY_CLASS'),
            "cv": lambda: lingpy('CV_CLASS'),
            "prosody": lambda: lingpy('PROSODY_CLASS'),
            "asjp": lambda: lingpy('ASJP_CLASS'),
            "color": lambda: lingpy('COLOR_CLASS'),
        }[data]()
        self.id = data
        self.system = system or TranscriptionSystem()
        # we want to know whether data type is lingpy, as in this case, we want
        # to resolve the mappings

    def resolve_sound(self, sound):
        """Function tries to identify a sound in the data.

        Notes
        -----
        The function tries to resolve sounds to take a sound with less complex
        features in order to yield the next approximate sound class, if the
        transcription data are sound classes.
        """
        if sound.name in self.data:
            return self.data[sound.name]['grapheme']
        if not sound.type == 'unknownsound':
            if sound.type in ['diphthong', 'cluster']:
                return self.resolve_sound(sound.from_sound)
            name = [s for s in sound.name.split(' ') if 
                self.system._feature_values.get(s, '') not in [
                    'laminality', 'ejection', 'tone'
                ]]
            while len(name) >= 4:
                sound = self.system.get(' '.join(name))
                if sound and sound.name in self.data:
                    return self.resolve_sound(sound)
                name.pop(0)
        raise KeyError(":sc:resolve_sound: No sound could be found.")

    def __getitem__(self, sound):
        if isinstance(sound, Sound):
            return self.resolve_sound(sound)
        return self.resolve_sound(self.system[sound])
    
    def get(self, sound, default=None):
        try:
            return self[sound]
        except KeyError:
            return default

    def items(self, sound, default=None):
        return self._data.items()

    def __call__(self, sounds, default="0"):
        return [self.get(x, default) for x in sounds.split()]
