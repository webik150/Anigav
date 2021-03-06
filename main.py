from ANIEngine import *
from OpenGL import GL
from ctypes import c_void_p
import math

settings = aniSettings()

model = glm.mat4(1)


def drawScene(sceneData):
    glBindVertexArray(settings.vao)
    glUseProgram(sceneData.msh.id)
    sceneData.spheres[sceneData.res][0].bind_faces()
    glEnableVertexAttribArray(glGetAttribLocation(sceneData.msh.id, "position"))
    glVertexAttribPointer(glGetAttribLocation(sceneData.msh.id, "position"), 3, GL_FLOAT, False, 0, c_void_p(0))
    glUniformMatrix4fv(glGetUniformLocation(sceneData.msh.id, "mPVM"), 1, False,
                       (settings.projection * settings.world * model).to_list())
    glUniform1f(glGetUniformLocation(sceneData.msh.id, "val1"), math.sin(settings.timeSinceStart / 120 * 25 * math.pi))
    glUniform1f(glGetUniformLocation(sceneData.msh.id, "bpm"), settings.bpm)
    glUniform1f(glGetUniformLocation(sceneData.msh.id, "time"), settings.timeSinceStart)
    glUniform1f(glGetUniformLocation(sceneData.msh.id, "val2"),
                math.sin(settings.timeSinceStart / 120 * 25 * math.pi) / 2 + 0.5)
    glDrawElements(GL_TRIANGLES, len(sceneData.spheres[sceneData.res][0].indicesFaces) * 3, GL_UNSIGNED_INT,
                   c_void_p(0))
    sceneData.spheres[sceneData.res][0].unbind()

    glUseProgram(sceneData.matrix.id)
    sceneData.spheres[sceneData.res][0].bind_edges()
    glEnableVertexAttribArray(glGetAttribLocation(sceneData.matrix.id, "position"))
    glVertexAttribPointer(glGetAttribLocation(sceneData.matrix.id, "position"), 3, GL_FLOAT, False, 0, c_void_p(0))
    glUniformMatrix4fv(glGetUniformLocation(sceneData.matrix.id, "mPVM"), 1, False,
                       (settings.projection * settings.world * model).to_list())
    glUniform1f(glGetUniformLocation(sceneData.matrix.id, "val1"),
                math.sin(settings.timeSinceStart / 120 * 25 * math.pi))
    glUniform1f(glGetUniformLocation(sceneData.matrix.id, "bpm"), settings.bpm)
    glUniform1f(glGetUniformLocation(sceneData.matrix.id, "time"), settings.timeSinceStart)
    glUniform1f(glGetUniformLocation(sceneData.matrix.id, "val2"),
                math.sin(settings.timeSinceStart / 120 * 25 * math.pi) / 2 + 0.5)
    glDrawElements(GL_LINES, len(sceneData.spheres[sceneData.res][0].indicesEdges) * 2, GL_UNSIGNED_INT, c_void_p(0))
    sceneData.spheres[sceneData.res][0].unbind()
    glBindVertexArray(0)


class scenedata:
    def __init__(self):
        self.yeet = 0


def main():
    global settings
    global model
    settings = aniInit(1080, 10800)
    settings.projection = glm.perspective(52.0, (settings.resolution[0] / settings.resolution[1]), 1.000, 100.0)
    settings.bpm = 120

    sceneData = scenedata()
    sceneData.msh = shader("matrixGreen.vert", "matrixGreen.frag", "msh")
    sceneData.matrix = shader("matrix.vert", "matrix.frag", "matrix")
    sceneData.quadSh = shader("screen.vert", "screen.frag", "quad")

    model = glm.translate(model, glm.vec3(0, 0, -5))
    model = glm.scale(model, glm.vec3(10))

    full_res = min(settings.resolution)
    aspect = settings.resolution[0] / settings.resolution[1]

    sceneData.res = 0
    sceneData.spheres = load_obj("sphere", settings.vao)
    sceneData.quad = pf.Wavefront("./models/quad.obj", collect_faces=True)
    glBindVertexArray(settings.vao)
    sceneData.quad.vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, sceneData.quad.vbo)
    glBufferData(GL_ARRAY_BUFFER, np.array(sceneData.quad.materials['None'].vertices, dtype=np.float32), GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    sceneData.cube = load_obj("cube.obj", settings.vao)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.key.key_code('r'):
                    refresh_shaders()
                if event.key == pg.key.key_code('l'):
                    sceneData.res = (sceneData.res + 1) % 9
                if event.key == pg.key.key_code('escape'):
                    pg.quit()
                    quit()
                    return
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 3:
                    pg.quit()
                    quit()
                    return
        settings.dtime = settings.clock.get_time() / 1000.0

        glBindFramebuffer(GL_FRAMEBUFFER, settings.fbo)
        glViewport(0, 0, settings.render_res, settings.render_res)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        model = glm.rotate(model, glm.radians(settings.dtime * 15), glm.vec3(0, 1, 0))
        model = glm.rotate(model, glm.radians(settings.dtime * 10), glm.vec3(1, 0, 0))

        drawScene(sceneData)

        glBindFramebuffer(GL_FRAMEBUFFER, settings.dfbo)
        glBindTexture(GL_TEXTURE_2D, 0)
        glClearColor(1.0, 0.0, 0.0, 1.0)
        glViewport(0, 0, int(full_res * aspect), full_res)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBindVertexArray(settings.vao)
        glUseProgram(sceneData.quadSh.id)
        glBindBuffer(GL_ARRAY_BUFFER, sceneData.quad.vbo)
        glEnableVertexAttribArray(glGetAttribLocation(sceneData.quadSh.id, "a_position"))
        glEnableVertexAttribArray(glGetAttribLocation(sceneData.quadSh.id, "a_texcoord"))
        glVertexAttribPointer(glGetAttribLocation(sceneData.quadSh.id, "a_position"), 3, GL_FLOAT, GL_FALSE, 32,
                              c_void_p(20))
        glVertexAttribPointer(glGetAttribLocation(sceneData.quadSh.id, "a_texcoord"), 2, GL_FLOAT, False, 32,
                              c_void_p(0))
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, settings.fgt)
        glUniform1i(glGetUniformLocation(sceneData.quadSh.id, "s_diffuse"), 0)
        glUniform1f(glGetUniformLocation(sceneData.quadSh.id, "time"), settings.timeSinceStart)
        glUniform1i(glGetUniformLocation(sceneData.quadSh.id, "mode"), 0)
        glUniform2f(glGetUniformLocation(sceneData.quadSh.id, "screenSize"), settings.resolution[0],
                    settings.resolution[1])

        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        pg.display.flip()

        settings.timeSinceStart += settings.clock.get_time() / 1000
        settings.clock.tick(60)


main()
