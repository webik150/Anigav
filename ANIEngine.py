import os.path
import pygame as pg
from pygame.locals import *
import numpy as np
from OpenGL.GL import *
import glm
import pywavefront as pf
from ctypes import c_void_p

DEBUG = False


class mesh:
    def __init__(self, msh, path, vertices, vao):
        glBindVertexArray(vao)
        self.vertices = np.array(vertices, dtype=np.float32).flatten()
        self.indicesEdges = np.array(msh.edges, dtype=np.uint32).flatten()
        self.indicesFaces = np.array(msh.faces, dtype=np.uint32).flatten()
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        self.eaoEdges = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.eaoEdges)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indicesEdges, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        self.eaoFaces = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.eaoFaces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indicesFaces, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        self.path = path
        glBindVertexArray(0)

    def bind_edges(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.eaoEdges)

    def bind_faces(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.eaoFaces)

    @staticmethod
    def unbind():
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)


class shader:
    def __init__(self, vertexPath, fragPath, name):
        self.id = 0
        self.vertexPath = vertexPath
        self.vertexId = 0
        self.fragPath = fragPath
        self.fragId = 0
        self.name = name
        shaders[self.name] = self
        self.load()

    def delete(self):
        glDeleteShader(self.fragId)
        glDeleteShader(self.vertexId)
        glDeleteProgram(self.id)

    def load(self):
        global shaders
        self.id = glCreateProgram()
        self.vertexId = createShader(self.id, self.vertexPath, GL_VERTEX_SHADER)
        self.fragId = createShader(self.id, self.fragPath, GL_FRAGMENT_SHADER)
        glLinkProgram(self.id)

    def reload(self):
        self.delete()
        self.load()

    def reloadvs(self):
        glDetachShader(self.id, self.vertexId)
        file = open(self.vertexPath, 'r')
        lines = file.readlines()
        file.close()
        if len(lines) <= 0:
            return False
        glShaderSource(self.vertexId, lines)
        glCompileShader(self.vertexId)
        status = glGetShaderiv(self.vertexId, GL_COMPILE_STATUS)
        # if compilation failed, print the log
        if not status:
            # display the log
            print(glGetShaderInfoLog(self.vertexId))
        else:
            # all is well, so attach the shader to the program
            glAttachShader(self.id, self.vertexId)

    def reloadfs(self):
        glDetachShader(self.id, self.fragId)
        file = open(self.fragPath, 'r')
        lines = file.readlines()
        file.close()
        if len(lines) <= 0:
            return False
        glShaderSource(self.fragId, lines)
        glCompileShader(self.fragId)
        status = glGetShaderiv(self.fragId, GL_COMPILE_STATUS)
        if not status:
            print(glGetShaderInfoLog(self.fragId))
        else:
            glAttachShader(self.id, self.fragId)


class aniSettings:
    def __init__(self):
        self.resolution = (0, 0)
        self.timeSinceStart = 0
        self.clock = pg.time.Clock()
        self.vao = 0


shaders = {}


def aniInit():
    global DEBUG
    settings = aniSettings()
    settings.projection = glm.mat4(1)
    settings.world = glm.mat4(1)
    pg.init()
    pg.display.set_mode(size=(0, 0), flags=FULLSCREEN | DOUBLEBUF | OPENGL, display=1 if DEBUG else 0)
    settings.resolution = pg.display.get_window_size()
    settings.render_res = 400
    # glEnableClientState(GL_VERTEX_ARRAY)
    # glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    settings.vao = glGenVertexArrays(1)
    initRenderBuffers(settings)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glPointSize(5.0)
    glLineWidth(0.5)
    return settings


def createShader(program, path, type):
    file = open(path, 'r')
    lines = file.readlines()
    file.close()
    if len(lines) <= 0:
        return False
    sh = glCreateShader(type)
    glShaderSource(sh, lines)
    glCompileShader(sh)
    # retrieve the compile status
    status = glGetShaderiv(sh, GL_COMPILE_STATUS)
    # if compilation failed, print the log
    if not status:
        # display the log
        print(glGetShaderInfoLog(sh))
    else:
        # all is well, so attach the shader to the program
        glAttachShader(program, sh)
    return sh


def refresh_shaders():
    for name in shaders:
        sh = shaders[name]
        sh.reload()


def load_obj(name, vao):
    origname = name
    name = os.path.join("models", name)
    if os.path.isdir(name):
        objs = []
        for files in os.listdir(name):
            root, ext = os.path.splitext(files)
            if os.path.isfile(os.path.join(name, files)) and ext == ".obj":
                objs.append(os.path.join(name, files))
        return [load_obj_at_path(origname + str(i), objs[i], vao) for i in range(len(objs))]
    elif os.path.exists(name + ".obj"):
        return load_obj_at_path(name, name + ".obj", vao)
    elif os.path.exists(name):
        return load_obj_at_path(name, name, vao)


def load_obj_at_path(name, path, vao):
    obj = pf.Wavefront(path, collect_faces=True)
    meshes = []
    for msh in obj.meshes:
        obj.meshes[msh].edges = []
        for triangle in obj.meshes[msh].faces:
            obj.meshes[msh].edges.append([triangle[0], triangle[1]])
            obj.meshes[msh].edges.append([triangle[1], triangle[2]])
            obj.meshes[msh].edges.append([triangle[0], triangle[2]])
        obj.meshes[msh].edges = np.unique(obj.meshes[msh].edges, axis=0)
        meshes.append(mesh(obj.meshes[msh], name, obj.vertices, vao))
    return meshes


def initRenderBuffers(settings):
    settings.fbo = glGenFramebuffers(1)
    settings.fgt = glGenTextures(1)
    settings.dbo = glGenRenderbuffers(1)
    settings.dfbo = glGetIntegerv(GL_FRAMEBUFFER_BINDING)

    glBindTexture(GL_TEXTURE_2D, settings.fgt)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, settings.render_res, settings.render_res, 0, GL_RGBA, GL_UNSIGNED_BYTE,
                 c_void_p(0))

    glBindRenderbuffer(GL_RENDERBUFFER, settings.dbo)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT16, settings.render_res, settings.render_res)

    glBindFramebuffer(GL_FRAMEBUFFER, settings.fbo)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, settings.fgt, 0)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, settings.dbo)

    glBindTexture(GL_TEXTURE_2D, 0)
    glBindRenderbuffer(GL_RENDERBUFFER, 0)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
