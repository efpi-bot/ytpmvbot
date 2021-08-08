FROM python:3.9.6-slim-buster

ENV TOKEN=

RUN mkdir /opt/ytpmvbot && \
    apt-get update && apt-get install ffmpeg -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

COPY / /opt/ytpmvbot

WORKDIR /opt/ytpmvbot

RUN pip install --no-cache-dir -r requirements.txt && \
    echo "${TOKEN}" > key

ENTRYPOINT [ "python", "ytpmv.py" ]