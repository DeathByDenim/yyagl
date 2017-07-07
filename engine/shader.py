from panda3d.core import AmbientLight, DirectionalLight, PointLight, \
    Spotlight, LVector4f, LVector3f, Vec3, Shader, Texture, WindowProperties,\
    FrameBufferProperties, GraphicsPipe, GraphicsOutput, NodePath, PandaNode
from direct.filter.FilterManager import FilterManager
from ..singleton import Singleton


class ShaderSetter(object):

    @staticmethod
    def build(lgt):
        cls2sett = {
            AmbientLight: ShaderSetterAmbient,
            PointLight: ShaderSetterPointLight,
            DirectionalLight: ShaderSetterDirectionalLight,
            Spotlight: ShaderSetterSpotlight}
        return cls2sett[lgt.node().__class__]()


class ShaderSetterAmbient(ShaderSetter):

    @staticmethod
    def set(pref, lgt):
        render.set_shader_input(pref + 'amb', lgt.node().get_color())


class ShaderSetterPointLight(ShaderSetter):

    @staticmethod
    def set(pref, lgt):
        lgt_pos = lgt.get_mat(base.cam).xform(LVector4f(0, 0, 0, 1))
        render.set_shader_input(pref + 'pos', lgt_pos)
        render.set_shader_input(pref + 'diff', lgt.node().get_color())
        render.set_shader_input(pref + 'spec', lgt.node().get_color())


class ShaderSetterDirectionalLight(ShaderSetter):

    @staticmethod
    def set(pref, lgt):
        lgt_pos = lgt.get_pos()
        lgt_vec = -render.get_relative_vector(lgt, Vec3(0, 1, 0))
        lgt_pos = LVector4f(lgt_vec[0], lgt_vec[1], lgt_vec[2], 0)
        render.set_shader_input(pref + 'pos', lgt_pos)
        render.set_shader_input(pref + 'diff', lgt.node().get_color())
        render.set_shader_input(pref + 'spec', lgt.node().get_color())


class ShaderSetterSpotlight(ShaderSetter):

    @staticmethod
    def set(pref, lgt):
        lgt_pos = lgt.get_mat(base.cam).xform(LVector4f(0, 0, 0, 1))
        lgt_vec = base.cam.get_relative_vector(lgt, Vec3(0, 1, 0))
        render.set_shader_input(pref + 'pos', lgt_pos)
        render.set_shader_input(pref + 'diff', lgt.node().get_color())
        render.set_shader_input(pref + 'spec', lgt.node().get_color())
        render.set_shader_input(pref + 'dir', lgt_vec)
        render.set_shader_input(pref + 'exp', lgt.node().get_exponent())
        cutoff = lgt.node().getLens().getFov()[0]
        render.set_shader_input(pref + 'cutoff', cutoff)


