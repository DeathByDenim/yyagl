from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage


class Tutorial:

    def __init__(self):
        keys_img = OnscreenImage(
            image='assets/images/gui/keys.png', parent=eng.base.a2dTopLeft,
            pos=(.7, 1, -.4), scale=(.6, 1, .3))
        keys_img.setTransparency(True)
        destroy_keys = lambda task: keys_img.destroy()
        taskMgr.doMethodLater(5.0, destroy_keys, 'destroy keys')

    def destroy(self):
        pass
