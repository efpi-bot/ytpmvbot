FROM python:3.9.6-slim-buster

COPY / /opt/ytpmvbot/

RUN apt-get update && apt-get install ffmpeg -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ytpmvbot

RUN pip install --no-cache-dir -r requirements.txt && \
    echo "${TOKEN}" > key

ENTRYPOINT [ "python", "ytpmv.py" ]