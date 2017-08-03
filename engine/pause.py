from os import pardir
from os.path import dirname, abspath, join
from sys import modules
from direct.task import Task
from direct.interval.IntervalGlobal import ivalMgr
from direct.gui.DirectFrame import DirectFrame
from ..gameobject import Gui, Logic, GameObject, Colleague


class PauseGui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        self.pause_frame = None

    def toggle(self, show_frm=True):
        if not self.mdt.logic.is_paused:
            if show_frm:
                self.pause_frame = DirectFrame(frameColor=(.3, .3, .3, .7),
                                               frameSize=(-1.8, 1.8, -1, 1))
        else:
            if self.pause_frame:
                self.pause_frame.destroy()


class PauseLogic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.paused_taskchain = 'ya2 paused tasks'
        taskMgr.setupTaskChain(self.paused_taskchain, frameBudget=0)
        self.is_paused = False
        fpath = dirname(modules[Task.__name__].__file__)
        self.direct_dir = abspath(join(fpath, pardir))
        self.paused_ivals = []
        self.paused_tasks = []

    def __process_task(self, tsk):
        func = tsk.get_function()  # ordinary tasks
        mod = func.__module__
        # sys_mod = sys.modules[mod].__file__.find(self.direct_dir) < 0
        # runtime: AttributeError: 'module' object has no attribute '__file__'
        modfile = ''
        if "from '" in str(modules[mod]):
            modfile = str(modules[mod]).split("from '")[1][:-2]
        sys_mod = modfile.find(self.direct_dir) < 0
        is_act = False
        if hasattr(func, 'im_class'):
            is_act = func.im_class.__name__ == 'ActorInterval'
        if mod.find('direct.interval') == 0 and not is_act:
            self.paused_tasks.append(tsk)  # python-based intervals
            tsk.interval.pause()
        elif mod not in modules or sys_mod:
            self.paused_tasks.append(tsk)

    def __pause_tsk(self, tsk):
        has_args = hasattr(tsk, 'getArgs')
        tsk.stored_extraArgs = tsk.get_args() if has_args else None
        if hasattr(tsk, 'getFunction'):
            tsk.stored_call = tsk.get_function()
        has_p = hasattr(tsk, '_priority')
        tsk.stored_priority = tsk._priority if has_p else tsk.get_sort()
        # only active tasks can be moved to other chain, so removes do_later
        # tasks since they are in sleeping state
        if hasattr(tsk, 'remainingTime'):  # do_later tasks
            tsk.remove()
        else:  # ordinary tasks
            tsk.lastactivetime = -tsk.time if hasattr(tsk, 'time') else 0
            tsk.setTaskChain(self.paused_taskchain)

    def pause_tasks(self):
        self.paused_tasks = []
        is_tsk = lambda tsk: tsk and hasattr(tsk, 'getFunction')
        tasks = [tsk for tsk in taskMgr.getTasks() if is_tsk(tsk)]
        map(self.__process_task, tasks)
        for tsk in [_tsk for _tsk in taskMgr.getDoLaters()if is_tsk(_tsk)]:
            self.paused_tasks.append(tsk)
            tsk.remainingTime = tsk.wakeTime - globalClock.get_frame_time()
            # I need to alter the wakeTime during task resume,
            # so I have to save the remaining time.
        map(self.__pause_tsk, self.paused_tasks)

    @staticmethod
    def __resume_do_later(tsk):
        d_t = globalClock.get_real_time() - globalClock.get_frame_time()
        temp_delay = tsk.remainingTime - d_t
        upon_death = tsk.uponDeath if hasattr(tsk, 'uponDeath') else None
        # no need to pass appendTask, since if it's already true,
        # the task is already appended to extraArgs
        new_task = taskMgr.doMethodLater(
            temp_delay, tsk.stored_call, tsk.name, uponDeath=upon_death,
            priority=tsk.stored_priority, extraArgs=tsk.stored_extraArgs)
        if hasattr(tsk, 'remainingTime'):  # restore the original delayTime
            new_task.delayTime = tsk.delayTime

    def __resume_tsk(self, tsk):
        if hasattr(tsk, 'interval'):  # it must be python-based intervals
            tsk.interval.resume()
            if hasattr(tsk, 'stored_call'):
                tsk.set_function(tsk.stored_call)
            return
        if hasattr(tsk, 'remainingTime'):
            self.__resume_do_later(tsk)
            return
        tsk.set_delay(tsk.lastactivetime)  # ordinary tasks
        tsk.set_task_chain('default')
        tsk.clear_delay()  # to avoid assertion error on resume

    def remove_task(self, tsk):
        if tsk in self.paused_tasks:
            self.paused_tasks.remove(tsk)
        # refactor: do_later invokes the method passing the task, so it'll be
        # possible to remove the task from the client and don't ask here
        # this will unhide some errors caught here

    def pause(self):
        self.paused_ivals = ivalMgr.getIntervalsMatching('*')
        self.pause_tasks()
        base.disableParticles()
        self.is_paused = True
        return self.is_paused

    def resume(self):
        map(lambda ival: ival.resume(), self.paused_ivals)
        map(self.__resume_tsk, self.paused_tasks)
        base.enableParticles()
        self.is_paused = False
        return self.is_paused

    def toggle(self, show_frm=True):
        self.mdt.gui.toggle(show_frm)
        (self.resume if self.is_paused else self.pause)()


class PauseMgr(GameObject, Colleague):

    def __init__(self, mdt):
        Colleague.__init__(self, mdt)
        self.gui = PauseGui(self)
        self.logic = PauseLogic(self)

    def remove_task(self, tsk):
        return self.logic.remove_task(tsk)
