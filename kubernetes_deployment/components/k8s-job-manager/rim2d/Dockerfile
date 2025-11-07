FROM rim2d:1.1.1-cuda12.2-ubuntu22.04

RUN apt-get update \
 && apt-get upgrade --assume-yes \
 && apt-get dist-upgrade --assume-yes \
 && apt-get install --no-install-recommends --assume-yes \
    python3 \
    python3-pip \
 && python3 -m pip install \
    s3fs  \
 && apt-get remove --purge --assume-yes \
    python3-pip \
 && apt-get clean \
 && apt autoremove --assume-yes \
 && rm --recursive --force /var/lib/apt/lists/*

WORKDIR /app

COPY main.py .

ENTRYPOINT [ "python3", "./main.py" ]
