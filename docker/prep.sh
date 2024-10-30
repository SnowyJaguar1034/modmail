#!/bin/bash

# Set colors
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
RED=$(tput setaf 1)
RESET=$(tput sgr0)

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
    echo "${YELLOW}[NOTICE] postgres/docker-compose.yml will require updating to use modmail_postgres${RESET}"
else
    docker network create -d bridge postgres
    echo "${GREEN}[OK] Docker network created: postgres${RESET}"
fi
echo "\n"

# Create Docker Network for backend
echo "${YELLOW}[UPDATE] Creating Docker Network: backend${RESET}"
if [ "$(docker network ls --format '{{.Name}}' | grep -w backend)" ]; then
    echo "${RED}[ERROR] Docker network backend already exists, creating modmail_backend${RESET}"
    docker network create -d bridge modmail_backend
    echo "${YELLOW}[NOTICE] backend/docker-compose.yml will require updating to use modmail_backend${RESET}"
else
    docker network create -d bridge backend
    echo "${GREEN}[OK] Docker network created: backend${RESET}"
fi
echo "\n"

# Create Docker Network for frontend
echo "${YELLOW}[UPDATE] Creating Docker Network: frontend${RESET}"
if [ "$(docker network ls --format '{{.Name}}' | grep -w frontend)" ]; then
    echo "${RED}[ERROR] Docker network frontend already exists, creating modmail_frontend${RESET}"
    docker network create -d bridge modmail_frontend
    echo "${YELLOW}[NOTICE] frontend/docker-compose.yml will require updating to use modmail_frontend${RESET}"
else
    docker network create -d bridge frontend
    echo "${GREEN}[OK] Docker network created: frontend${RESET}"
}

# Print Docker Networks again
echo "${YELLOW}Docker Networks:${RESET}"
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}\t{{.Internal}}"
echo "${GREEN}All networks created successfully!${RESET}"
echo "${YELLOW}Next steps: Please update your docker-compose files accordingly.${RESET}"

