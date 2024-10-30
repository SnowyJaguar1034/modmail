#!/bin/sh

# Set colors
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

# Variables to track completion status
postgres_created=false
backend_created=false
frontend_created=false

# Volume flags
postgres_volume_exists=false
modmail_postgres_volume_exists=false

echo "${GREEN}🚀 Starting Docker Prep Script${RESET}"
echo "${YELLOW}🛠️ Configuring Docker for ModMail Bot${RESET}"

# Print Docker Networks
echo "${YELLOW}[NOTICE] Current Docker Networks:${RESET}"
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}\t{{.Internal}}"
echo ""

# Function to create a Docker network
create_network() {
    default_name="$1"
    fallback_name="$2"
    user_input=""

    if docker network ls --format '{{.Name}}' | grep -qw "$default_name"; then
        echo "${YELLOW}[NOTICE] Network '$default_name' already exists!${RESET}"
    else
        echo "${YELLOW}[UPDATE] Creating Docker Network: $default_name${RESET}"
        docker network create -d bridge "$default_name"
        echo "${GREEN}[OK] Docker network created: $default_name${RESET}"
        postgres_created=true
        return
    fi

    printf "Enter a custom name for the network (or press Enter to use '$fallback_name'): "
    read user_input
    name="${user_input:-$fallback_name}"
    echo "${YELLOW}[UPDATE] Creating Docker Network: $name${RESET}"
    docker network create -d bridge "$name"
    echo "${GREEN}[OK] Docker network created: $name${RESET}"
}

# Create Docker Networks
create_network "postgres" "modmail_postgres"
echo ""
create_network "backend" "modmail_backend"
echo ""
create_network "frontend" "modmail_frontend"
echo ""

# Print Docker Networks again
echo "${YELLOW}Docker Networks:${RESET}"
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}\t{{.Internal}}"
echo ""

# Create Docker Volumes
echo "${YELLOW}[UPDATE] Creating Docker Volumes:${RESET}"

# Function to create a Docker volume
create_volume() {
    default_name="$1"
    fallback_name="$2"
    user_input=""

    if docker volume ls --format '{{.Name}}' | grep -qw "$default_name"; then
        echo "${YELLOW}[NOTICE] Volume '$default_name' already exists!${RESET}"
    else
        echo "${YELLOW}[UPDATE] Creating Docker Volume: $default_name${RESET}"
        docker volume create "$default_name"
        echo "${GREEN}[OK] Docker volume created: $default_name${RESET}"
        return
    fi

    printf "Enter a custom name for the volume (or press Enter to use '$fallback_name'): "
    read user_input
    name="${user_input:-$fallback_name}"
    echo "${YELLOW}[UPDATE] Creating Docker Volume: $name${RESET}"
    docker volume create "$name"
    echo "${GREEN}[OK] Docker volume created: $name${RESET}"
}

# Create volumes
create_volume "postgres" "modmail_postgres"
echo ""

# Next steps
echo "${YELLOW}[NOTICE] Next steps:${RESET}"
if ! $postgres_created || ! $backend_created || ! $frontend_created || ! $postgres_volume_exists; then
    echo "${YELLOW}Please ensure to update your docker-compose files as needed.${RESET}"
    if ! $postgres_created; then
        echo "${YELLOW} - Update 'Volumes' section in backend/docker-compose to use modmail_postgres${RESET}"
        echo "${YELLOW} - Update 'Networks' section in backend/docker-compose to use modmail_postgres${RESET}"
        echo "${YELLOW} - Update 'Networks' section in frontend/docker-compose to use modmail_postgres${RESET}"
    fi
    if ! $backend_created; then
        echo "${YELLOW} - Update backend/docker-compose to use modmail_backend${RESET}"
    fi
    if ! $frontend_created; then
        echo "${YELLOW} - Update frontend/docker-compose to use modmail_frontend${RESET}"
    fi
else
    echo "${GREEN}🎉 All networks and volumes are set up correctly, no docker-compose.yml updates needed!${RESET}"
fi
