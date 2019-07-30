import os

ROOT_DIR = os.path.abspath("../src/Mask_RCNN/")
MODEL_DIR = os.path.abspath("../src/coco/")
COCO_MODEL_PATH = os.path.join(MODEL_DIR, "mask_rcnn_coco.h5")

import sys
import random
import math

import numpy as np
import skimage.io
import matplotlib
matplotlib.use('PS')
import matplotlib.pyplot as plt
sys.path.append(ROOT_DIR)
import mrcnn.utils
import mrcnn.model
import mrcnn.visualize
import time

"""Load the configuration file for the MS-COCO model. """
sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))
import coco


class InferenceConfig(coco.CocoConfig):
    """Overwrite the batch size.

    Batch size = GPU_COUNT * IMAGES_PER_GPU
    For our needs, we need batch size = 1
    """
    
    GPU_COUNT = 1
    IMAGES_PER_GPU =1
    DETECTION_MIN_CONFIDENCE = 0.2
    
class Detect(object):
    def __init__(self, name):
        self.dir = name
        self.config = InferenceConfig()
        
    def filter_vehicles(self, detect_objects):
        """Skip boxes that do not indicate carsm busses or trucks.
        
        Coco model, IDs are:
             - 3 car,
             - 4 motorbike
             - 6 bus
             - 7 train
             - 8 truck
             - 9 boat
             """
        mask = np.array([i in (3, 8, 6) for i in detect_objects['class_ids']], dtype=bool)
        vehicles = {
            'rois': detect_objects['rois'][mask],
            'class_ids': detect_objects['class_ids'][mask],
            'scores': detect_objects['scores'][mask],
            'masks': detect_objects['masks'][:,:,mask]
            }
            
        return vehicles
        
        
    def main(self):
        print("detecting cars...")
        
        """Create a model object and load the weights."""
        model =mrcnn.model.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=self.config)
        
        model.load_weights(COCO_MODEL_PATH, by_name=True)
        
        """Check class numbers"""
        dataset = coco.CocoDataset()
        dataset.load_coco(MODEL_DIR, "train")
        dataset.prepare()
        
        """Load an image"""
        IMAGE = self.dir #os.path.abspath("../../resources/images/stjohns.jpg")
        image = skimage.io.imread(IMAGE)
        results = model.detect([image], verbose=1)
        
        
        """Visualize results"""
        r = results[0]
        r = self.filter_vehicles(r)
        
        """Save image"""
        t = int(time.time())
        name = str(t) + ".png"
        path = os.path.abspath("../output")
        
        mrcnn.visualize.display_instances(
            path,
            name,
            image,
            r['rois'],
            r['masks'],
            r['class_ids'],
            dataset.class_names,
            r['scores'],
            title='# os detect cars: {}'.format(len(r['class_ids'])))
        
        return len(r['class_ids'])
        
        


