FROM python:alpine

COPY / /opt/ytpmvbot/
WORKDIR /opt/ytpmvbot

RUN apk update && apk add g++ ffmpeg

RUN pip install -r requirements.txt

ENV PATH=/root/.local/bin:$PATH

HEALTHCHECK --interval=2m --timeout=1s \
    CMD [ "/opt/ytpmvbot/healthcheck.sh" ]

ENTRYPOINT [ "/opt/ytpmvbot/docker-entrypoint.sh" ]
CMD [ "python", "ytpmv.py", "||", "echo 'Bot exited with error'" ]