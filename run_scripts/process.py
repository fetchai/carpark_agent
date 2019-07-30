"""Process frames. Detect cars. Save frames with colorful boxes."""
import os
import datetime

import numpy as np
import skimage.io
import matplotlib.pyplot as plt

import mrcnn.model
import mrcnn.visualize
import car_detection.config
import car_detection.filters
import car_detection.utils
import car_detection.names


"""Main."""
config = car_detection.config.InferenceConfig()

# Create a model object and load the weights.
model = mrcnn.model.MaskRCNN(
    mode="inference", model_dir=car_detection.config.MODEL_PATH, config=config)
weights_path = os.path.join(
    car_detection.config.MODEL_PATH, car_detection.config.WEIGHTS_FILE)
model.load_weights(weights_path, by_name=True)


images = skimage.io.imread_collection("/tmp/video-frames/*.png")
past_r = None
checkpoint = datetime.datetime.now()
for i, image in enumerate(images):
    try:
        results = model.detect([image], verbose=False)
        r0 = results[0]
        r0 = car_detection.filters.filter_vehicles(r0)
        r0 = car_detection.filters.filter_small_objects(r0, treshold=0.002)
        r0 = car_detection.filters.filter_duplicated_objects(r0, treshold=0.8)

        # check time
        now = datetime.datetime.now()
        print('Step: {} - Time: {}'.format(i, now - checkpoint))
        checkpoint = now

        if past_r is None:
            past_r = r0, r0
            continue

        r = car_detection.filters.filter_flickers(past_r[0], r0)

        # visualization
        fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=100)
        col = car_detection.config.color_range
        colors = np.array(
            [col[int(200*(s-0.5)) if s > 0.5 else 0].rgb for s in r['scores']])
        mrcnn.visualize.display_instances(
            image, r['rois'], r['masks'], r['class_ids'],
            car_detection.names.coco_class_names, r['scores'],
            ax=ax, colors=colors)

        fig.subplots_adjust(
            left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        with open('/tmp/boxed-frames/frame_{:05d}.png'.format(i), 'bw') as file:
            fig.canvas.print_png(file)

        plt.close()

        # Counting moving vehicles
        vec = car_detection.utils.translations(past_r[1], r, treshold=0.3)
        moving = car_detection.utils.moving_vehicles(vec, treshold=2)
        print('   Detected cars: {}'.format(len(r['class_ids'])))
        print('   Moving: {}'.format(sum(moving)))
        print('   Standing or parked: {}'.format(len(moving) - sum(moving)))

        past_r = r0, r
    except Exception as err:
        print('------ PROBLEM ------')
        print('------ with {} ------'.format(i))
        print(err)
        continue
