from abc import ABCMeta
from yyagl.gameobject import GameObjectMdt
from .logic import RaceLogic, RaceLogicSinglePlayer, RaceLogicServer, \
    RaceLogicClient
from .event import RaceEvent, RaceEventServer, RaceEventClient
from .gui.gui import RaceGui
from .fsm import _Fsm


class Race(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = RaceLogic
    event_cls = RaceEvent
    gui_cls = RaceGui
    fsm_cls = _Fsm

    def __init__(self, init_lst=[]):
        init_lst = [
            [('fsm', self.fsm_cls, [self])],
            [('gfx', self.gfx_cls, [self])],
            [('phys', self.phys_cls, [self])],
            [('gui', self.gui_cls, [self])],
            [('logic', self.logic_cls, [self])],
            [('audio', self.audio_cls, [self])],
            [('ai', self.ai_cls, [self])],
            [('event', self.event_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst)


class RaceSinglePlayer(Race):
    logic_cls = RaceLogicSinglePlayer


class RaceServer(Race):
    logic_cls = RaceLogicServer
    event_cls = RaceEventServer


class RaceClient(Race):
    logic_cls = RaceLogicClient
    event_cls = RaceEventClient
