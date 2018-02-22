class ObsInfo(object):

    def __init__(self, mth, sort, args):
        self.mth = mth
        self.sort = sort
        self.args = args


class Subject(object):

    def __init__(self):
        self.observers = {}

    def attach(self, obs_meth, sort=10, rename='', args=[]):
        onm = rename or obs_meth.__name__
        if onm not in self.observers: self.observers[onm] = []
        self.observers[onm] += [ObsInfo(obs_meth, sort, args)]
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
                obs.mth(*act_args, **kwargs)

    def destroy(self): self.observers = None


class Observer(object): pass
