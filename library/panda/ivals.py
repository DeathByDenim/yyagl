from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.FunctionInterval import Func


class PandaSeq(object):

    def __init__(self, *args):
        ivals = [arg.ival for arg in args]
        self.seq = Sequence(*ivals)

    def start(self): return self.seq.start()

    def append(self, ival): return self.seq.append(ival.ival)


class PandaWait(object):

    def __init__(self, time): self.ival = Wait(time)


class PandaPosIval(object):

    def __init__(self, np, time=1.0, pos=(0, 0, 0), blendType='easeInOut'):
        self.ival = LerpPosInterval(np, time, pos=pos, blendType=blendType)


class PandaFunc(object):

    def __init__(self, fun, *args): self.ival = Func(fun, *args)
