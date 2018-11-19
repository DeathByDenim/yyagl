from panda3d.core import LVecBase4f
from direct.gui.DirectGuiGlobals import NORMAL, DISABLED
from yyagl.engine.vec import Vec2


class WidgetMixin(object):

    highlight_color_offset = [
        LVecBase4f(0, 0, .4, 0),
        LVecBase4f(0, .4, 0, 0),
        LVecBase4f(.4, 0, 0, 0),
        LVecBase4f(.4, .4, 0, 0)]

    def __init__(self):
        self.start_txt_color = self.start_frame_color = None
        self.was_visible = True
        self.curr_offset = LVecBase4f(0, 0, 0, 0)

    def get_np(self): return self.img

    def enable(self): pass

    def disable(self): pass

    @property
    def pos(self):
        pos = self.get_pos(aspect2d)
        return Vec2(pos[0], pos[2])


class ImgMixin(WidgetMixin):

    def init(self, wdg): pass


class FrameMixin(WidgetMixin):

    def init(self, wdg):
        self.curr_offset = LVecBase4f(0, 0, 0, 0)
        self.start_frame_color = wdg.get_np()['frameColor']

    def enable(self):
        self['state'] = NORMAL
        if hasattr(self, 'set_alpha_scale'): self.set_alpha_scale(1)

    def disable(self):
        self['state'] = DISABLED
        if hasattr(self, 'set_alpha_scale'): self.set_alpha_scale(.25)

    def on_wdg_enter(self, pos=None, player=0):  # pos: mouse's position
        self.curr_offset += WidgetMixin.highlight_color_offset[player]
        self.get_np()['frameColor'] = LVecBase4f(self.start_frame_color) + self.curr_offset

    def on_wdg_exit(self, pos=None, player=0):  # pos: mouse's position
        self.curr_offset -= WidgetMixin.highlight_color_offset[player]
        self.get_np()['frameColor'] = LVecBase4f(self.start_frame_color) + self.curr_offset


class BtnMixin(FrameMixin):

    def init(self, wdg):
        FrameMixin.init(self, wdg)
        wdg = wdg.get_np()
        self.start_txt_color = wdg.component('text0').textNode.get_text_color()

    def on_arrow(self, direction): pass

    def on_wdg_enter(self, pos=None, player=0):  # pos: mouse's position
        FrameMixin.on_wdg_enter(self, pos, player)
        self.get_np()['text_fg'] = self.start_txt_color + self.curr_offset
        self.get_np().set_shader_input('col_offset', self.curr_offset)

    def on_wdg_exit(self, pos=None, player=0):  # pos: mouse's position
        FrameMixin.on_wdg_exit(self, pos, player)
        self.get_np()['text_fg'] = self.start_txt_color
        self.get_np()['frameColor'] = self.start_frame_color
        self.get_np().set_shader_input('col_offset', self.curr_offset)

    def on_enter(self, player):
        if self['command'] and self['state'] == NORMAL:
            lst_arg = [player] if player is not None else []
            self['command'](*self['extraArgs'] + lst_arg)


class EntryMixin(FrameMixin):

    def on_arrow(self, direction): pass

    def on_wdg_enter(self, pos=None, player=0):  # pos: mouse's position
        FrameMixin.on_wdg_enter(self, pos, player)
        #self.get_np()['focus'] = 1  # it focuses it if mouse over
        #self.get_np().setFocus()

    def on_wdg_exit(self, pos=None, player=0):  # pos: mouse's position
        FrameMixin.on_wdg_exit(self, pos, player)
        #self.get_np()['focus'] = 0
        #self.get_np().setFocus()

    def on_enter(self, player=0):
        self['focus'] = 1
        if self['command'] and self['state'] == NORMAL:
            self['command'](*self['extraArgs'])


class CheckBtnMixin(BtnMixin):

    def on_enter(self, player=0):
        self['indicatorValue'] = not self['indicatorValue']
        BtnMixin.on_enter(self, player)


class SliderMixin(FrameMixin):

    def on_arrow(self, direction):
        if direction in [(-1, 0), (1, 0)]:
            n_p = self.get_np()
            delta = (n_p['range'][1] - n_p['range'][0]) / 10.0
            n_p['value'] += -delta if direction == (-1, 0) else delta
            return True

    def on_enter(self, player=0): pass


class OptionMenuMixin(BtnMixin):

    def on_arrow(self, direction):
        is_hor = direction in [(-1, 0), (1, 0)]
        nodepath = self.get_np()
        if is_hor or nodepath.popupMenu.is_hidden(): return
        old_idx = nodepath.highlightedIndex
        dir2offset = {(0, -1): 1, (0, 1): -1}
        idx = nodepath.highlightedIndex + dir2offset[direction]
        idx = min(len(nodepath['items']) - 1, max(0, idx))
        if old_idx == idx: return True
        fcol = nodepath.component('item%s' % idx)['frameColor']
        old_cmp = nodepath.component('item%s' % old_idx)
        nodepath._unhighlightItem(old_cmp, fcol)
        nodepath._highlightItem(nodepath.component('item%s' % idx), idx)
        return True

    def on_enter(self, player=0):
        nodepath = self.get_np()
        if nodepath.popupMenu.is_hidden():
            nodepath.showPopupMenu()
            nodepath._highlightItem(nodepath.component('item0'), 0)
            return
        else:
            nodepath.selectHighlightedIndex()
            idx = nodepath.selectedIndex
            if nodepath['command']: nodepath['command'](nodepath['items'][idx])
            nodepath.hidePopupMenu()
            idx += -1 if idx else 1
            fcol = nodepath.component('item%s' % idx)['frameColor']
            curr_name = 'item%s' % nodepath.selectedIndex
            nodepath._unhighlightItem(nodepath.component(curr_name), fcol)
            return True
        BtnMixin.on_enter(self)
