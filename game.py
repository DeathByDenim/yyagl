import __builtin__
from abc import ABCMeta
from .gameobject import Logic, GameObject
from .engine.engine import Engine
from .facade import Facade


class GameLogic(Logic):

    def on_start(self): pass


class GameFacade(Facade):

    def __init__(self):
        self._fwd_mth('demand', lambda obj: obj.fsm.demand)


class GameBase(GameObject, GameFacade):  # it doesn't manage the window
    __metaclass__ = ABCMeta

    def __init__(self, init_lst, cfg):
        GameFacade.__init__(self)
        self.eng = Engine(cfg)
        GameObject.__init__(self, init_lst)

    def destroy(self):
        GameFacade.destroy(self)
        GameObject.destroy(self)
        self.eng = self.eng.destroy()


class Game(GameBase):  # it adds the window

    def run(self):
        self.logic.on_start()
        base.run()
