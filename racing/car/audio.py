from collections import namedtuple
from panda3d.core import AudioSound
from yyagl.gameobject import Audio


CarSounds = namedtuple('CarSounds', 'engine brake crash crash_hs lap landing')


class CarAudio(Audio):

    def __init__(self, mdt, props):
        Audio.__init__(self, mdt)
        self.engine_sfx = loader.loadSfx(props.sounds.engine)
        self.brake_sfx = loader.loadSfx(props.sounds.brake)
        self.crash_sfx = loader.loadSfx(props.sounds.crash)
        self.crash_high_speed_sfx = loader.loadSfx(props.sounds.crash_hs)
        self.lap_sfx = loader.loadSfx(props.sounds.lap)
        self.landing_sfx = loader.loadSfx(props.sounds.landing)
        map(lambda sfx: sfx.set_loop(True), [self.engine_sfx, self.brake_sfx])
        self.engine_sfx.set_volume(0)
        self.engine_sfx.play()

    def update(self, is_skidmarking, speed_ratio):
        is_brk_playing = self.brake_sfx.status() == AudioSound.PLAYING
        if is_skidmarking and not is_brk_playing:
            self.brake_sfx.play()
        elif not is_skidmarking and is_brk_playing:
            self.brake_sfx.stop()
        self.engine_sfx.set_volume(max(.25, abs(speed_ratio)))
        self.engine_sfx.set_play_rate(max(.25, abs(speed_ratio)))

    def destroy(self):
        self.engine_sfx.stop()
        Audio.destroy(self)
