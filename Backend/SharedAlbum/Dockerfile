# Use the official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set working directory
# In Dockerfile for videoprocrabbmq
WORKDIR /app
COPY . /app
COPY ./rabbitmq /app/rabbitmq


# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5100

# Command to run the app
CMD ["python", "sharedalbum.py"]
