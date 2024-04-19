import cv2 as cv
import moderngl as gl 

img = cv.imread("parrale_motion.PNG")

cv.imshow("Display window", img)
k = cv.waitKey(0) # Wait for a keystroke in the window

ctx = gl.get_context()
buf = ctx.buffer(b"Hello World!")  # allocated on the GPU
buf.read()
b'Hello World!'
