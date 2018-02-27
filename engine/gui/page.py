from inspect import getmro
from panda3d.core import LPoint3f, LVecBase2f
from direct.gui.DirectGuiGlobals import ENTER, EXIT, DISABLED
from yyagl.library.gui import Btn, Slider, CheckBtn, OptionMenu, Entry
from yyagl.library.ivals import Seq, Wait, PosIval, Func
from yyagl.engine.vec import Vec2
from ...gameobject import GameObject, GuiColleague, EventColleague
from ...facade import Facade
from .imgbtn import ImgBtn
from .widget import Widget


class PageGui(GuiColleague):

    def __init__(self, mediator, menu_args):
        GuiColleague.__init__(self, mediator)
        self.menu_args = menu_args
        self.widgets = []
        self.build()
        self.translate()
        self.curr_wdg = self.__next_wdg((-.1, 0, -1), (-3.6, 1, 1))
        if self.curr_wdg: self.curr_wdg.on_wdg_enter()

    def build(self, back_btn=True):
        if back_btn: self.__build_back_btn()
        self._set_widgets()
        self.transition_enter()
        self.eng.cursor_top()

    def add_widgets(self, widgets): self.widgets += widgets

    def on_arrow(self, direction):
        if not self.curr_wdg: return
        catch_cmd = self.curr_wdg.on_arrow(direction)
        # e.g. up/down in a combobox or left/right in a slider
        if catch_cmd: return
        next_wdg = self.__next_wdg(direction)
        if not next_wdg: return
        self.curr_wdg.on_wdg_exit()
        self.curr_wdg = next_wdg
        self.curr_wdg.on_wdg_enter()

    def on_enter(self):
        if not self.curr_wdg: return
        if self.curr_wdg.on_enter(): self.enable()

    @property
    def buttons(self):
        is_btn = lambda wdg: Btn in getmro(wdg.__class__)
        return [wdg for wdg in self.widgets if is_btn(wdg)]

    def __currwdg2wdg_dot_direction(self, wdg, direction, start=None):
        start_pos = start if start else self.curr_wdg.get_pos(aspect2d)
        vec = wdg.get_pos(aspect2d) - start_pos
        vec = Vec2(vec.x, vec.z).normalize()
        return vec.dot(LVecBase2f(direction[0], direction[2]))

    def __next_weight(self, wdg, direction, start=None):
        start_pos = start if start else self.curr_wdg.get_pos(aspect2d)
        dot = self.__currwdg2wdg_dot_direction(wdg, direction, start)
        wdg_pos = wdg.get_pos(aspect2d)
        #if 'Slider' in wdg.__class__ .__name__:
        #    wdg_pos = LPoint3f(wdg_pos[0], 1, wdg_pos[2])
        axis = 0 if direction in [(-1, 0, 0), (1, 0, 0)] else 2
        proj_dist = abs(wdg_pos[axis] - start_pos[axis])
        weights = [.5, .5] if not axis else [.1, .9]
        return weights[0] * (dot * dot) + weights[1] * (1 - proj_dist)

    def __next_wdg(self, direction, start=None):
        # interactive classes
        iclss = [Btn, CheckBtn, Slider, OptionMenu, ImgBtn, Entry]
        inter = lambda wdg: any(pcl in iclss for pcl in getmro(wdg.__class__))
        wdgs = [wdg for wdg in self.widgets if inter(wdg)]
        wdgs = filter(lambda wdg: wdg.is_enabled, wdgs)
        if hasattr(self, 'curr_wdg') and self.curr_wdg:
            wdgs.remove(self.curr_wdg)
        in_direction = lambda wdg: self.__currwdg2wdg_dot_direction(wdg, direction, start) > .1
        wdgs = filter(in_direction, wdgs)
        if not wdgs: return
        nextweight = lambda wdg: self.__next_weight(wdg, direction, start)
        return max(wdgs, key=nextweight)

    def _set_widgets(self):
        map(self.__set_widget, self.widgets)

    def __set_widget(self, wdg):
        clsname = wdg.__class__.__name__ + 'Widget'
        wdg.__class__ = type(clsname, (wdg.__class__, Widget), {})
        wdg.init(wdg)
        if hasattr(wdg, 'bind'):
            wdg.bind(ENTER, wdg.on_wdg_enter)
            wdg.bind(EXIT, wdg.on_wdg_exit)

    def transition_enter(self):
        self.translate()
        map(self.__set_enter_transition, self.widgets)
        self.enable()

    def __set_enter_transition(self, wdg):
        pos = wdg.get_pos()
        wdg.set_pos(pos - (3.6, 0, 0))
        Seq(
            Wait(abs(pos[2] - 1) / 4),
            PosIval(wdg.get_np(), .5, pos)
        ).start()

    def enable(self):
        #evts=[
        #    ('arrow_left-up', self.on_arrow, [(-1, 0, 0)]),
        #    ('arrow_right-up', self.on_arrow, [(1, 0, 0)]),
        #    ('arrow_up-up', self.on_arrow, [(0, 0, 1)]),
        #    ('arrow_down-up', self.on_arrow, [(0, 0, -1)]),
        #    ('enter', self.on_enter)]
        #map(lambda args: self.mediator.event.accept(*args), evts)
        pass

    def disable(self):
        #evts=['arrow_left-up', 'arrow_right-up', 'arrow_up-up',
        #      'arrow_down-up', 'enter']
        #map(self.mediator.event.ignore, evts)
        pass

    def transition_exit(self, destroy=True):
        map(lambda wdg: self.__set_exit_transition(wdg, destroy), self.widgets)

    def __set_exit_transition(self, wdg, destroy):
        pos = wdg.get_pos()
        end_pos = (pos[0] + 3.6, pos[1], pos[2])
        seq = Seq(
            Wait(abs(pos[2] - 1) / 4),
            PosIval(wdg.get_np(), .5, end_pos),
            Func(wdg.destroy if destroy else wdg.hide))
        if not destroy: seq.append(Func(wdg.set_pos, pos))
        seq.start()

    def translate(self):
        tr_wdg = [wdg for wdg in self.widgets if hasattr(wdg, 'bind_transl')]
        for wdg in tr_wdg: wdg.wdg['text'] = wdg.bind_transl

    def __build_back_btn(self):
        self.widgets += [Btn(
            text='', pos=(-.2, 1, -.8), command=self._on_back,
            tra_src='Back', tra_tra=_('Back'), **self.menu_args.btn_args)]

    def _on_back(self): self.notify('on_back', self.__class__.__name__)

    def show(self):
        map(lambda wdg: wdg.show(), self.widgets)
        self.transition_enter()

    def hide(self):
        self.transition_exit(False)
        self.notify('on_hide')

    def destroy(self):
        self.menu_args = None
        self.transition_exit()


class PageEvent(EventColleague):

    def on_back(self): pass


class PageFacade(Facade):

    def __init__(self):
        fwds =[
            ('show', lambda obj: obj.gui.show),
            ('hide', lambda obj: obj.gui.hide),
            ('enable', lambda obj: obj.gui.enable),
            ('disable', lambda obj: obj.gui.disable),
            ('attach_obs', lambda obj: obj.gui.attach),
            ('detach_obs', lambda obj: obj.gui.detach)]
        map(lambda args: self._fwd_mth(*args), fwds)


class Page(GameObject, PageFacade):

    gui_cls = PageGui
    event_cls = PageEvent

    def __init__(self, menu_args):
        # refactor: pages e.g. yyagl/engine/gui/mainpage.py don't call this
        PageFacade.__init__(self)
        self.menu_args = menu_args
        GameObject.__init__(self, self.init_lst)
        self.gui.attach(self.on_hide)
        self.gui.attach(self.on_back)

    @property
    def init_lst(self):
        return [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_args])]]

    def on_hide(self): self.event.ignoreAll()

    def on_back(self, cls_name): self.event.on_back()

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
