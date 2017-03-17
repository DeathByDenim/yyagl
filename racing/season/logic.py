from yyagl.gameobject import Logic
from yyagl.racing.ranking.ranking import Ranking
from yyagl.racing.tuning.tuning import Tuning, TuningProps


class SeasonLogic(Logic):

    def __init__(self, mdt, season_props):
        Logic.__init__(self, mdt)
        self.props = s_p = season_props
        self.ranking = Ranking(s_p.cars, s_p.background, s_p.font, s_p.fg_col)
        tuning_props = TuningProps(
            s_p.cars, s_p.player_car, s_p.background, s_p.engine_img,
            s_p.tires_img, s_p.suspensions_img)
        self.tuning = Tuning(tuning_props)
        self.drivers = {}
        self.skills = s_p.skills
        self.tracks = s_p.tracks
        self.player_car = s_p.player_car

    def start(self):
        self.ranking.logic.reset()
        self.tuning.logic.reset()
        self.drivers = {}
        self.tuning.attach_obs(self.on_tuning_done)

    def on_tuning_done(self):
        self.step()

    def load(self, ranking, tuning, drivers):
        self.ranking.load(ranking)
        self.tuning.load(tuning)
        self.drivers = drivers

    def step(self):
        track = game.track.props.path[7:]
        # todo: reference of race into season
        if self.props.tracks.index(track) == len(self.props.tracks) - 1:
            self.notify('on_season_end')
        else:
            next_track = self.props.tracks[self.props.tracks.index(track) + 1]
            n_t = 'tracks/' + next_track
            self.notify('on_season_cont', n_t, self.props.player_car,
                        self.drivers, self.skills)

    def destroy(self):
        self.tuning.detach_obs(self.on_tuning_done)
        Logic.destroy(self)


class SingleRaceSeasonLogic(SeasonLogic):

    def step(self):
        game.demand('Menu')
