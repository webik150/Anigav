from ANIEngine import *
from ctypes import c_void_p

from ANIScene import SceneData, TestScene1

settings = aniSettings()


def main():
    global settings
    settings = aniInit()
    scene_data = SceneData(settings.resolution[0], settings.resolution[1])

    scene_data.msh = shader("matrixGreen.vert", "matrixGreen.frag", "msh")
    scene_data.matrix = shader("matrix.vert", "matrix.frag", "matrix")
    scene_data.quadSh = shader("screen.vert", "screen.frag", "quad")

    settings.currentScene = TestScene1(settings)

    full_res = min(settings.resolution)
    aspect = settings.resolution[0] / settings.resolution[1]

    scene_data.res = 0
    scene_data.quad = pf.Wavefront("./models/quad.obj", collect_faces=True)
    glBindVertexArray(settings.vao)
    scene_data.quad.vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, scene_data.quad.vbo)
    glBufferData(GL_ARRAY_BUFFER, np.array(scene_data.quad.materials['None'].vertices, dtype=np.float32),
                 GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                settings.inputs.stop()
                pg.quit()
                quit()
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.key.key_code('r'):
                    refresh_shaders()
                if event.key == pg.key.key_code('l'):
                    scene_data.res = (scene_data.res + 1) % 9
                if event.key == pg.key.key_code('escape'):
                    settings.inputs.stop()
                    pg.quit()
                    quit()
                    return
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 3:
                    settings.inputs.stop()
                    pg.quit()
                    quit()
                    return
        settings.dtime = settings.clock.get_time() / 1000.0

        glBindFramebuffer(GL_FRAMEBUFFER, settings.fbo)
        glViewport(0, 0, settings.render_res, settings.render_res)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        settings.currentScene.draw(scene_data, settings)

        glBindFramebuffer(GL_FRAMEBUFFER, settings.dfbo)
        glBindTexture(GL_TEXTURE_2D, 0)
        glClearColor(1.0, 0.0, 0.0, 1.0)
        glViewport(0, 0, int(full_res * aspect), full_res)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBindVertexArray(settings.vao)
        glUseProgram(scene_data.quadSh.id)
        glBindBuffer(GL_ARRAY_BUFFER, scene_data.quad.vbo)
        glEnableVertexAttribArray(glGetAttribLocation(scene_data.quadSh.id, "a_position"))
        glEnableVertexAttribArray(glGetAttribLocation(scene_data.quadSh.id, "a_texcoord"))
        glVertexAttribPointer(glGetAttribLocation(scene_data.quadSh.id, "a_position"), 3, GL_FLOAT, GL_FALSE, 32,
                              c_void_p(20))
        glVertexAttribPointer(glGetAttribLocation(scene_data.quadSh.id, "a_texcoord"), 2, GL_FLOAT, False, 32,
                              c_void_p(0))
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, settings.fgt)
        glUniform1f(glGetUniformLocation(scene_data.quadSh.id, "analog0"), settings.inputs.channels[0].get_value())
        glUniform1f(glGetUniformLocation(scene_data.quadSh.id, "analog1"), settings.inputs.channels[1].get_value())
        glUniform1f(glGetUniformLocation(scene_data.quadSh.id, "analog2"), settings.inputs.channels[2].get_value())
        glUniform1f(glGetUniformLocation(scene_data.quadSh.id, "analog3"), settings.inputs.channels[3].get_value())
        glUniform1i(glGetUniformLocation(scene_data.quadSh.id, "s_diffuse"), 0)
        glUniform1f(glGetUniformLocation(scene_data.quadSh.id, "time"), settings.timeSinceStart)
        glUniform1i(glGetUniformLocation(scene_data.quadSh.id, "mode"), 0)
        glUniform2f(glGetUniformLocation(scene_data.quadSh.id, "screenSize"), settings.resolution[0],
                    settings.resolution[1])

        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        pg.display.flip()

        settings.timeSinceStart += settings.clock.get_time() / 1000
        settings.clock.tick(60)


main()
