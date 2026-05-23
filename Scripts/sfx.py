class SoundMixer:

    def __init__(self, assets):
        self.assets = assets
        self.playing = []

    def play(self, s_type, variant=0, loop=-1, vol=1.0):
        if isinstance(variant, str):
            sound = self.assets[s_type][variant][0]  # each variant is stored as a list of sounds
        else:
            sound = self.assets[s_type][variant]
        sound.play(loop)
        sound.set_volume(vol)
        self.playing.append([s_type, variant])

    def check(self):
        if self.playing:
            if self.assets[self.playing[0][0]][self.playing[0][1]]:
                temp = self.playing[0]
                self.playing.pop()
                return temp
        return []
    
    def stop(self, s_type='', variant=0, stop_all=False):
        if stop_all:
            if s_type != '':
                sfx = self.assets[s_type]
                for key in sfx:
                    for sound in sfx[key]:
                        sound.stop()
            else:
                for sound_type in self.assets:
                    sfx = self.assets[sound_type]
                    for key in sfx:
                        for sound in sfx[key]:
                            sound.stop()
        else:
            if isinstance(variant, str):
                self.assets[s_type][variant][0].stop()
            else:
                self.assets[s_type][variant].stop()