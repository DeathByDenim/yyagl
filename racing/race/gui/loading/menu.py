from yyagl.gameobject import GameObjectMdt, Gui
from yyagl.engine.gui.menu import MenuArgs, Menu
from .loadingpage import LoadingPage


class _Gui(Gui):

    def __init__(self, mdt, loading, track_path, car_path, player_cars, drivers):
        Gui.__init__(self, mdt)
        menu_args = MenuArgs(
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .25, 1), .1,
            (-4.6, 4.6, -.32, .88), (0, 0, 0, .2), (.9, .9, .9, .8),
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg',
            '')
        self.menu = Menu(menu_args)
        self.menu.loading = loading
        self.menu.logic.push_page(LoadingPage(self.menu, track_path, car_path, player_cars, drivers))

    def destroy(self):
        Gui.destroy(self)
        self.menu = self.menu.destroy()


class LoadingMenu(Menu):
    gui_cls = _Gui


    def __init__(self, loading, track_path='', car_path='', player_cars=[], drivers=None):
        init_lst = [
            [('fsm', self.fsm_cls, [self])],
            [('gfx', self.gfx_cls, [self])],
            [('phys', self.phys_cls, [self])],
            [('gui', self.gui_cls, [self, loading, track_path, car_path, player_cars, drivers])],
            [('logic', self.logic_cls, [self])],
            [('audio', self.audio_cls, [self])],
            [('ai', self.ai_cls, [self])],
            [('event', self.event_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst)
