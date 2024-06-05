import glfw
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GL.shaders as shaders
import numpy as np
import trimesh
import ctypes

# Function to load the STL file using trimesh
def load_stl(file_path):
    mesh = trimesh.load(file_path)
    vertices = np.array(mesh.vertices, dtype=np.float32)
    faces = np.array(mesh.faces, dtype=np.uint32)
    normals = np.array(mesh.vertex_normals, dtype=np.float32)
    return vertices, faces, normals

def compile_shader(source, shader_type):
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)
    if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
        error = gl.glGetShaderInfoLog(shader).decode()
        raise RuntimeError(f"Shader compilation error: {error}")
    return shader

# Function to initialize OpenGL settings
def init_gl(vertices, faces, normals):
    # Create and compile shaders
    with open("vertex_shader.glsl") as f:
        vertex_shader_source = f.read()
    with open("fragment_shader.glsl") as f:
        fragment_shader_source = f.read()
    
    vertex_shader = compile_shader(vertex_shader_source, gl.GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_shader_source, gl.GL_FRAGMENT_SHADER)
    
    shader_program = gl.glCreateProgram()
    gl.glAttachShader(shader_program, vertex_shader)
    gl.glAttachShader(shader_program, fragment_shader)
    gl.glLinkProgram(shader_program)
    
    if not gl.glGetProgramiv(shader_program, gl.GL_LINK_STATUS):
        error = gl.glGetProgramInfoLog(shader_program).decode()
        raise RuntimeError(f"Program linking error: {error}")
    
    gl.glUseProgram(shader_program)

    # Create buffers and arrays
    VAO = gl.glGenVertexArrays(1)
    VBO = gl.glGenBuffers(1)
    EBO = gl.glGenBuffers(1)

    gl.glBindVertexArray(VAO)

    # Vertex buffer
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    vertex_data = np.hstack((vertices, normals)).astype(np.float32)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, gl.GL_STATIC_DRAW)

    # Element buffer
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, EBO)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, faces.nbytes, faces, gl.GL_STATIC_DRAW)

    # Position attribute
    position = gl.glGetAttribLocation(shader_program, 'position')
    gl.glVertexAttribPointer(position, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * vertex_data.itemsize, ctypes.c_void_p(0))
    gl.glEnableVertexAttribArray(position)

    # Normal attribute
    normal = gl.glGetAttribLocation(shader_program, 'normal')
    gl.glVertexAttribPointer(normal, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * vertex_data.itemsize, ctypes.c_void_p(3 * vertex_data.itemsize))
    gl.glEnableVertexAttribArray(normal)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0)

    return shader_program, VAO

# Function to draw the mesh
def draw_mesh(VAO, faces_count):
    gl.glBindVertexArray(VAO)
    gl.glDrawElements(gl.GL_TRIANGLES, faces_count * 3, gl.GL_UNSIGNED_INT, None)
    gl.glBindVertexArray(0)

def create_view_matrix(camera_pos, camera_look_at, camera_up):
    f = np.array(camera_look_at - camera_pos)
    f = f / np.linalg.norm(f)
    
    u = np.array(camera_up)
    u = u / np.linalg.norm(u)
    
    s = np.cross(f, u)
    s = s / np.linalg.norm(s)
    
    u = np.cross(s, f)

    view = np.matrix([
        [s[0],  u[0], -f[0], 0.0],
        [s[1],  u[1], -f[1], 0.0],
        [s[2],  u[2], -f[2], 0.0],
        [-np.dot(s, camera_pos), -np.dot(u, camera_pos), np.dot(f, camera_pos), 1.0]
    ])
    
    return view

def create_projection_matrix(fov, aspect, near, far):
    f = 1.0 / np.tan(fov / 2.0)
    proj = np.matrix([
        [f / aspect, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, (far + near) / (near - far), -1.0],
        [0.0, 0.0, (2 * far * near) / (near - far), 0.0]
    ])
    
    return proj    

def main():
    # Initialize glfw
    if not glfw.init():
        return

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(1920, 1080, "STL Viewer", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)

    # Enable depth testing and face culling
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LEQUAL)
    gl.glEnable(gl.GL_CULL_FACE)
    gl.glCullFace(gl.GL_BACK)

    # Load the STL file
    vertices, faces, normals = load_stl('teapot.stl')  # Replace 'your_model.stl' with your STL file path

    # Initialize OpenGL settings
    shader_program, VAO = init_gl(vertices, faces, normals)
    faces_count = len(faces)

    # Define camera position and orientation
    camera_pos = np.array([20.0, 20.0, 20.0])
    camera_look_at = np.array([0.0, 0.0, 0.0])
    camera_up = np.array([0.0, 0.0, 1.0])

    # Get Light source Coordinates

    # Uniform locations
    model_loc = gl.glGetUniformLocation(shader_program, 'model')
    view_loc = gl.glGetUniformLocation(shader_program, 'view')
    projection_loc = gl.glGetUniformLocation(shader_program, 'projection')
    light_pos_loc = gl.glGetUniformLocation(shader_program, 'lightPos')
    view_pos_loc = gl.glGetUniformLocation(shader_program, 'viewPos')
    light_color_loc = gl.glGetUniformLocation(shader_program, 'lightColor')
    object_color_loc = gl.glGetUniformLocation(shader_program, 'objectColor')   

    # Create view and projection matrices
    view = create_view_matrix(camera_pos, camera_look_at, camera_up)
    projection = create_projection_matrix(45, 1920 / 1080, 0.1, 100.0)

    # Main loop
    while not glfw.window_should_close(window):
        # Render here, e.g. using pyOpenGL
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # Use the shader program
        gl.glUseProgram(shader_program)

        # Camera transformations
        glu.gluLookAt(
            camera_pos[0], camera_pos[1], camera_pos[2],
            camera_look_at[0], camera_look_at[1], camera_look_at[2],
            camera_up[0], camera_up[1], camera_up[2]
        )

        model = np.identity(4, dtype=np.float32)

        # Set uniforms
        gl.glUniformMatrix4fv(model_loc, 1, gl.GL_FALSE, model)
        gl.glUniformMatrix4fv(view_loc, 1, gl.GL_FALSE, view)
        gl.glUniformMatrix4fv(projection_loc, 1, gl.GL_FALSE, projection)

        gl.glUniform3f(light_pos_loc, 10.0, 0.0, 0.0)
        gl.glUniform3f(view_pos_loc, camera_pos[0], camera_pos[1], camera_pos[2])
        gl.glUniform3f(light_color_loc, 1.0, 1.0, 1.0)
        gl.glUniform3f(object_color_loc, 0.0, 1.0, 0.0)

        # Draw the mesh
        draw_mesh(VAO, faces_count)

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()