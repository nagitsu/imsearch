import os
import uuid

from elasticsearch_dsl import Q
from flask import Flask, abort, jsonify, request, send_from_directory
from flask_cors import CORS
from PIL import Image

from . import settings
from .index import search, store_doc
from .store import detect_objects


ALLOWED_EXTENSIONS = ['jpeg', 'jpg', 'png', 'gif']


app = Flask(__name__)
CORS(app)


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'bad_request',
        'message': error.description,
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'not_found',
        'message': error.description,
    }), 404


@app.route('/store/', methods=['POST'])
def store_image():
    # Validate the input.
    if 'image' not in request.files:
        abort(400, '`image` is required.')

    file = request.files['image']

    if file.filename == '':
        abort(400, '`image` is required.')

    invalid_extension = (
        '.' not in file.filename or
        file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS
    )
    if invalid_extension:
        abort(400, 'Invalid extension. Allowed: {}'.format(ALLOWED_EXTENSIONS))

    try:
        image = Image.open(file).convert('RGB')
    except Exception:
        # TODO: What exception?
        abort(400, 'Invalid image.')

    # Perform the object detection (using Luminoth).
    objects = detect_objects(image)

    # Generate a unique ID and store in the filesystem using it as name.
    image_id = str(uuid.uuid4())

    # Image already read by Pillow, go back and store.
    file.seek(0)
    file.save(os.path.join(settings.UPLOAD_FOLDER, image_id))

    # Prepare the document and index to Elasticsearch.
    doc = {
        'image_name': file.filename,
        'image_id': image_id,
        'objects': objects,
    }
    store_doc(doc)

    # Return the detected objects.
    # TODO: Don't leak `image_id`.
    return jsonify(doc)


@app.route('/search/', methods=['POST'])
def search_images():
    # TODO: Validate input.
    query = request.get_json(force=True)

    offset = query.get('offset', 0)
    limit = query.get('limit', 50)

    s = search()

    qs = []
    if 'term' in query:
        qs.append(Q('match', objects__label=query['term']))
    if 'min_width' in query:
        qs.append(Q('range', objects__width={'gte': query['min_width']}))
    if 'min_height' in query:
        qs.append(Q('range', objects__height={'gte': query['min_height']}))

    if qs:
        s = s.filter(
            'nested', path='objects',
            query=Q('bool', must=qs)
        )

    s = s[offset:offset + limit]

    raw_hits = s.execute()
    hits = [hit.to_dict() for hit in raw_hits]

    return jsonify(result=hits, count=raw_hits.hits.total)


@app.route('/image/<image_id>/', methods=['GET'])
def get_image(image_id):
    """Returns image `image_id`.

    In a real-world scenario, this wouldn't be served through an application
    server but through something like nginx.
    """
    return send_from_directory(settings.UPLOAD_FOLDER, image_id)
