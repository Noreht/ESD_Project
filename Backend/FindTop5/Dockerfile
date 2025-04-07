FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code into the container
COPY findtop5.py /app/

# Expose the port the app runs on
EXPOSE 5300

# Run the Flask app
CMD ["python", "findtop5.py"]