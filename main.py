import glfw
import numpy as np
import trimesh
from OpenGL.GL import *
from pyrr import Matrix44, Vector3
from PIL import Image
import ctypes

# Initialize GLFW
glfw.init()
if not glfw.init():
    raise Exception("GLFW can not be initialized!")

# Create a windowed mode window and its OpenGL context
window = glfw.create_window(1920, 1080, "Synthetic Image Generator", None, None)
if not window:
    glfw.terminate()
    raise Exception("GLFW window can not be created!")

# Make the window's context current
glfw.make_context_current(window)
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)
glCullFace(GL_BACK)
glFrontFace(GL_CCW)
glEnable(GL_POLYGON_OFFSET_FILL)
glPolygonOffset(1.0, 1.0)

def load_model(path):
    mesh = trimesh.load_mesh(path)
    vertices = np.array(mesh.vertices, dtype=np.float32)
    faces = np.array(mesh.vertex_normals, dtype=np.float32)
    return vertices, faces

satellite_vertices, satellite_faces = load_model('teapot.stl')

vertex_shader_source = """
#version 330 core
layout(location = 0) in vec3 position;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);

}
"""

fragment_shader_source = """
#version 330 core
out vec4 FragColor;
void main()
{
    FragColor = vec4(1.0, 1.0, 1.0, 1.0); // White color
}
"""

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise Exception(glGetShaderInfoLog(shader))
    return shader

vertex_shader = compile_shader(vertex_shader_source, GL_VERTEX_SHADER)
fragment_shader = compile_shader(fragment_shader_source, GL_FRAGMENT_SHADER)

shader_program = glCreateProgram()
glAttachShader(shader_program, vertex_shader)
glAttachShader(shader_program, fragment_shader)
glLinkProgram(shader_program)

if not glGetProgramiv(shader_program, GL_LINK_STATUS):
    raise Exception(glGetProgramInfoLog(shader_program))

glDeleteShader(vertex_shader)
glDeleteShader(fragment_shader)

# Generate and bind a Vertex Array Object (VAO)
VAO = glGenVertexArrays(1)
glBindVertexArray(VAO)

# Generate and bind a Vertex Buffer Object (VBO)
VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, satellite_vertices.nbytes, satellite_vertices, GL_STATIC_DRAW)

# Generate and bind an Element Buffer Object (EBO)
EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, satellite_faces.nbytes, satellite_faces, GL_STATIC_DRAW)

# Enable the vertex attribute and specify the layout
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * satellite_vertices.itemsize, ctypes.c_void_p(0))

def get_view_matrix(camera_pos, camera_target, camera_up):
    return Matrix44.look_at(camera_pos, camera_target, camera_up)

def get_projection_matrix(fov, aspect_ratio, near, far):
    return Matrix44.perspective_projection(fov, aspect_ratio, near, far)

camera_pos = Vector3([0.0, -30.0, 1.0])
camera_target = Vector3([0.0, 0.0, 0.0])
camera_up = Vector3([0.0, 1.0, 0.0])
view_matrix = get_view_matrix(camera_pos, camera_target, camera_up)
projection_matrix = get_projection_matrix(90.0, 1920/1080, 0.1, 200.0)

def render():
    model_matrix = Matrix44.identity()

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Use the shader program
        glUseProgram(shader_program)

        # Set the uniform variables
        model_loc = glGetUniformLocation(shader_program, "model")
        view_loc = glGetUniformLocation(shader_program, "view")
        proj_loc = glGetUniformLocation(shader_program, "projection")
        
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_matrix)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection_matrix)

        # Draw the satellite model
        glBindVertexArray(VAO)
        glDrawArrays(GL_TRIANGLES, 0, len(satellite_vertices))

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    render()