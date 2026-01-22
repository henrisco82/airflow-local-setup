FROM apache/airflow:3.1.6-python3.12

USER root

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv system-wide
RUN curl -LsSf https://astral.sh/uv/install.sh | env CARGO_HOME=/usr/local UV_INSTALL_DIR=/usr/local/bin sh

# Copy and install Python dependencies as root
COPY requirements.txt /requirements.txt
RUN uv pip install \
    --system \
    --no-cache \
    -r /requirements.txt

USER airflow

WORKDIR /opt/airflow
