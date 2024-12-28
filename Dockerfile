FROM python:3.10-slim

WORKDIR /app
COPY . /app
COPY firebase-key.json /firebase-key.json

RUN pip install --no-cache-dir -r requirements.txt
CMD ["flask", "run", "--host=0.0.0.0"]
