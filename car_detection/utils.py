'''Common utility functions and classes.'''
import numpy
import car_detection.mrcnn.utils


          
def translations(past, current, treshold=0.6):
    """Calculating vectors of translations."""
    def center(x):
        """Calculate center of the box."""
        return (x[2] + x[0])/2, (x[3] + x[1])/2

    overlaps = car_detection.mrcnn.utils.compute_overlaps(current['rois'], past['rois'])

    result = []
    for i, row in enumerate(overlaps):
        if len(row) == 0:
            continue
        
        max_index = row.argmax(axis=0)
        if row[max_index] < treshold:
            continue

        past_box = past['rois'][max_index]
        current_box = current['rois'][i]
        vector = numpy.array([center(past_box), center(current_box)])

        result.append(
            {
                'past_box': past_box,
                'current_box': current_box,
                'vector': vector
            })

    return result


def moving_vehicles(trans, treshold=5):
    """Count number of moving vehicles."""
    results = []
    for tr in trans:
        v = tr['vector']
        move_y = v[0][0] - v[1][0]
        move_x = v[0][1] - v[1][1]

        moving = False
        if abs(move_y) > treshold or abs(move_x) > treshold:
            moving = True
        results.append(moving)

    return results
