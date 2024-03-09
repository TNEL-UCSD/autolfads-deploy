## Building image
## docker build -t ucsdtnel/autolfads:latest -f cpu.Dockerfile .
##
## Running container in standalone mode
## docker run -it --rm 
##    -v $(pwd):/share
##    ucsdtnel/autolfads
##       --data /share/data
##       --checkpoint /share/output/lorenz
##       --config-file /share/data/lorenz.yaml
##

ARG TENSORFLOW_VERSION=2.0.4
# Build tensorflow-addons so it doesn't force installation of tensorflow-gpu
FROM ubuntu:18.04 as tfaddon-cpu
ARG TENSORFLOW_VERSION
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        build-essential \
        curl \
        git \
        rsync \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y \
        python3 \
        python3-pip \
    && python3 -m pip install --upgrade pip \
    && ln -s /usr/bin/python3 /usr/local/bin/python \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt
# Install bazel
ARG BAZELISK_VERSION=1.11.0
RUN mkdir /bazel \
    && curl -LJ "https://github.com/bazelbuild/bazelisk/releases/download/v${BAZELISK_VERSION}/bazelisk-linux-amd64" > /opt/bazelisk \
    && chmod +x /opt/bazelisk
# Generated artifact located in /opt/addons/artifacts/tensorflow_addons-*.whl
RUN git clone https://github.com/tensorflow/addons.git \
    && cd addons \
    && git checkout v0.6.0 --quiet \
    && sed -i s/tensorflow-gpu\ ==\ 2.0.0-rc0/tensorflow\ ==\ ${TENSORFLOW_VERSION}/ setup.py \
    && sed -i s/tensorflow\ ==\ 2.0.0-rc0/tensorflow\ ==\ ${TENSORFLOW_VERSION}/ setup.py \
    && mv build_deps/requirements.txt build_deps/requirements.txt.bak \
    && echo "tensorflow==${TENSORFLOW_VERSION}" > build_deps/requirements.txt \
    && echo "y" | ./configure.sh \
    && ../bazelisk build build_pip_pkg \
    && bazel-bin/build_pip_pkg artifacts

FROM alpine/git as clone
ARG TENSORFLOW_VERSION
WORKDIR /opt
RUN git clone https://github.com/snel-repo/autolfads-tf2.git \
    && cd autolfads-tf2 \
    && git checkout e6aae8a

FROM tensorflow/tensorflow:${TENSORFLOW_VERSION}-py3
COPY --from=tfaddon-cpu /opt/addons/artifacts/ /opt/tensorflow-addons
COPY --from=clone /opt/autolfads-tf2/lfads-tf2 /opt/lfads-tf2
WORKDIR /opt/lfads-tf2/
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install /opt/tensorflow-addons/tensorflow_addons-*.whl \
    && sed -i s/tensorflow-gpu==2.0.0/tensorflow/ /opt/lfads-tf2/setup.py \
    && sed -i s/tensorflow-addons==0.6/tensorflow-addons/ /opt/lfads-tf2/setup.py \
    && python3 -m pip install -e .

# This is only necessary for standalone container operation when using PBT
COPY --from=clone /opt/autolfads-tf2/tune-tf2 /opt/tune-tf2
WORKDIR /opt/tune-tf2/
RUN python3 -m pip install -e .

WORKDIR /root
COPY main.py /root/
ENTRYPOINT ["python3", "main.py"]
