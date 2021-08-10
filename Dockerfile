FROM cobaltdocker/eht16-python3:buster-slim AS build

COPY / /opt/ytpmvbot/
WORKDIR /opt/ytpmvbot

# install lsb_release to prevent pip from erroring
RUN apt-get update && apt-get install lsb-release -y --no-install-recommends && \
    \
    rm -rf /var/lib/apt/lists/* && \
    pip install --user --no-cache-dir -r requirements.txt && \
    chmod +x /opt/ytpmvbot/docker-entrypoint.sh && \
    apt-get -y purge --auto-remove lsb-release

FROM cobaltdocker/eht16-python3:buster-slim AS app

COPY --from=build /root/.local /root/.local
COPY --from=build /opt/ytpmvbot /opt/ytpmvbot

WORKDIR /opt/ytpmvbot

RUN apt-get update && apt-get install ffmpeg -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

ENV PATH=/root/.local/bin:$PATH

ENTRYPOINT [ "/opt/ytpmvbot/docker-entrypoint.sh" ]
CMD [ "python", "ytpmv.py", "||", "echo 'Bot exited with error'" ]