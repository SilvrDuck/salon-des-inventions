FROM python:3.13-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PDM
RUN pip install -U pdm

# Disable PDM update check
ENV PDM_CHECK_UPDATE=false

COPY pyproject.toml pdm.lock ./
COPY ./src ./src

RUN pdm install

ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD ["pdm", "run", "python", "src/salon/chat/main.py"]
