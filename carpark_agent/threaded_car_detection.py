import os
import cv2
import time
import glob
import threading
import skimage
import numpy as np
from car_detection.helpers import ParkedCarDetector
from .file_paths import FilePaths
from .gps import GPS

# If there is no maximum capacity stored we set it to this
default_max_cap = 8

class ThreadedCarDetection:
    def __init__(self, database, default_lat_lon, poll_seconds, max_file_count):
        # Configuration
        self.db = database
        self.default_lat_lon = default_lat_lon
        self.poll_seconds = poll_seconds
        self.max_file_count = max_file_count

        # Detection mask and temporary images
        self.process_image = None
        self.mask_image = None
        self.mask_ref_image = None

        # The detector
        self.detector = None
        self.prev_recent_filename = None
        self.gps = GPS()

        # Thread control
        self.kill_event = threading.Event()
        self.on_calc_finished = threading.Event()
        self.processing_thread = None

    def load_mask_image(self, image_shape):
        if os.path.isfile(FilePaths.mask_image_path):
            self.mask_image = skimage.io.imread(FilePaths.mask_image_path)
        else:
            self.mask_image = np.full(
                image_shape,
                (255, 255, 255),
                np.uint8)

        if os.path.isfile(FilePaths.mask_ref_image_path):
            self.mask_ref_image = skimage.io.imread(FilePaths.mask_ref_image_path)
        else:
            self.mask_ref_image = np.full(
                image_shape,
                (255, 255, 255),
                np.uint8)

    # Start up car detection (image processing) thread
    def start_processing(self):
        self.processing_thread = threading.Thread(target=self.processing_function)
        self.processing_thread.start()

    def stop_processing(self):
        self.kill_event.set()
        self.processing_thread.join(120)

    def get_new_image(self):
        search_text = FilePaths.raw_image_dir + "*" + FilePaths.image_file_ext
        files = glob.glob(search_text)
        files.sort(reverse=True)
        index = 0
        while True:
            if index >= len(files) or files[index] == self.prev_recent_filename:
                return None
            try:
                ret_image = skimage.io.imread(files[index])
                self.prev_recent_filename = files[index]
                return ret_image
            except Exception as e:
                # don't show this it looks alarming, but is qujite normal as image is probably halfway
                # through being written to
                # print("Failed to load raw image file: {} : {}".format(files[index], e.args))
                index += 1

    def prune_files_and_db(self):
        # prune the processed image files
        search_text = FilePaths.processed_image_dir + "*" + FilePaths.image_file_ext
        files = glob.glob(search_text)
        files.sort()
        num_files_to_remove = max(0, len(files) - self.max_file_count)
        for i in range(0, num_files_to_remove):
            os.remove(files[i])

        # prune the database
        self.db.prune_image_table(self.max_file_count)


    def processing_function(self):
        print("Starting: Car detection thread")
        max_cap = self.db.get_max_capacity()
        if max_cap is None:
            self.db.save_max_capacity(default_max_cap)

        self.detector = ParkedCarDetector()
        self.detector.enable_flicker_removal = False

        image_count = 0
        time.sleep(2)
        last_time = time.time()
        while not self.kill_event.wait(0):
            # get GPS data if we have it
            lat, lon = self.gps.GetValues()
            if lat is not None and lon is not None:
                self.db.save_lat_lon(lat, lon)
                self.db.set_system_status("gps_source", "GPS Unit")

            # Retrieve latest value fom database
            lat, lon = self.db.get_lat_lon()
            if lat is None and lon is None:
                lat, lon = self.default_lat_lon
                self.db.save_lat_lon(lat, lon)
                self.db.set_system_status("gps_source", "Command line")

            this_time = time.time()
            print("waiting for new image to be available: " + time.strftime('%Mm %Ss', time.gmtime(this_time- last_time)))
            image = self.get_new_image()

            # save this one out immediately in case it causes a cash we will have a record of it
            if image is not None:
                print("New image available - detecting vehicles...")

                # Find contours ni the mask image so we can just focus in on that area
                self.load_mask_image(image.shape)
                greyscale_mask = cv2.cvtColor(self.mask_image, cv2.COLOR_RGB2GRAY)

                image_right = greyscale_mask.shape[1] - 1
                image_top = greyscale_mask.shape[0] -1

                cv2.line(greyscale_mask, (0, 0), (0, image_top), (0, 0, 0), 1)
                cv2.line(greyscale_mask, (0, image_top), (image_right, image_top), (0, 0, 0), 1)
                cv2.line(greyscale_mask, (image_right, image_top), (image_right, 0), (0, 0, 0), 1)
                cv2.line(greyscale_mask, (image_right, 0), (0, 0), (0, 0, 0), 1)


                result = cv2.findContours(greyscale_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                contours, hierarchy = result if len(result) == 2 else result[1:3]


                left = greyscale_mask.shape[1]
                bottom = greyscale_mask.shape[0]
                right = 0
                top = 0
                for cnt in contours:
                    x, y, w, h = cv2.boundingRect(cnt)
                    left = min(left, x)
                    right = max(right, x + w)
                    bottom = min(bottom, y)
                    top = max(top, y + h)

                # If we don't have a masked area at all or it is too small, then just process the whole image
                if right < left or top < bottom:
                    left = 0
                    bottom = 0
                    right = greyscale_mask.shape[1]
                    top = greyscale_mask.shape[0]

                self.process_image = np.zeros((top-bottom, right-left, 3), np.uint8)
                zoom_image = image[bottom:top, left:right]
                zoom_image_mask = self.mask_image[bottom:top, left:right]
                cv2.multiply(zoom_image, zoom_image_mask, self.process_image, 1 / 255.0)

                # Do detections and visualise
                start_detect_time = time.time()
                results = self.detector.detect_cars(self.process_image)
                end_detect_time = time.time()
                print("Detection complete. Computation duration: " + format(time.strftime('%Mm %Ss', time.gmtime(end_detect_time - start_detect_time))))
                bwImage = cv2.cvtColor(self.process_image, cv2.COLOR_RGB2GRAY)
                bwImage = cv2.cvtColor(bwImage, cv2.COLOR_GRAY2RGB)
                out_image = self.detector.image_visualise(bwImage, results)

                print("Visualisation complete")
                processed_filename = FilePaths.generate_processed_from_raw_path(self.prev_recent_filename)
                skimage.io.imsave(processed_filename, out_image)

                # Add images and data to database
                total_count = len(results['class_ids'])
                moving_count = sum(self.detector.moving) if self.detector.enable_flicker_removal else 0
                free_spaces = self.db.get_max_capacity() - total_count
                self.db.add_entry_no_save(
                    self.prev_recent_filename,
                    processed_filename,
                    total_count,
                    moving_count,
                    free_spaces,
                    lat,
                    lon)
                self.prune_files_and_db()

                image_count += 1
                self.on_calc_finished.set()
                last_time = time.time()

            time.sleep(self.poll_seconds)




