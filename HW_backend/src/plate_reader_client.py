import requests
from typing import List
from pprint import pprint


class PlateReaderClient:
    def __init__(self, host: str):
        self.host = host

    def read_plate_number(self, im):
        res = requests.post(
            f'{self.host}/readPlateNumber',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=im,
        )

        return res.json()

    def greeting(self, user: str):
        res = requests.post(
            f'{self.host}/greeting',
            json={
                'user': user,
            },
        )

        return res.json()

    def image_id2number(self, image_id: int):
        image_id = int(image_id)
        res = requests.post(
            f'{self.host}/image_id2Number',
            json={
                'image_id': image_id,
            },
        )
        return res.json()

    def id_list2numbers(self, id_list: List[int]):

        id_list = list(map(int, id_list))

        res = requests.post(
            f'{self.host}/id_list2numbers',
            json={
                'id_list': id_list,
            },
        )
        return res.json()


if __name__ == '__main__':
    client = PlateReaderClient(host='http://158.160.53.219:8080')

    with open('./HW_backend/images/9965.jpg', 'rb') as im:
        res = client.read_plate_number(im)
        pprint(res)

    res = client.image_id2number(9965)
    pprint(res)

    res = client.image_id2number(1111)
    pprint(res)

    res = client.image_id2number('10022')
    pprint(res)

    res = client.id_list2numbers([10022, 9965, 111])
    pprint(res)

    res = client.id_list2numbers(['10022', 9965, '111'])
    pprint(res)

    # res = client.id_list2numbers(['10022', '9965', 'aaaa'])
    # pprint(res)
