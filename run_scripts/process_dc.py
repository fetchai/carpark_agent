"""Process frames. Detect cars. Save frames with colorful boxes."""
import datetime
import skimage.io
from car_detection.helpers import ParkedCarDetector

input_path = "/tmp/video-frames"
output_path = "/tmp/boxed-frames"


# Create the car detector
detector = ParkedCarDetector()

# Get images and Loop through them
images = skimage.io.imread_collection(input_path + "/*.png")
checkpoint = datetime.datetime.now()
for i, image in enumerate(images):
    result = detector.detect_cars(image)

    # check time
    now = datetime.datetime.now()
    print('\nStep: {} - Time: {}'.format(i, now - checkpoint))
    checkpoint = now

    # Get ready to visualize
    out_filename = output_path+ '/frame_{:05d}.png'.format(i)


    # visualization
    detector.save_visualise(image, result, out_filename)

    if (detector.moving is not None):
        print('   Detected cars: {}'.format(len(result['class_ids'])))
        print('   Moving: {}'.format(sum(detector.moving)))
        print('   Standing or parked: {}'.format(len(detector.moving) - sum(detector.moving)))




