"""Model configuration."""
import os
import car_detection.coco.coco
from colour import Color


MODEL_PATH = temp_dir = str(os.path.join(os.path.dirname(__file__), "weights"))
WEIGHTS_FILE = "mask_rcnn_coco.h5"

high = Color("blue")
low = Color("red")
color_range = list(low.range_to(high, 101))


class InferenceConfig(car_detection.coco.coco.CocoConfig):
    """Configure the MS-COCO model.

    Owerwrite the batch size.python3
    Batch size = GPU_COUNT * IMAGES_PER_GPU
    For our needs, we need batch size = 1
    """
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    DETECTION_MIN_CONFIDENCE = 0.6
    #DETECTION_NMS_THRESHOLD = 0.4
    #IMAGE_MAX_DIM = 320
    IMAGE_MAX_DIM = 960
    #IMAGE_MAX_DIM = 1920
