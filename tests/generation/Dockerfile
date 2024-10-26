# Dockerfile

# Use an official Python image as a base
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY tests/generation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the `services` and `tests` directories into the container
COPY tests/generation /app/tests/generation
COPY services /app/services
COPY .env /app/.env

ENV PYTHONPATH=/app

# # Expose any necessary ports
EXPOSE 6379

# # Keep the container running for interaction
CMD ["tail", "-f", "/dev/null"]
