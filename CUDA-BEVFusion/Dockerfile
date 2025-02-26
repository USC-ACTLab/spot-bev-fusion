FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

RUN DEBIAN_FRONTEND=noninteractive apt-get update -q && \
    apt-get update -q && \
    apt-get install -yq --no-install-recommends \
    build-essential \
    cmake \
    tensorrt \
    python3-pip \
    python-is-python3 \
    python3-argcomplete \
    libprotobuf-dev \
    protobuf-compiler \
    libpython3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install --upgrade pip \
    onnx