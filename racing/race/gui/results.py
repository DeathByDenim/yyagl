from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from yyagl.racing.ranking.gui import RankingGui
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.gameobject import GameObject


class Results(GameObject):

    def __init__(self, rprops):
        GameObject.__init__(self)
        self.__res_txts = []
        self.__buttons = []
        self.drivers = self.result_frm = None
        self.rprops = rprops
        self.font = rprops.season_props.gameprops.menu_args.font
        self.text_fg = rprops.season_props.gameprops.menu_args.text_active
        self.text_bg = rprops.season_props.gameprops.menu_args.text_normal

    def show(self, race_ranking, lap_times, drivers):
        track = self.rprops.track_path
        self.drivers = drivers
        self.result_frm = DirectFrame(
            frameColor=(.8, .8, .8, .64), frameSize=(-2, 2, -1, 1))
        laps = len(lap_times)
        text_bg = self.rprops.season_props.gameprops.menu_args.text_normal
        pars = {'scale': .1, 'fg': text_bg,
                'font': self.rprops.season_props.gameprops.menu_args.font}
        self.__res_txts = [
            OnscreenText(str(round(lap_times[i], 2)),
                         pos=(0, .52 - .2 * (i + 1)), **pars)
            for i in range(laps)]
        self.__res_txts += [OnscreenText(_('LAP'), pos=(-.6, .68), **pars)]
        self.__res_txts += [OnscreenText(_('TIME'), pos=(0, .68), **pars)]
        self.__res_txts += [OnscreenText(_('RANKING'), pos=(.5, .68),
                                         align=TextNode.A_left, **pars)]
        self.__res_txts += [
            OnscreenText(str(i), pos=(-.6, .52 - .2 * i), **pars)
            for i in range(1, 4)]
        race_ranking_sorted = sorted(race_ranking.items(), key=lambda x: x[1])
        race_ranking_sorted = reversed([el[0] for el in race_ranking_sorted])

        for i, car in enumerate(race_ranking_sorted):
            dpars = i, car, .76, .54, str(i + 1) + '. %s'
            txt, img = RankingGui.set_drv_txt_img(self, *dpars)
            self.__res_txts += [txt, img]
        self.__res_txts += [
            OnscreenText(_('share:'), pos=(-.1, -.82), align=TextNode.A_right,
                         **pars)]
        self.__buttons = []

        min_time = min(lap_times or [0])
        facebook_url = self.rprops.share_urls[0]
        twitter_url = self.rprops.share_urls[1]
        twitter_url = twitter_url.format(time=round(min_time, 2), track=track)
        plus_url = self.rprops.share_urls[2]
        tumblr_url = self.rprops.share_urls[3]
        sites = [('facebook', facebook_url), ('twitter', twitter_url),
                 ('google_plus', plus_url), ('tumblr', tumblr_url)]
        menu_args= self.rprops.season_props.gameprops.menu_args
        self.__buttons += [
            ImgBtn(
                scale=.078,
                pos=(.02 + i*.18, 1, -.79), frameColor=(0, 0, 0, 0),
                image=menu_args.social_imgs_dpath % site[0],
                command=self.eng.open_browser, extraArgs=[site[1]],
                rolloverSound=menu_args.rollover_sfx,
                clickSound=menu_args.click_sfx)
            for i, site in enumerate(sites)]

        def step():
            self.notify('on_race_step', race_ranking)
            self.destroy()
            GameObject.destroy(self)
        cont_btn = DirectButton(
            text=_('Continue'), pos=(0, 1, -.6), command=step,
            **self.rprops.season_props.gameprops.menu_args.btn_args)
        self.__buttons += [cont_btn]

    def destroy(self):
        if not self.result_frm or self.result_frm.isEmpty():
            return
        # if it is reached by step then there are two destroys: step's one
        # and race.gui's one
        map(lambda txt: txt.destroy(), self.__res_txts)
        map(lambda btn: btn.destroy(), self.__buttons)
        self.result_frm.destroy()
        GameObject.destroy(self)
