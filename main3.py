import glfw
import OpenGL.GL as gl
import OpenGL.GLU as glu
import numpy as np
import trimesh

# Function to load the STL file using trimesh
def load_stl(file_path):
    mesh = trimesh.load(file_path)
    vertices = np.array(mesh.vertices)
    faces = np.array(mesh.faces)
    return vertices, faces

# Function to initialize OpenGL settings
def init_gl():
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)
    gl.glClearDepth(1.0)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LEQUAL)
    gl.glShadeModel(gl.GL_SMOOTH)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(45, 800 / 600, 0.1, 100.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)

# Function to draw the mesh
def draw_mesh(vertices, faces):
    gl.glBegin(gl.GL_TRIANGLES)
    for face in faces:
        for vertex in face:
            gl.glVertex3fv(vertices[vertex])
    gl.glEnd()

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

    # Load the STL file
    vertices, faces = load_stl('teapot.stl')  # Replace 'your_model.stl' with your STL file path

    # Define camera position and orientation
    camera_pos = np.array([30.0, 30.0, 20.0])
    camera_look_at = np.array([0.0, 0.0, 0.0])
    camera_up = np.array([0.0, 0.0, 1.0])

    # Initialize OpenGL settings
    init_gl()

    # Main loop
    while not glfw.window_should_close(window):
        # Render here, e.g. using pyOpenGL
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()

        # Apply camera transformation
        glu.gluLookAt(
            camera_pos[0], camera_pos[1], camera_pos[2],
            camera_look_at[0], camera_look_at[1], camera_look_at[2],
            camera_up[0], camera_up[1], camera_up[2]
        )

        # Rotate the model
        # gl.glRotatef(glfw.get_time() * 50, 0, 0, 1)

        # Draw the mesh
        draw_mesh(vertices, faces)

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()