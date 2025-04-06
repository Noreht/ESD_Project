FROM python:3.11-slim

# Install system dependencies for OpenCV and Tesseract
RUN echo 'Acquire::http::Pipeline-Depth "0";' > /etc/apt/apt.conf.d/99nopipelining


RUN apt-get clean && rm -rf /var/lib/apt/lists/* \
    && apt-get update --fix-missing \
    && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
# In Dockerfile for videoprocrabbmq
WORKDIR /app
COPY . /app

COPY ./rabbitmq /app/rabbitmq
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY . .

# Expose any needed ports (if applicable)
# EXPOSE 5000

# Run the main script
CMD ["python", "vidprocrabbmq.py"]
