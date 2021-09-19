from OpenGL.GL import *
import glm
import pywavefront as pf
from ctypes import c_void_p


class SceneData:
    def __init__(self, width, height):
        self.world = glm.mat4(1)
        self.projection = glm.perspective(52.0, (width / height), 1.000, 100.0)


class Scene:

    def __init__(self):
        self.objects = []

    def draw(self, settings, data: SceneData):
        glBindVertexArray(settings.vao)
        glBindVertexArray(0)


class TestScene1(Scene):

    def __init__(self, settings):
        super().__init__()
        from ANIEngine import GameObject
        self.objects = [GameObject.from_file("dagger.obj", "matrix", settings)]
        self.objects[0].model = glm.translate(self.objects[0].model, glm.vec3(0, 0, -5))
        self.objects[0].model = glm.scale(self.objects[0].model, glm.vec3(1))
        self.objects[0].wireframe = True

    def draw(self, data: SceneData, settings):
        glBindVertexArray(settings.vao)
        for go in self.objects:
            if not go.wireframe:
                self.objects[0].model = glm.rotate(self.objects[0].model, glm.radians(settings.dtime * 15),
                                                   glm.vec3(0, 1, 0))
                self.objects[0].model = glm.rotate(self.objects[0].model, glm.radians(settings.dtime * 10),
                                                   glm.vec3(1, 0, 0))
                go.bind_faces()
                go.set_default_uniforms(data, settings)
                glDrawElements(GL_TRIANGLES, len(go.mesh.indicesFaces) * 3, GL_UNSIGNED_INT, c_void_p(0))
            else:
                go.bind_edges()
                self.objects[0].model = glm.rotate(self.objects[0].model, glm.radians(settings.dtime * 15),
                                                   glm.vec3(0, 1, 0))
                self.objects[0].model = glm.rotate(self.objects[0].model, glm.radians(settings.dtime * 10 * (settings.inputs.channels[1].get_value()+1)*10),
                                                   glm.vec3(1, 0, 0))
                go.set_default_uniforms(data, settings)
                glDrawElements(GL_LINES, len(go.mesh.indicesEdges) * 2, GL_UNSIGNED_INT, c_void_p(0))
            go.unbind()
        glBindVertexArray(0)
