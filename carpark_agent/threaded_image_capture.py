
import cv2
import time
import threading


class ThreadedImageCapture:
    def __init__(self, cam_width=1280, cam_height=720):
        self.cam_width = cam_width
        self.cam_height = cam_height

        # Set up video capture object
        self.vidcap = cv2.VideoCapture(0)
        self.vidcap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.vidcap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)

        # Query this to get latest image
        self.latest_image = None

        # Thread control
        self.kill_event = threading.Event()
        self.capture_thread = threading.Thread(target=self.capture_function)
        #self.enable_capture = True

    def start_capture(self):
        self.capture_thread.start()

    def stop_capture(self):
        self.kill_event.set()
        self.capture_thread.join(120)

    def get_latest_video_image(self):
        return self.latest_image

    def get_capture_image(self):
        return self.latest_image

    def capture_function(self):
        print("Starting: Image Capture Thread")
        count = 0
        while not self.kill_event.wait(0):
            #    print(str(count) + ": Capture")
            # count += 1
            ret, frame = self.vidcap.read()
            if ret:
                self.latest_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                print("Failed to read from camera")
            time.sleep(0.1)
