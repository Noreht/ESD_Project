# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

#! istg if anyone removes this line
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Run the notification service
CMD ["python", "notification.py"]
