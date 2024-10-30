#!/bin/bash

# Set colors
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
RED=$(tput setaf 1)
RESET=$(tput sgr0)

# Variables to track completion status
postgres_created=false
backend_created=false
frontend_created=false

echo "${GREEN}Starting Docker Prep Script${RESET}"
echo "${YELLOW}Configuring Docker for ModMail Bot${RESET}"

# Print Docker Networks
echo "${YELLOW}[NOTICE] Current Docker Networks:${RESET}"
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}\t{{.Internal}}"
echo "\n"

# Create Docker Network for postgres
echo "${YELLOW}[UPDATE] Creating Docker Network: postgres${RESET}"
if [ "$(docker network ls --format '{{.Name}}' | grep -w postgres)" ]; then
    echo "${RED}[ERROR] Docker network postgres already exists, creating modmail_postgres${RESET}"
    docker network create -d bridge modmail_postgres
else
    docker network create -d bridge postgres
    echo "${GREEN}[OK] Docker network created: postgres${RESET}"
    postgres_created=true
fi
echo "\n"

# Create Docker Network for backend
echo "${YELLOW}[UPDATE] Creating Docker Network: backend${RESET}"
if [ "$(docker network ls --format '{{.Name}}' | grep -w backend)" ]; then
    echo "${RED}[ERROR] Docker network backend already exists, creating modmail_backend${RESET}"
    docker network create -d bridge modmail_backend
else
    docker network create -d bridge backend
    echo "${GREEN}[OK] Docker network created: backend${RESET}"
    backend_created=true
fi
echo "\n"

# Create Docker Network for frontend
echo "${YELLOW}[UPDATE] Creating Docker Network: frontend${RESET}"
if [ "$(docker network ls --format '{{.Name}}' | grep -w frontend)" ]; then
    echo "${RED}[ERROR] Docker network frontend already exists, creating modmail_frontend${RESET}"
    docker network create -d bridge modmail_frontend
else
    docker network create -d bridge frontend
    echo "${GREEN}[OK] Docker network created: frontend${RESET}"
    frontend_created=true
fi

# Print Docker Networks again
echo "${YELLOW}Docker Networks:${RESET}"
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}\t{{.Internal}}"
echo "\n"

# Next steps
echo "${YELLOW}[NOTICE] Next steps:${RESET}"
if ! $postgres_created || ! $backend_created || ! $frontend_created; then
    echo "${YELLOW}Please ensure to update your docker-compose files as needed.${RESET}"
    if ! $postgres_created; then
        echo "${YELLOW} - Update backend/docker-compose to use modmail_postgres${RESET}"
        echo "${YELLOW} - Update frontend/docker-compose to use modmail_postgres${RESET}"
    fi
    if ! $backend_created; then
        echo "${YELLOW} - Update backend/docker-compose to use modmail_backend${RESET}"
    fi
    if ! $frontend_created; then
        echo "${YELLOW} - Update frontend/docker-compose to use modmail_frontend${RESET}"
    fi
else
    echo "${GREEN}All networks are set up correctly, no docker-compose.yml updates needed!${RESET}"
fi


