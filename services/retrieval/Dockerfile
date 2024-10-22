# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY services/retrieval /app/services/retrieval
COPY services/common /app/services/common
COPY .env /app/.env

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/services/retrieval/requirements.txt

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1

# Set PYTHONPATH to include the project root
ENV PYTHONPATH=/app

# Expose any required ports (if your service listens on a port)
# EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "-m", "services.retrieval.app"]