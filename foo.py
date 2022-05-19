from camera import VideoCamera

def gen(camera):
    while True:
        frame = camera.get_frame()
    
gen(VideoCamera())