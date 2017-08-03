from random import uniform
from yyagl.gameobject import Ai


class RearRocketAi(Ai):

    def __init__(self, mdt, car):
        Ai.__init__(self, mdt)
        self.collect_time = globalClock.get_frame_time()
        self.car = car
        self.fire_time = uniform(2, 5)

    def update(self):
        curr_t = globalClock.get_frame_time()
        is_before_fire = curr_t - self.collect_time < self.fire_time
        if self.mdt.logic.has_fired or is_before_fire:
            return
        obstacles = list(self.car.ai.rear_logic.get_obstacles())
        name_c, distance_center, name_l, distance_left, name_r, \
            distance_right = obstacles
        return distance_center < 40 and name_c == 'Vehicle'
