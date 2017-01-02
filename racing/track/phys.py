from panda3d.bullet import BulletRigidBodyNode, BulletTriangleMesh, \
    BulletTriangleMeshShape, BulletGhostNode
from yyagl.gameobject import Phys
from yyagl.racing.weapon.bonus.bonus import Bonus


class TrackPhys(Phys):

    def __init__(self, mdt):
        self.corners = None
        self.rigid_bodies = []
        self.ghosts = []
        self.nodes = []
        Phys.__init__(self, mdt)

    def sync_build(self):
        self.model = loader.loadModel(self.mdt.path + '/collision')
        self.__load(['Road', 'Offroad'], False, False)
        self.__load(['Wall'], True, False)
        self.__load(['Goal', 'Slow', 'Respawn'], True, True)
        self.__set_corners()
        self.__set_waypoints()
        self.__hide_models()

    def __load(self, names, merged, ghost):
        for geom_name in names:
            eng.log_mgr.log('setting physics for: ' + geom_name)
            geoms = eng.phys.find_geoms(self.model, geom_name)
            if geoms:
                self.__process_meshes(geoms, geom_name, merged, ghost)

    def __process_meshes(self, geoms, geom_name, merged, ghost):
        meth = self.add_geoms_merged if merged else self.add_geoms_unmerged
        if not merged:
            for geom in geoms:
                self.__build_mesh(meth, geom, geom_name, ghost)
        else:
            self.__build_mesh(meth, geoms, geom_name, ghost)

    def add_geoms_merged(self, geoms, mesh, geom_name):
        for geom in geoms:
            geom.flattenLight()
            for _geom in [g.decompose() for g in geom.node().getGeoms()]:
                mesh.addGeom(_geom, geom.getTransform(self.model))
        return geom_name

    def add_geoms_unmerged(self, geoms, mesh, geom_name):
        geoms.flattenLight()
        for _geom in [g.decompose() for g in geoms.node().getGeoms()]:
            mesh.addGeom(_geom, geoms.getTransform(self.model))
        return geoms.get_name()

    def __build_mesh(self, meth, geoms, geom_name, ghost):
        mesh = BulletTriangleMesh()
        name = meth(geoms, mesh, geom_name)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.__build(shape, name, ghost)

    def __build(self, shape, geom_name, ghost):
        if ghost:
            ncls = BulletGhostNode
            meth = eng.phys.world_phys.attachGhost
            lst = self.ghosts
        else:
            ncls = BulletRigidBodyNode
            meth = eng.phys.world_phys.attachRigidBody
            lst = self.rigid_bodies
        nodepath = eng.gfx.world_np.attachNewNode(ncls(geom_name))
        self.nodes += [nodepath]
        nodepath.node().addShape(shape)
        meth(nodepath.node())
        lst += [nodepath.node()]
        nodepath.node().notifyCollisions(True)

    def __set_corners(self):
        corners = ['topleft', 'topright', 'bottomright', 'bottomleft']
        pmod = self.model
        self.corners = [pmod.find('**/Minimap' + crn) for crn in corners]

    def __set_waypoints(self):
        wp_root = self.model.find('**/Waypoints')
        _waypoints = wp_root.findAllMatches('**/Waypoint*')
        self.waypoints = {}
        self.bonuses = []
        for w_p in _waypoints:
            wpstr = '**/Waypoint'
            prevs = w_p.getTag('prev').split(',')
            lst_wp = [wp_root.find(wpstr + idx) for idx in prevs]
            self.waypoints[w_p] = lst_wp
            self.bonuses += [Bonus(w_p.get_pos())]

    def __hide_models(self):
        for mod in ['Road', 'Offroad', 'Wall', 'Respawn', 'Slow', 'Goal']:
            models = self.model.findAllMatches('**/%s*' % mod)
            map(lambda mod: mod.hide(), models)

    def get_start_pos(self, i):
        start_pos = (0, 0, 0)
        start_pos_hpr = (0, 0, 0)
        node_str = '**/Start' + str(i + 1)
        start_pos_node = self.model.find(node_str)
        if start_pos_node:
            start_pos = start_pos_node.get_pos()
            start_pos_hpr = start_pos_node.get_hpr()
        return start_pos, start_pos_hpr

    @property
    def lrtb(self):
        return self.corners[0].getX(), self.corners[1].getX(), \
            self.corners[0].getY(), self.corners[3].getY()

    def destroy(self):
        self.model.removeNode()
        map(lambda chl: chl.remove_node(), self.nodes)
        map(eng.phys.world_phys.remove_rigid_body, self.rigid_bodies)
        map(eng.phys.world_phys.remove_ghost, self.ghosts)
        self.corners = self.rigid_bodies = self.ghosts = self.nodes = \
            self.waypoints = None
        map(lambda bon: bon.destroy(), self.bonuses)
