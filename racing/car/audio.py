from panda3d.core import AudioSound
from yyagl.gameobject import Audio


class CarAudio(Audio):

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        self.engine_sfx = loader.loadSfx('assets/sfx/engine.ogg')
        self.brake_sfx = loader.loadSfx('assets/sfx/brake.ogg')
        self.crash_sfx = loader.loadSfx('assets/sfx/crash.ogg')
        crash_hs = 'assets/sfx/crash_high_speed.ogg'
        self.crash_high_speed_sfx = loader.loadSfx(crash_hs)
        self.lap_sfx = loader.loadSfx('assets/sfx/lap.ogg')
        self.landing_sfx = loader.loadSfx('assets/sfx/landing.ogg')
        map(lambda sfx: sfx.set_loop(True), [self.engine_sfx, self.brake_sfx])
        self.engine_sfx.play()

    def update(self, input_dct):
        playing = self.brake_sfx.status() == AudioSound.PLAYING
        if self.mdt.logic.is_skidmarking and not playing:
            self.brake_sfx.play()
        elif not self.mdt.logic.is_skidmarking and playing:
            self.brake_sfx.stop()
        self.engine_sfx.set_volume(max(.25, abs(self.mdt.phys.speed_ratio)))
        self.engine_sfx.set_play_rate(max(.25, abs(self.mdt.phys.speed_ratio)))

    def destroy(self):
        self.engine_sfx.stop()
        Audio.destroy(self)
