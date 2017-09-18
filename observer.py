from collections import namedtuple


ObsInfo = namedtuple('ObsInfo', 'mth sort redirect args')


class Subject(object):

    def __init__(self):
        self.observers = {}

    def attach(self, obs_meth, sort=10, rename='', redirect=None, args=[]):
        if rename:
            obs_meth.__name__ = rename
        onm = obs_meth if isinstance(obs_meth, str) else obs_meth.__name__
        if onm not in self.observers: self.observers[onm] = []
        self.observers[onm] += [ObsInfo(obs_meth, sort, redirect, args)]
        sorted_obs = sorted(self.observers[onm], key=lambda obs: obs.sort)
        self.observers[onm] = sorted_obs

    def detach(self, obs_meth):
        onm = obs_meth.__name__
        observers = [obs for obs in self.observers[onm] if obs.mth == obs_meth]
        if not observers: raise Exception
        map(self.observers[onm].remove, observers)

    def notify(self, meth, *args, **kwargs):
        if meth not in self.observers: return  # no obs for this notification
        for obs in self.observers[meth]:
            if obs in self.observers[meth]: # if an obs removes another one
                act_args = obs.args + list(args)
                cb_meth = obs.redirect or obs.mth
                cb_meth(*act_args, **kwargs)

    def destroy(self): self.observers = None


class Observer(object): pass
