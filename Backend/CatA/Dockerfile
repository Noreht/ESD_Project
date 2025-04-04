# Use official Python slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Set work directory
# In Dockerfile for videoprocrabbmq
WORKDIR /app
COPY . /app
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Expose the port Flask app runs on
EXPOSE 5001

# Command to run your app
CMD ["python", "cata.py"]
