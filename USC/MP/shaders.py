import OpenGL.GL as gl


__author__ = 'mavinm'

SHADER2STRING = {gl.GL_VERTEX_SHADER: "vertex",
                 gl.GL_GEOMETRY_SHADER: "geometry",
                 gl.GL_FRAGMENT_SHADER: "fragment"}


class ShaderException(Exception):
    pass


class ShaderCreator():

    def createShader(self, vertex_loc, fragment_loc):
        shader = gl.glCreateProgram()
        shader_list = []
        shader_list.append(self.compileShader(gl.GL_VERTEX_SHADER, vertex_loc))
        shader_list.append(self.compileShader(gl.GL_FRAGMENT_SHADER, fragment_loc))

        for shade in shader_list:
            gl.glAttachShader(shader, shade)

        self.linkShader(shader)

        for shade in shader_list:
            gl.glDetachShader(shader, shade)

        return shader

    def compileShader(self, shader_type, shader_file):
        shader = gl.glCreateShader(shader_type)
        file = open(shader_file, 'r')
        shader_str = file.readlines()
        file.close()
        gl.glShaderSource(shader, shader_str)
        gl.glCompileShader(shader)
        status = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        if not status:
            log = gl.glGetShaderInfoLog(shader)
            shader_name = SHADER2STRING[shader_type]
            raise ShaderException("Compile failure in {} shader:\n{}\n".format(shader_name, log))

        return shader

    def linkShader(self, shader):
        gl.glLinkProgram(shader)
        status = gl.glGetProgramiv(shader, gl.GL_LINK_STATUS)
        if not status:
            log = gl.glGetProgramInfoLog(shader)
            raise ShaderException, "Linking failue:\n{}\n".format(log)