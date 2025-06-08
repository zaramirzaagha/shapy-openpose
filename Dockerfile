# Use CUDA base image
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    libopencv-dev \
    libprotobuf-dev \
    protobuf-compiler \
    libgoogle-glog-dev \
    libgflags-dev \
    libboost-all-dev \
    libhdf5-serial-dev \
    python3-pip \
    libatlas-base-dev \
    libglfw3-dev \
    libgles2-mesa-dev \
    libturbojpeg \
    python3.8 \
    python3.8-dev \
    python3.8-distutils \
    && apt-get clean \
    && ln -sf /usr/bin/python3.8 /usr/bin/python3

# Install shapy
WORKDIR /shapy

RUN git clone https://github.com/muelea/shapy.git .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/shapy/attributes/

WORKDIR /shapy/attributes

RUN pip install .

WORKDIR /shapy/mesh-mesh-intersection
    
RUN export CUDA_SAMPLES_INC=$(pwd)/include \
    && pip install --no-cache-dir -r requirements.txt \
    && TORCH_CUDA_ARCH_LIST="8.0" CUDA_HOME=/usr/local/cuda pip install . \
    && pip cache purge

# Install openpose
WORKDIR /openpose

RUN git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose.git .

WORKDIR /openpose/build

RUN cmake .. \
    -DCUDA_ARCH=Manual \
    -DCUDA_ARCH_BIN="80" \
    -DBUILD_PYTHON=ON \
    -DBUILD_CAFFE=ON \
    -DDOWNLOAD_BODY_25_MODEL=OFF \
    -DDOWNLOAD_FACE_MODEL=OFF \
    -DDOWNLOAD_HAND_MODEL=OFF \
    && make -j$(nproc)

# Build FastAPI app
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt
COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
