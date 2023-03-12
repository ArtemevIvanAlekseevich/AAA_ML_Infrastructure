import requests
import logging
from flask import Flask, request
from models.plate_reader import PlateReader, InvalidImage
import io


app = Flask(__name__)
plate_reader = PlateReader.load_from_file(
    './model_weights/plate_reader_model.pth')


def get_image_from_id(image_id):
    link = f'http://51.250.83.169:7878/images/{image_id}'
    responce = requests.get(link)
    if responce.status_code == 200:
        im = responce.content
        im = io.BytesIO(im)
        return im
    else:
        return 'This image does not exist'


@app.route('/')
def hello():
    user = request.args['user']
    return f'<h1 style="color:red;"><center>Hello {user}!</center></h1>'


# <url>:8080/greeting?user=me
# <url>:8080 : body: {"user": "me"}
# -> {"result": "Hello me"}
@app.route('/greeting', methods=['POST'])
def greeting():
    # return request.json
    if 'user' not in request.json:
        return {'error': 'field "user" not found'}, 400

    user = request.json['user']
    return {
        'result': f'Hello {user}',
    }


# <url>:8080/readPlateNumber : body <image bytes>
# -> {"plate_number": "c180mv ..."}
@app.route('/readPlateNumber', methods=['POST'])
def read_plate_number():
    im = request.get_data()
    im = io.BytesIO(im)

    try:
        res = plate_reader.read_text(im)
    except InvalidImage:
        logging.error('invalid image')
        return {'error': 'invalid image'}, 400

    return {
        'plate_number': res,
    }


# <url>:8080/id2Number?id=123321
# <url>:8080/readPlateNumber : body: {"id": 123321}
# -> {"plate_number": "c180mv ..."}
@app.route('/image_id2Number', methods=['POST'])
def read_plate_number_from_id():

    if 'image_id' not in request.json:
        return {'error': 'field "image_id" not found'}, 400

    image_id = request.json['image_id']

    if not isinstance(image_id, int):
        return {'error': 'Image_id should be int'}, 400

    im = get_image_from_id(image_id)

    if im == 'This image does not exist':
        return {'error': im}, 400

    try:
        res = plate_reader.read_text(im)
    except InvalidImage:
        logging.error('invalid image')
        return {'error': 'invalid image'}, 400

    return {
        'plate_number': res,
    }


# <url>:8080/id2Number?id=123321&id=456654
# <url>:8080/readPlateNumber : body: {"id": [123321, 456654]}
# -> {"plate_numbers": {123321: "c180mv ...", 456654: "c180mv ..."}}
@app.route('/id_list2numbers', methods=['POST'])
def read_plate_numbers_from_id_list():

    if 'id_list' not in request.json:
        return {'error': 'field "id_list" not found'}, 400

    response = dict()
    id_list = request.json['id_list']

    if not isinstance(id_list, list):
        return {'error': 'id_list should be list'}, 400

    for image_id in id_list:

        if not isinstance(image_id, int):
            response[image_id] = {'error': 'image_id should be int',
                                  'status_code': 400}
            continue

        im = get_image_from_id(image_id)

        if im == 'This image does not exist':
            response[image_id] = {'error': im, 'status_code': 400}
            continue

        try:
            res = plate_reader.read_text(im)
            response[image_id] = {'number': res, 'status_code': 200}

        except InvalidImage:
            logging.error('invalid image')
            response[image_id] = {'error': 'invalid image', 'status_code': 400}

    return {
        'plate_numbers': response,
    }


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=8080, debug=True)
