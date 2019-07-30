import time
import threading
import skimage
import glob
import os

from .file_paths import FilePaths

class ThreadedImageRecorder:
    def __init__(self, image_source, poll_seconds, max_file_count):
        # Configuration
        self.image_source = image_source
        self.poll_seconds = poll_seconds
        self.loop_count = 0
        self.max_file_count = max_file_count

        # Thread control
        self.kill_event = threading.Event()
        self.on_calc_finished = threading.Event()
        self.processing_thread = None


    # Start up car detection (image processing) thread
    def start_processing(self):
        self.processing_thread = threading.Thread(target=self.processing_function)
        self.processing_thread.start()

    def stop_processing(self):
        self.kill_event.set()
        self.processing_thread.join(120)

    def prune_image_files(self):
        search_text = FilePaths.raw_image_dir + "*" + FilePaths.image_file_ext
        files = glob.glob(search_text)
        files.sort()
        num_files_to_remove = max(0, len(files) - self.max_file_count)
        for i in range(0, num_files_to_remove):
            os.remove(files[i])


    def processing_function(self):

        print("Starting: Image recorder thread")
        self.image_source.get_capture_image()
        time.sleep(20)
        while not self.kill_event.wait(0):
            src_image = self.image_source.get_capture_image()
            image = self.image_source.get_capture_image().copy() if src_image is not None else None

            if image is not None:
                t = int(time.time())
                skimage.io.imsave(FilePaths.generate_raw_image_path(t), image)
                print("Saving image: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time()))))
                self.prune_image_files()

            # never sleep for longer than a second otherwise it can take ages to shut down
            if self.poll_seconds > 1:
                t = time.time()
                while time.time() - t < self.poll_seconds and not self.kill_event.wait(0):
                    time.sleep(1)
            else:
                time.sleep(self.poll_seconds)




