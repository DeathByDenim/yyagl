from panda3d.core import TextNode, NodePath
from direct.gui.OnscreenText import OnscreenText
from yyagl.gameobject import Colleague
from yyagl.engine.gui.page import PageGui
from direct.gui.DirectGuiGlobals import FLAT
from direct.gui.DirectButton import DirectButton


class Loading(Colleague):

    def __init__(self, mdt):
        self.mdt = mdt

    def enter_loading(self, track_path='', car_path='', player_cars=[]):
        eng.gfx.init()
        if not track_path and not car_path:
            tracks = ['prototype', 'desert']
            track = tracks[tracks.index(game.options['save']['track'])]
            track_path = 'tracks/' + track
            car_path = game.options['save']['car']
        conf = game.options
        if 'save' not in conf.dct:
            conf['save'] = {}
        conf['save']['track'] = track_path[7:]
        conf['save']['car'] = car_path
        conf.store()
        font = eng.font_mgr.load_font('assets/fonts/zekton rg.ttf')
        self.load_txt = OnscreenText(
            text=_('LOADING...\n\nPLEASE WAIT, IT MAY REQUIRE SOME TIME'),
            scale=.12, pos=(0, .4), font=font, fg=(.75, .75, .75, 1),
            wordwrap=12)
        self.curr_load_txt = OnscreenText(
            text='',
            scale=.08, pos=(-.1, .1), font=font, fg=(.75, .75, .75, 1),
            parent=base.a2dBottomRight, align=TextNode.A_right)
        try:
            self.preview = loader.loadModel(track_path + '/preview/preview')
        except IOError:
            self.preview = loader.loadModel(track_path+'/preview/preview.bam')
        self.preview.reparent_to(render)
        self.cam_pivot = NodePath('cam pivot')
        self.cam_pivot.reparent_to(render)
        self.cam_node = NodePath('cam node')
        self.cam_node.set_pos(500, 0, 0)
        self.cam_node.reparent_to(self.cam_pivot)
        hpr = (360, 0, 0)
        self.cam_pivot.hprInterval(25, hpr, blendType='easeInOut').loop()
        self.cam_tsk = taskMgr.add(self.update_cam, 'update cam')
        txt = _(
            'Please, visit our site while the track is loading! We hope you can find interesting stuff there. '
            'Moreover, by visiting it (especially disabling your adblocker onto the site) '
            'you support us and contribute to keep Yorg as free as possible. Thank you very much! :)')
        self.txt = OnscreenText(text=txt, pos=(-1.65, -.4), scale=.08, wordwrap=24,
            fg=(1, 1, 1, 1), font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'),
            align=TextNode.A_left)
        menu_data = [
            ('Visit our site', _('visit our site\nI love to support you!'),
             lambda: eng.gui.open_browser('http://www.ya2.it'))]
        btn_args = {
            'text_font': eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'),
            'text_fg': (.75, .75, .75, 1),
            'frameColor': (0, 0, 0, .2),
            'relief': FLAT,
            'frameSize': (-.6, .6, -.2, .16),
            'rolloverSound': loader.loadSfx('assets/sfx/menu_over.wav'),
            'clickSound': loader.loadSfx('assets/sfx/menu_clicked.ogg')}
        self.btn = DirectButton(text=menu_data[0][1], pos=(1.0, 0, -.55), command=menu_data[0][2], text_scale=.08, **btn_args)
        PageGui.transl_text(self.btn, menu_data[0][0])

    def on_loading(self, msg):
        self.curr_load_txt.setText(msg)

    def update_cam(self, task):
        pos = self.cam_node.get_pos(render)
        eng.base.camera.set_pos(pos[0], pos[1], 1000)
        eng.base.camera.look_at(0, 0, 0)
        return task.again

    def exit_loading(self):
        game.player_car.event.attach(self.mdt.event.on_wrong_way)
        game.player_car.event.attach(self.mdt.event.on_end_race)
        self.preview.remove_node()
        self.cam_pivot.remove_node()
        self.load_txt.destroy()
        self.curr_load_txt.destroy()
        taskMgr.remove(self.cam_tsk)
        eng.base.camera.set_pos(0, 0, 0)
        self.txt.destroy()
        self.btn.destroy()
