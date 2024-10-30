#!/bin/bash
echo "Starting Docker Prep Script"
echo "Configuring Docker for ModMail Bot"

# Print Docker Networks
echo "Existing Docker Networks:"
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}\t{{.Internal}}"
echo "\n"

# Create Docker Network
echo "Creating Docker Network: postgres"
docker network create -d bridge postgres
echo "Creatting Docker Network: backend"
docker network create -d bridge backend
echo "Creating Docker Network: frontend"
docker network create -d bridge frontend

# Print Docker Networks
echo "Docker Networks:"
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}\t{{.Internal}}"
echo "\n"
