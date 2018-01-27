from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from yyagl.gameobject import GuiColleague
from yyagl.facade import Facade
from .results import Results
from .loading.loading import Loading
from .minimap import Minimap


class RaceGuiFacade(Facade):

    def __init__(self):
        self._fwd_mth('update_minimap', lambda obj: obj.minimap.update)


class RaceGui(GuiColleague, RaceGuiFacade):

    def __init__(self, mdt, rprops):
        GuiColleague.__init__(self, mdt)
        r_p = self.props = rprops
        self.results = Results(rprops)
        self.loading = Loading()
        self.way_txt = OnscreenText(
            '', pos=(.1, .1), scale=.1,
            fg=r_p.season_props.gameprops.menu_args.text_err,
            parent=base.a2dBottomLeft, align=TextNode.ALeft,
            font=self.eng.font_mgr.load_font(r_p.season_props.font))
        self.minimap = None
        RaceGuiFacade.__init__(self)

    def start(self):
        self.minimap = Minimap(
            self.mdt.track.lrtb, self.props.minimap_path,
            self.props.minimap_image, self.props.col_dct,
            self.props.season_props.car_names,
            self.props.season_props.player_car_name)

    def destroy(self):
        self.results.destroy()
        self.way_txt.destroy()
        self.minimap.destroy()
        GuiColleague.destroy(self)
