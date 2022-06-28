## Building image
## docker build -t ucsdtnel/autolfads:latest-gpu -f gpu.Dockerfile .
##
## Running container in standalone mode
## docker run -it --rm 
##    -v $(pwd):/share
##    ucsdtnel/autolfads:latest-gpu
##       --data /share/data
##       --checkpoint /share/output/lorenz
##       --config-file /share/data/lorenz.yaml
##

# tensorflow-additions requires 2.0.0
ARG TENSORFLOW_VERSION=2.0.0

FROM alpine/git as clone
ARG TENSORFLOW_VERSION
WORKDIR /opt
RUN git clone https://github.com/snel-repo/autolfads-tf2.git \
    && cd autolfads-tf2 \
    && git checkout e6aae8a

FROM tensorflow/tensorflow:$TENSORFLOW_VERSION-gpu-py3
COPY --from=clone /opt/autolfads-tf2/lfads-tf2 /opt/lfads-tf2
WORKDIR /opt/lfads-tf2/
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub \
    && apt-get update && apt-get install -y --no-install-recommends \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install -e .

# This is only necessary for standalone container operation when using PBT
COPY --from=clone /opt/autolfads-tf2/tune-tf2 /opt/tune-tf2
WORKDIR /opt/tune-tf2/
RUN python3 -m pip install -e .

WORKDIR /root
COPY main.py /root/
ENTRYPOINT ["python3", "main.py"]
