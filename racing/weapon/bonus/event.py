from yyagl.gameobject import EventColleague


class BonusEvent(EventColleague):

    def __init__(self, mdt):
        EventColleague.__init__(self, mdt)
        self.eng.attach_obs(self.on_collision)

    def on_collision(self, obj, tgt_obj):
        # define "filtered" notification, so a receiver can define a filter for
        # its message (like a precondition for receiving them)
        is_bon = tgt_obj.get_name() == 'Bonus'
        if is_bon and obj in self.mdt.phys.ghost.getOverlappingNodes():
            self.notify('on_bonus_collected', self.mdt)
            self.mdt.destroy()

    def destroy(self):
        self.eng.detach_obs(self.on_collision)
        EventColleague.destroy(self)
