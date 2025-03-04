# Base image with CUDA support for GPU acceleration
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch3D (if needed)
RUN python ./scripts/install_pytorch3d.py

# Install custom modules
RUN pip install ./freqencoder ./shencoder ./gridencoder ./raymarching

# Download model data (Google Drive)
RUN apt-get install -y wget unzip && \
    wget --no-check-certificate 'https://drive.google.com/uc?id=18Q2H612CAReFxBd9kxr-i1dD8U1AUfsV' -O data.zip && \
    unzip data.zip -d data && rm data.zip

RUN wget --no-check-certificate 'https://drive.google.com/uc?id=1C2639qi9jvhRygYHwPZDGs8pun3po3W7' -O model.zip && \
    unzip model.zip -d model && rm model.zip

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
