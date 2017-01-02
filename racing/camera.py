from panda3d.core import Vec3


class Camera(object):

    cam_speed = 50
    cam_dist_min = 12
    cam_dist_max = 18
    cam_z_max = 5
    cam_z_min = 3
    look_dist_min = 2
    look_dist_max = 6
    look_z_max = 2
    look_z_min = 0

    def __init__(self, car):
        self.car = car
        self.tgt_cam_x = None
        self.tgt_cam_y = None
        self.tgt_cam_z = None
        self.tgt_look_x = None
        self.tgt_look_y = None
        self.tgt_look_z = None

    def update_cam(self):
        speed_ratio = self.car.phys.speed_ratio
        cam_dist_diff = self.cam_dist_max - self.cam_dist_min
        look_dist_diff = self.look_dist_max - self.look_dist_min
        cam_z_diff = self.cam_z_max - self.cam_z_min
        look_z_diff = self.look_z_max - self.look_z_min

        nodepath = self.car.gfx.nodepath
        fwd_vec = eng.base.render.getRelativeVector(nodepath, Vec3(0, 1, 0))
        fwd_vec.normalize()

        car_pos = nodepath.get_pos()
        cam_vec = -fwd_vec * (self.cam_dist_min + cam_dist_diff * speed_ratio)
        tgt_vec = fwd_vec * (self.look_dist_min + look_dist_diff * speed_ratio)
        delta_pos_z = self.cam_z_min + cam_z_diff * speed_ratio
        delta_cam_z = self.look_z_min + look_z_diff * speed_ratio

        curr_cam_pos = car_pos + cam_vec + (0, 0, delta_pos_z)
        curr_cam_dist_fact = self.cam_dist_min + cam_dist_diff * speed_ratio

        curr_occl = self.__occlusion_mesh(curr_cam_pos, curr_cam_dist_fact)
        if curr_occl:
            occl_pos = curr_occl.getHitPos()
            cam_vec = occl_pos - car_pos

        self.tgt_cam_x = car_pos.x + cam_vec.x
        self.tgt_cam_y = car_pos.y + cam_vec.y
        self.tgt_cam_z = car_pos.z + cam_vec.z + delta_pos_z

        self.tgt_look_x, self.tgt_look_y, self.tgt_look_z = car_pos + tgt_vec

        curr_incr = self.cam_speed * globalClock.getDt()

        def new_pos(cam_pos, tgt):
            beyond = abs(cam_pos - tgt) > curr_incr
            fit_pos = lambda: cam_pos + (1 if tgt > cam_pos else -1) * curr_incr
            return fit_pos() if beyond else tgt
        new_x = new_pos(eng.base.camera.getX(), self.tgt_cam_x)
        new_y = new_pos(eng.base.camera.getY(), self.tgt_cam_y)
        new_z = new_pos(eng.base.camera.getZ(), self.tgt_cam_z)

        # overwrite camera's position to set the physics
        #new_x = car_pos.x + 10
        #new_y = car_pos.y - 5
        #new_z = car_pos.z + 5

        if not self.car.logic.is_rolling:
            eng.base.camera.setPos(new_x, new_y, new_z)
        look_z = self.tgt_look_z + delta_cam_z
        eng.base.camera.look_at(self.tgt_look_x, self.tgt_look_y, look_z)

    def __occlusion_mesh(self, pos, curr_cam_dist_fact):
        tgt = self.car.gfx.nodepath.getPos()
        occl = eng.phys.world_phys.rayTestClosest(pos, tgt)
        if not occl.hasHit():
            return
        occl_n = occl.getNode().getName()
        if occl_n not in ['Vehicle', 'Goal'] and curr_cam_dist_fact > .1:
            return occl

    @property
    def camera(self):
        return eng.base.camera

    def destroy(self):
        self.car = None