FROM ubuntu:18.04

LABEL maintainer="Munseong Jeong <ryan.m.jeong@hotmail.com>"

# Faster mirror for Korea + install Python 3.8 (Ubuntu 18.04 ships 3.6 by default)
RUN sed -i 's/kr.archive.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list \
  && sed -i 's/archive.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list \
  && sed -i 's/security.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list \
  && apt-get update && apt-get install -y \
  software-properties-common \
  && add-apt-repository ppa:deadsnakes/ppa -y \
  && apt-get update && apt-get install -y \
  python3-pip \
  python3.8 \
  python3.8-dev \
  && ln -sf /usr/bin/python3.8 /usr/local/bin/python \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# copy source & install deps
WORKDIR /srv/app
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server/app ./app

EXPOSE 33333
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "33333"]
