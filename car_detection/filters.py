"""Filters for frame process."""
import car_detection.mrcnn.utils
import numpy as np


def filter_vehicles(detected_objects):
    """Skip boxes that do not indicate cars, buses or trucks.

    Cuco models ids are:
     - 2 bicycle,
     - 3 car,
     - 4 motorcycle,
     - 6 bus,
     - 7 train,
     - 8 truck,
     - 9 boat.
    """
    mask = np.array(
        #[i in (2, 3, 4, 6, 8) for i in detected_objects['class_ids']],
        [i in (3, 8) for i in detected_objects['class_ids']],
        dtype=bool)

    vehicles = {
        'rois': detected_objects['rois'][mask],
        'class_ids': detected_objects['class_ids'][mask],
        'scores': detected_objects['scores'][mask],
        'masks': detected_objects['masks'][:,:,mask]
    }

    return vehicles

def filter_large_unconfident_objects(detected_objects, size_threshold=400,confidence_threshold=0.9):
    """Skip boxes that are large and unconfident."""
    max_size = lambda x: max((x[2]-x[0]),(x[3]-x[1]))
   
    sizeMask = np.array(
        [max_size(i) < size_threshold for i in detected_objects['rois']], dtype=bool)
        
    confidenceMask = np.array(
        [i > confidence_threshold for i in detected_objects['scores']], dtype=bool)

    mask = sizeMask | confidenceMask
    
    vehicles = {
        'rois': detected_objects['rois'][mask],
        'class_ids': detected_objects['class_ids'][mask],
        'scores': detected_objects['scores'][mask],
        'masks': detected_objects['masks'][:,:,mask]
    }

    return vehicles

def filter_small_objects(detected_objects, treshold=0.001):
    """Skip boxes that are small."""
    size = lambda x: (x[2]-x[0])*(x[3]-x[1])
    size_x, size_y, _ = detected_objects['masks'].shape
    min_size = size_x*size_y*treshold

    mask = np.array(
        [size(i) > min_size for i in detected_objects['rois']], dtype=bool)

    vehicles = {
        'rois': detected_objects['rois'][mask],
        'class_ids': detected_objects['class_ids'][mask],
        'scores': detected_objects['scores'][mask],
        'masks': detected_objects['masks'][:,:,mask]
    }

    return vehicles


def filter_duplicated_objects(detected_objects, treshold=0.8):
    """Keep one box out of many that cover the same region."""
    r = detected_objects['rois']
    overlaps = car_detection.mrcnn.utils.compute_overlaps(r, r)

    mask = [True]*len(r)
    for i, v in enumerate(overlaps):
        v = v.copy()
        np.put(v, i, 0)
        if v.max() < treshold:
            continue
        j = np.argmax(v)
        score_i = detected_objects['scores'][i]
        score_j = detected_objects['scores'][j]
        mask[j if score_i > score_j else i] = False

    mask = np.array(mask, dtype=bool)
    results = {
        'rois': detected_objects['rois'][mask],
        'class_ids': detected_objects['class_ids'][mask],
        'scores': detected_objects['scores'][mask],
        'masks': detected_objects['masks'][:,:,mask]
    }

    return results


def filter_flickers(past, current, treshold=0.6):
    """Keep only objects that occure in both frames."""
    overlaps = car_detection.mrcnn.utils.compute_overlaps(current['rois'], past['rois'])

    mask = [True]*len(current['rois'])
    for i, row in enumerate(overlaps):
        if row.size == 0:
            mask[i] = False
            continue
        
        max_index = row.argmax(axis=0)
        if row[max_index] < treshold:
            mask[i] = False

    mask = np.array(mask, dtype=bool)
    results = {
        'rois': current['rois'][mask],
        'class_ids': current['class_ids'][mask],
        'scores': current['scores'][mask],
        'masks': current['masks'][:,:,mask]
    }

    return results
