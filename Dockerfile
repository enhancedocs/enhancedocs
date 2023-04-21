FROM python:3.11.3

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app

RUN pip3 install -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
