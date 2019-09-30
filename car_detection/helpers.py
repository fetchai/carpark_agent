'''Common utility functions and classes.'''
import numpy
import car_detection.mrcnn.utils


'''imports needed for diarmid's new classes'''

import os

''' Required otherwise convert to string doesn't work on the canvas - need to have Tk installed - could cause problems on RPi'''
import matplotlib
matplotlib.use("Agg")


import matplotlib.pyplot as plt
import skimage.io

import car_detection.config
import car_detection.filters
import car_detection.names
import car_detection.utils


import car_detection.mrcnn.model
import car_detection.mrcnn.visualize

from .circular_list import CircularList


class ParkedCarDetector:
        
    def __init__(self):

        """Main."""
        conf = car_detection.config.InferenceConfig()

        # Create a model object and load the weights.
        self.model = car_detection.mrcnn.model.MaskRCNN(
            mode="inference", model_dir=car_detection.config.MODEL_PATH, config=conf)
        weights_path = os.path.join(
            car_detection.config.MODEL_PATH, car_detection.config.WEIGHTS_FILE)
        self.model.load_weights(weights_path, by_name=True)
        
        # Keep track of this image and the prevous one to do between-frame flicker removal
        self.raw_history = CircularList(2)
        self.no_flicker_history = CircularList(2)
        self.enable_flicker_removal = True
        self.enable_remove_large_unconfident = False
        self.moving = None
        

    def reset_history(self):
        self.raw_history = CircularList(2)
        self.no_flicker_history = CircularList(2)
    

    def create_max_rois(self, result):
        max_size = lambda x: max((x[2]-x[0]),(x[3]-x[1]))
        result['max_rois'] = []
        for j in result['rois']:
            result['max_rois'].append(max_size(j))

            
    def detect_cars(self, image):
        height, width, channels = image.shape
        maxDim = max(width, height)

        results = self.model.detect([image], verbose=False)
        raw_result = results[0]
        raw_result = car_detection.filters.filter_vehicles(raw_result)
        #raw_result = car_detection.filters.filter_small_objects(raw_result, treshold=0.002)
        #raw_result = car_detection.filters.filter_duplicated_objects(raw_result, treshold=0.8)
        
        if (self.enable_remove_large_unconfident):
            raw_result = car_detection.filters.filter_large_unconfident_objects(
                raw_result,
                size_threshold=0.4 * maxDim,
                confidence_threshold=0.92)
            
        self.moving = None
        self.create_max_rois(raw_result)
        
        if (not self.enable_flicker_removal):
            return raw_result;
        
        self.raw_history.append(raw_result)
    
        # Do we have a previous frame?
        if not self.raw_history.has_past_item(1):
            return None
        
        # Remove flickering detections
        no_flicker_result = car_detection.filters.filter_flickers(
            self.raw_history.get_past_item(1),
            self.raw_history.get_past_item(0))
        
        self.create_max_rois(no_flicker_result)
        
        # Keep track of the results after flicker filtering
        self.no_flicker_history.append(no_flicker_result)
        
                
        # If we don't have two such sets of results, then can't get velocity info
        if self.no_flicker_history.has_past_item(1):
        
            # Counting moving vehicles
            vec = car_detection.utils.translations(
                self.no_flicker_history.get_past_item(1),
                self.no_flicker_history.get_past_item(0),
                treshold=0.3)
            self.moving = car_detection.utils.moving_vehicles(vec, treshold=2)
            
            
            
        return no_flicker_result
 

    # returns a skimage of the results
    def image_visualise(self, image, results):
        height, width, channels = image.shape

        fig, ax = plt.subplots(figsize=(width * 0.01, height * 0.01), dpi=100)

        if (results is None):
            return image

        col = car_detection.config.color_range
        colors = numpy.array(
            [col[int(200 * (s - 0.5)) if s > 0.5 else 0].rgb for s in results['scores']])

        car_detection.mrcnn.visualize.display_instances(
            image,
            results['rois'],
            results['masks'],
            results['class_ids'],
            car_detection.names.coco_class_names,
            results['scores'],
            #results['max_rois'],
            ax=ax,
            colors=colors)

        fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        plt.autoscale(tight=True)
        fig.canvas.draw()
        buf = numpy.fromstring(fig.canvas.tostring_rgb(), dtype='uint8')
        if buf.size != height * width * 3:
            print("Warning: Visualisation buffer is not same size as input image - attempting to adjust")
            width = round(buf.size / (3 * height))
            if buf.size != height * width * 3:
                print("Failed to resize visualisation")
                return None
        buf.shape = (height, width, 3)
        plt.close(fig)

        return buf

    # saves the resulting image to a file
    def save_visualise(self, image, results, filename):
        height, width, channels = image.shape
        
        fig, ax = plt.subplots(figsize=(width * 0.01, height * 0.01), dpi=100)
        
        if (results is None):
            skimage.io.imsave(filename, image)
            print("Save original image")
            return
            
        
        col = car_detection.config.color_range
        colors = numpy.array(
            [col[int(200*(s-0.5)) if s > 0.5 else 0].rgb for s in results['scores']])
        
        mrcnn.visualize.display_instances(
            image,
            results['rois'],
            results['masks'],
            results['class_ids'],
            car_detection.names.coco_class_names,
            results['scores'],
#            results['max_rois'],
            ax=ax,
            colors=colors)

        fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        plt.autoscale(tight=True)
        with open(filename, 'bw') as file:
            fig.canvas.print_png(file)

        plt.close(fig)
          
