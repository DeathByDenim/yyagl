from datetime import datetime
from platform import system, release
from panda3d.core import loadPrcFileData
from direct.directnotify.DirectNotify import DirectNotify
from ..gameobject import Colleague


class LogMgr(Colleague):

    def __init__(self, mdt):
        Colleague.__init__(self, mdt)
        self.__notify = DirectNotify().newCategory('ya2')

    @staticmethod
    def configure():
        loadPrcFileData('', 'notify-level-ya2 info')

    def log(self, msg):
        str_time = datetime.now().strftime("%H:%M:%S")
        log_msg = '{time} {msg}'.format(time=str_time, msg=msg)
        self.__notify.info(log_msg)

    def log_conf(self):
        self.log('version: ' + eng.logic.version)
        self.log('operative system: ' + system() + ' ' + release())
        gsg = eng.base.win.get_gsg()
        self.log(gsg.getDriverVendor())
        self.log(gsg.getDriverRenderer())
        shad_maj = gsg.getDriverShaderVersionMajor()
        shad_min = gsg.getDriverShaderVersionMinor()
        self.log('shader: {maj}.{min}'.format(maj=shad_maj, min=shad_min))
        self.log(gsg.getDriverVersion())
        drv_maj = gsg.getDriverVersionMajor()
        drv_min = gsg.getDriverVersionMinor()
        drv = 'driver version: {maj}.{min}'
        self.log(drv.format(maj=drv_maj, min=drv_min))
        if not eng.base.win:
            return
        prop = eng.base.win.get_properties()
        self.log('fullscreen: ' + str(prop.get_fullscreen()))
        res_x, res_y = prop.get_x_size(), prop.get_y_size()
        res_tmpl = 'resolution: {res_x}x{res_y}'
        self.log(res_tmpl.format(res_x=res_x, res_y=res_y))
