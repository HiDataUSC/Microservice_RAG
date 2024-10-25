# Dockerfile

# Use an official Python image as a base
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt to the container
COPY ../tests/generation/requirements.txt .
# COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the `services` and `tests` directories into the container
# COPY services/ /app/services
COPY ./tests /app/tests

# Expose any necessary ports
EXPOSE 6379

# Keep the container running for interaction
CMD ["tail", "-f", "/dev/null"]
