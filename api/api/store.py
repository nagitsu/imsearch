from luminoth.tools.checkpoint import get_checkpoint_config
from luminoth.utils.predicting import PredictorNetwork

from . import settings


CACHED_DETECTOR = None


def load_detector():
    config = get_checkpoint_config(settings.LUMI_CHECKPOINT)
    detector = PredictorNetwork(config)
    return detector


def detect_objects(image):
    # To avoid loading the model every time.
    global CACHED_DETECTOR
    if CACHED_DETECTOR is None:
        CACHED_DETECTOR = load_detector()
    detector = CACHED_DETECTOR

    detections = detector.predict_image(image)

    # Transform into the format expected by the ES mapping. Change bounding box
    # format from two extremes to top-left corner plus dimensions, so it's more
    # natural to search in.
    objects = [
        {
            'label': det['label'],
            'x': det['bbox'][0],
            'y': det['bbox'][1],
            'width': det['bbox'][2] - det['bbox'][0],
            'height': det['bbox'][3] - det['bbox'][1],
        } for det in detections
    ]

    return objects
