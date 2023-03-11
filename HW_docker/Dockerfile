FROM python:3.8

ENV FLASK_APP=server

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY ./server.py /code/server.py

EXPOSE 8080

CMD flask run -h 0.0.0.0 -p 8080
