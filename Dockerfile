# Use a slim base Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    libcap2-bin \
    libprotobuf-dev \
    protobuf-compiler \
    libnl-3-dev \
    libnl-genl-3-dev \
    libnl-route-3-dev \
    git \
    pkg-config \
    flex \
    bison \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install nsjail from source
RUN git clone https://github.com/google/nsjail.git /opt/nsjail && \
    cd /opt/nsjail && \
    make && \
    cp nsjail /usr/local/bin/

# Copy app code and nsjail config
COPY app.py .
COPY nsjail.cfg .

# Expose port for Flask app
EXPOSE 8080

# Run the Flask app
CMD ["python3", "app.py"]