class ShaderMgr(object):

    __metaclass__ = Singleton

    def __init__(self, shaders, gamma):
        self.lights = []
        self.gamma = gamma
        self.buffer = None
        self.lcam = None
        if shaders:
            self.setup_post_fx()

    def __set_lgt(self, lgt, col):
        lgt.set_color(col)
        self.lights += [render.attach_new_node(lgt)]
        render.set_light(self.lights[-1])

    def set_amb_lgt(self, col):
        self.__set_lgt(AmbientLight('ambient light'), col)

    def set_dir_lgt(self, col, direction):
        self.__set_lgt(DirectionalLight('directional light'), col)
        self.lights[-1].set_hpr(*direction)

    def set_pnt_lgt(self, col, pos):
        self.__set_lgt(PointLight('point light'), col)
        self.lights[-1].set_pos(*pos)

    def set_spotlight(self, col, exp, cutoff, pos, look_at):
        self.__set_lgt(Spotlight('spotlight'), col)
        self.lights[-1].set_exponent(exp)
        self.lights[-1].get_lens().set_fov(cutoff, cutoff)
        self.lights[-1].set_pos(*pos)
        self.lights[-1].look_at(*look_at)

    @staticmethod
    def set_default_args(idx):
        pref = 'lights[%s].' % idx
        render.set_shader_input(pref + 'pos', LVector4f(0, 0, 0, 1))
        render.set_shader_input(pref + 'amb', LVector3f(0, 0, 0))
        render.set_shader_input(pref + 'diff', LVector3f(0, 0, 0))
        render.set_shader_input(pref + 'spec', LVector3f(0, 0, 0))
        render.set_shader_input(pref + 'dir', LVector3f(0, 0, 0))
        render.set_shader_input(pref + 'exp', .0)
        render.set_shader_input(pref + 'cutoff', .0)

    def set_lgt_args(self, idx, lgt):
        self.set_default_args(idx)
        ShaderSetter.build(lgt).set('lights[%s].' % idx, lgt)

    def clear_lights(self):
        for lgt in self.lights:
            eng.base.render.clear_light(lgt)
            lgt.removeNode()
        self.lights = []

    def setup_post_fx(self):
        self.filter_mgr = FilterManager(base.win, base.cam)
        rendered_scene = Texture()
        aa_scene = Texture()
        filtered_scene = Texture()
        filter_quad = self.filter_mgr.renderQuadInto(colortex=filtered_scene)
        aa_quad = self.filter_mgr.renderQuadInto(colortex=aa_scene)
        final_quad = self.filter_mgr.renderSceneInto(colortex=rendered_scene)
        with open('yyagl/assets/shaders/filter.vert') as f:
            fvert = f.read()
        with open('yyagl/assets/shaders/filter.frag') as f:
            ffrag = f.read()
        filter_quad.set_shader(Shader.make(Shader.SLGLSL, fvert, ffrag))
        filter_quad.set_shader_input('in_tex', rendered_scene)
        with open('yyagl/assets/shaders/fxaa.vert') as f:
            avert = f.read()
        with open('yyagl/assets/shaders/fxaa.frag') as f:
            afrag = f.read()
        aa_quad.set_shader(Shader.make(Shader.SLGLSL, avert, afrag))
        aa_quad.set_shader_input('in_tex', filtered_scene)
        with open('yyagl/assets/shaders/pass.frag') as f:
            pfrag = f.read()
        final_quad.set_shader(Shader.make(Shader.SLGLSL, fvert, pfrag))
        final_quad.set_shader_input('gamma', self.gamma)
        final_quad.set_shader_input('in_tex', aa_scene)

    def apply(self):
        winprops = WindowProperties.size(2048, 2048)
        props = FrameBufferProperties()
        props.set_rgb_color(1)
        props.set_alpha_bits(1)
        props.set_depth_bits(1)
        lbuffer = base.graphicsEngine.make_output(
            base.pipe, 'offscreen buffer', -2, props, winprops,
            GraphicsPipe.BFRefuseWindow, base.win.getGsg(), base.win)
        self.buffer = lbuffer
        ldepthmap = Texture()
        lbuffer.addRenderTexture(ldepthmap, GraphicsOutput.RTMBindOrCopy,
                                 GraphicsOutput.RTPDepthStencil)
        ldepthmap.set_minfilter(Texture.FTShadow)
        ldepthmap.set_magfilter(Texture.FTShadow)

        base.camLens.set_near_far(1.0, 10000)
        base.camLens.set_fov(75)

        self.lcam = base.makeCamera(lbuffer)
        self.lcam.node().set_scene(render)
        self.lcam.node().get_lens().set_fov(45)
        self.lcam.node().get_lens().set_near_far(1, 100)

        render.set_shader_input('light', self.lcam)
        render.set_shader_input('depthmap', ldepthmap)
        render.set_shader_input('ambient', .15, .15, .15, 1.0)

        lci = NodePath(PandaNode('light camera initializer'))
        with open('yyagl/assets/shaders/caster.vert') as fvert:
            vert = fvert.read()
        with open('yyagl/assets/shaders/caster.frag') as ffrag:
            frag = ffrag.read()
        lci.set_shader(Shader.make(Shader.SLGLSL, vert, frag))
        self.lcam.node().set_initial_state(lci.get_state())

        mci = NodePath(PandaNode('main camera initializer'))
        with open('yyagl/assets/shaders/main.vert') as fvert:
            vert = fvert.read()
        with open('yyagl/assets/shaders/main.frag') as ffrag:
            frag = ffrag.read()
        frag = frag.replace('<LIGHTS>', str(len(self.lights)))
        # use PTALVecBaseX instead
        # setShaderInput('vec3argname', PTALVecBase3(((0, 0, 0), (1, 1, 1))))
        render.set_shader(Shader.make(Shader.SLGLSL, vert, frag))
        render.set_shader_input('num_lights', len(self.lights))
        map(lambda lgt: self.set_lgt_args(*lgt), enumerate(self.lights))
        mci.setShader(Shader.make(Shader.SLGLSL, vert, frag))
        base.cam.node().set_initial_state(mci.getState())

        self.lcam.set_pos(15, 30, 45)
        self.lcam.look_at(0, 15, 0)
        self.lcam.node().get_lens().set_near_far(1, 100)

    def toggle_shader(self):
        if render.get_shader():
            render.set_shader_off()
            render.set_shader_auto()
            return
        self.apply()

    def destroy(self):
        self.clear_lights()
