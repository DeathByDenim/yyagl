from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from yyagl.gameobject import Gui
from yyagl.engine.gui.imgbtn import ImgBtn
from panda3d.core import TextNode


class TuningGui(Gui):

    def __init__(self, mdt, sprops):
        Gui.__init__(self, mdt)
        self.buttons = self.background = None
        self.sprops = sprops

    def show(self):
        self.background = OnscreenImage(
            self.sprops.background_fpath, scale=(1.77778, 1, 1))
        self.background.setBin('background', 10)
        bprops = {'scale': .4, 'command': self.on_btn}
        self.txt = OnscreenText(
            text=_('What do you want to upgrade?'), scale=.1, pos=(0, .76),
            font=loader.loadFont(self.sprops.font), fg=self.sprops.fg_col)
        self.buttons = [ImgBtn(
            pos=(-1.2, 1, .1), image=self.sprops.tuning_imgs[0],
            extraArgs=['f_engine'], **bprops)]
        self.buttons += [ImgBtn(
            pos=(0, 1, .1), image=self.sprops.tuning_imgs[1],
            extraArgs=['f_tires'], **bprops)]
        self.buttons += [ImgBtn(
            pos=(1.2, 1, .1), image=self.sprops.tuning_imgs[2],
            extraArgs=['f_suspensions'], **bprops)]
        tuning = self.mdt.car2tuning[self.sprops.player_car_name]
        self.upg1_txt = OnscreenText(
            text=_('current upgrades: +') + str(tuning.f_engine),
            scale=.06,
            pos=(-1.53, -.36), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft, fg=self.sprops.fg_col)
        self.upg2_txt = OnscreenText(
            text=_('current upgrades: +') + str(tuning.f_tires),
            scale=.06,
            pos=(-.35, -.36), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft, fg=self.sprops.fg_col)
        self.upg3_txt = OnscreenText(
            text=_('current upgrades: +') + str(tuning.f_suspensions),
            scale=.06,
            pos=(.85, -.36), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft, fg=self.sprops.fg_col)
        self.hint1_txt = OnscreenText(
            text=_("engine: it increases car's maximum speed"),
            scale=.06,
            pos=(-1.53, -.46), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft, fg=self.sprops.fg_col)
        self.hint2_txt = OnscreenText(
            text=_("tires: they increase car's adherence"),
            scale=.06,
            pos=(-.35, -.46), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft, fg=self.sprops.fg_col)
        self.hint3_txt = OnscreenText(
            text=_("supensions: they increase car's stability"),
            scale=.06,
            pos=(.85, -.46), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft, fg=self.sprops.fg_col)

    def on_btn(self, val):
        self.notify('on_tuning_sel', val)

    def hide(self):
        wdgs = [self.background, self.txt, self.hint1_txt, self.hint2_txt,
                self.hint3_txt, self.upg1_txt, self.upg2_txt,
                self.upg3_txt]
        map(lambda wdg: wdg.destroy(), self.buttons + wdgs)
