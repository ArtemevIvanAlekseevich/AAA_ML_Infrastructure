# Homework backend

### app

Для начала реализовал метод ```get_image_from_id```, который достает по id изображение, если оно есть, иначе возвращает ```"This image does not exist"```:

```python
import requests

def get_image_from_id(image_id):
    link = f'http://51.250.83.169:7878/images/{image_id}'
    responce = requests.get(link)
    if responce.status_code == 200:
        im = responce.content
        im = io.BytesIO(im)
        return im
    else:
        return 'This image does not exist'
```

Затем добавил 2 метода ```read_plate_number_from_id``` и ```read_plate_numbers_from_id_list```.
Первый используется если надо прочитать только 1 номер. В json запроса должно быть поле ```image_id``` иначе вернется статус код 400 с сообщением ```'field "image_id" not found'```. Если функция ```get_image_from_id``` вернет ```'This image does not exist'```, то ```read_plate_number_from_id``` тоже вернется статус код 400 с сообщением ```'This image does not exist'```. Если id не int также вернётся ошибка 400 с сообщением ```'Image_id should be int'```.

Возвращает json-ы видов: ```{'plate_number': 'о101но750'}```,  ```{'error': 'This image does not exist'}```, ```{'error': 'Image_id should be int'}```

```python
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
```

```read_plate_numbers_from_id_list``` используется если надо прочитать несколько номеров. В json запроса должно быть поле ```id_list``` иначе вернется статус код 400 с сообщением ```'field "id_list" not found'```. Все ошибки при обработке ```id``` аналогичны методу ```read_plate_number_from_id```, но если ошибка возникает для какого ```id```, то метод продолжит выполнение для других ```id``` а для этого в поле ответа запишет соответствующую ошибку. 
Возвращает json вида:
```python
{'plate_numbers': 
    {
        '111': {'error': 'This image does not exist', 'status_code': 400}, 
        '9965': {'number': 'о101но750', 'status_code': 200}, 
        '10022': {'number': 'с181мв190', 'status_code': 200}
    }
}
```

### plate_reader_client

Добавил 2 метода к классу ```PlateReaderClient```. Оба пытаются привести данные к требуемым типам для сервиса и отправляют запросы на соответствующие url.
Метод для одного id:

```python
def image_id2number(self, image_id: int):
    image_id = int(image_id)
    res = requests.post(
        f'{self.host}/image_id2Number',
        json={
            'image_id': image_id,
        },
    )
    return res.json()
```
Метод для списка id:
```python
def id_list2numbers(self, id_list: List[int]):

    id_list = list(map(int, id_list))

    res = requests.post(
        f'{self.host}/id_list2numbers',
        json={
            'id_list': id_list,
        },
    )
    return res.json()
```
Примеры работы клиента:
- корректный id:
```python
    res = client.image_id2number(9965)
    pprint(res)
    # Вывод
    {'plate_number': 'о101но750'}
```

- несуществующий id:
```python
    res = client.image_id2number(1111)
    pprint(res)
    # Вывод
    {'error': 'This image does not exist'}
```

- корректный id, но в виде строки:
```python
    res = client.image_id2number('10022')
    pprint(res)
    # Вывод
    {'plate_number': 'с181мв190'}
```

- 2 id корректны, последний нет:
```python
    res = client.id_list2numbers([10022, 9965, 111])
    pprint(res)
    # Вывод
    {'plate_numbers': {'10022': {'number': 'с181мв190', 'status_code': 200},
                    '111': {'error': 'This image does not exist',
                            'status_code': 400},
                    '9965': {'number': 'о101но750', 'status_code': 200}}}
```

- предыдущий запрос, но часть в виде строки:
```python
    res = client.id_list2numbers(['10022', 9965, '111'])
    pprint(res)
    # Вывод
    {'plate_numbers': {'10022': {'number': 'с181мв190', 'status_code': 200},
                    '111': {'error': 'This image does not exist',
                            'status_code': 400},
                    '9965': {'number': 'о101но750', 'status_code': 200}}}
```
- невозможно преобразовать 'aaaa' к int:
```python
    res = client.id_list2numbers(['10022', '9965', 'aaaa'])
    # Вывод
    ValueError: invalid literal for int() with base 10: 'aaaa'
```


