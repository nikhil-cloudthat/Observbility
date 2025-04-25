# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY kubescape_python.py /app

# Install required Python libraries
RUN pip install --no-cache-dir flask prometheus_client beautifulsoup4 kubernetes

# Expose the application's port
EXPOSE 8000

# Run the application
CMD ["python", "kubescape_python.py"]
