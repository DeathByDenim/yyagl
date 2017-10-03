from abc import ABCMeta
from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from .logic import RankingLogic
from .gui import RankingGui


class RankingFacade(Facade):

    def __init__(self):
        self._fwd_mth('load', lambda obj: obj.logic.load)
        self._fwd_mth('show', lambda obj: obj.gui.show)
        self._fwd_mth('hide', lambda obj: obj.gui.hide)
        self._fwd_mth('reset', lambda obj: obj.logic.reset)
        self._fwd_mth('attach_obs', lambda obj: obj.gui.attach_obs)
        self._fwd_mth('detach_obs', lambda obj: obj.gui.detach_obs)
        self._fwd_prop('carname2points', lambda obj: obj.logic.carname2points)


class Ranking(GameObject, RankingFacade):
    __metaclass__ = ABCMeta

    def __init__(self, car_names, background_fpath, font, fg_col):
        init_lst = [
            [('gui', RankingGui, [self, background_fpath, font, fg_col])],
            [('logic', RankingLogic, [self, car_names])]]
        GameObject.__init__(self, init_lst)
        RankingFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        RankingFacade.destroy(self)
