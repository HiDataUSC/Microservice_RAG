#!/bin/bash

# Define the path to the docker-compose file
COMPOSE_FILE_PATH="./tests/generation/docker-compose.yml"

# Step 1: Start Docker Compose services
echo "Starting Docker Compose services"
docker-compose -f $COMPOSE_FILE_PATH up --build -d

# Step 2: Check if Redis container is running
echo "Checking if Redis container is running..."
docker-compose -f $COMPOSE_FILE_PATH exec redis redis-cli ping
if [ $? -ne 0 ]; then
    echo "Error: Redis container is not running as expected."
    docker-compose -f $COMPOSE_FILE_PATH down
    exit 1
fi
echo "Redis container is running successfully."

# Step 3: Run the generation unit test inside the app container
echo "Running generation unit test..."
docker-compose -f $COMPOSE_FILE_PATH exec app pytest tests/generation/unit
echo "Running generation integration test..."
docker-compose -f $COMPOSE_FILE_PATH exec app pytest tests/generation/integration

# Step 4: Stop Docker Compose services (containers will stop, but volumes are preserved)
echo "Stopping Docker Compose services..."
docker-compose -f $COMPOSE_FILE_PATH down -v

# Step 5: Verify if the containers have been removed
echo "Verifying containers have been removed..."
remaining_containers=$(docker ps -a --filter "name=redis" -q)
if [ -n "$remaining_containers" ]; then
    echo "Error: Redis container was not removed after stopping."
    exit 1
else
    echo "Containers have been removed successfully."
fi

echo "Docker Compose test completed successfully."
exit 0
