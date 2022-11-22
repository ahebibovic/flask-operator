FROM python:3-alpine

WORKDIR /app

RUN pip install kopf kubernetes

COPY . .

CMD ["kopf", "run","handlers.py","--verbose"]