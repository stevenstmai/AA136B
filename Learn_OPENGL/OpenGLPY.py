import pygame as pg
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader


"""
Notes: 
Philospohy of Open GL: In graphiscs #1 bottleneck, bus or link between CPU and GPU (used to store in RAM, for vertexes, and CPU wouuld send over in draw calls). In modern graphics, ship data to GPU once, then tell GPU to use resources which it has set up and ready to go
If we send vertex data and texture, GPU returns integers that represents data in memory

"""
class App:
    def __init__(self):

        # Init pygame, returns integers = number of modules init
        pg.init()

        # New window (width, height) (special flags: running opengl graphics, creates opengl context, double buffer (107E, swap))
        pg.display.set_mode((1920,1080), pg.OPENGL | pg.DOUBLEBUF)

        # Clock object, used to control framerate 
        self.clock = pg.time.Clock()

        # OpenGL init (set up most of it by pygame, we show which color we want RGB alpha)
        glClearColor(0.2, 0.2, 0.2, 1)

        # triangle stuff
        self.shader = self.createShader("Learn_OPENGL/shaders/vertex.txt", "Learn_OPENGL/shaders/fragment.txt")
        glUseProgram(self.shader)
        self.triangle = Triangle()

        self.mainLoop()

    def createShader(self, vertex_filepath: str, fragment_filepath: str) -> int:
        """
            Compile and link shader modules to make a shader program.

            Parameters:

                vertex_filepath: path to the text file storing the vertex
                                source code
                
                fragment_filepath: path to the text file storing the
                                    fragment source code
            
            Returns:

                A handle to the created shader program
        """

        with open(vertex_filepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragment_filepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def mainLoop(self):

        running = True
        while (running):
            # Check events 
            for event in pg.event.get():
                if (event.type == pg.QUIT): # if get exit event, leave loop
                    running = False

            # Color buffer, big array, color value of all pixels on screens. Binary math comes back in python opengl. Every pixel color, is a 32 bit unsinged integer. Color = RGBA (1 byte for color) (0-255) (Things are nomralized, decimnal between 0 and 1)
            glClear(GL_COLOR_BUFFER_BIT)

            glUseProgram(self.shader)
            glBindVertexArray(self.triangle.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count)

            # Flip buffer to update display
            pg.display.flip()

            # timing (60 fps)
            self.clock.tick(60)
        self.quit()

    def quit(self):
        self.triangle.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class Triangle:

    def __init__(self):

        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
            0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.5, 0.0, 0.0, 0.0, 1.0,
        )

        self.vertices = np.array(self.vertices, dtype = np.float32)
        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vb0,))

    
# Main entry point for game, if we write a program that gets bundled up with something else in a larger project, best pratice to identify the main entry popint
if __name__ == "__main__":
    myApp = App()
