#!/bin/sh

# Check if Docker is installed
# Check if Docker is installed
if ! [ -x "$(command -v docker)" ]; then
    echo "${RED}[ERROR] Docker is not installed. Please install Docker and try again.${RESET}"
    exit 1
fi

# Set colors
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

# Default and fallback names for networks and volumes
DEFAULT_NAMES=("postgres" "backend" "frontend")
FALLBACK_NAMES=("modmail_postgres" "modmail_backend" "modmail_frontend")
DEFAULT_VOLUMES=("postgres" "modmail_postgres")

echo "${GREEN}🚀 Starting Docker Prep Script${RESET}"
echo "${YELLOW}🛠️ Configuring Docker for ModMail Bot${RESET}"

# Print Docker Networks
echo "${YELLOW}[NOTICE] Current Docker Networks:${RESET}"
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}\t{{.Internal}}"
echo ""

# Generalized function to create a Docker network or volume
create_resource() {
    type="$1"          # "network" or "volume"
    default_name="$2"
        if ! docker "$type" create "$default_name"; then
            echo "${RED}[ERROR] Failed to create Docker $type: $default_name${RESET}"
            exit 1
        fi

    if docker "$type" ls --format '{{.Name}}' | grep -qw "$default_name"; then
        echo "${YELLOW}[NOTICE] $type '$default_name' already exists!${RESET}"
    else
        echo "${YELLOW}[UPDATE] Creating Docker $type: $default_name${RESET}"
    if ! docker "$type" create "$name"; then
        echo "${RED}[ERROR] Failed to create Docker $type: $name${RESET}"
        exit 1
    fi
        echo "${GREEN}[OK] Docker $type created: $default_name${RESET}"
        return
    fi

    printf "Enter a custom name for the $type (or press Enter to use '$fallback_name'): "
    read user_input
    name="${user_input:-$fallback_name}"
    echo "${YELLOW}[UPDATE] Creating Docker $type: $name${RESET}"
    docker "$type" create "$name"
    echo "${GREEN}[OK] Docker $type created: $name${RESET}"
}

# Create Docker Networks
for i in "${!DEFAULT_NAMES[@]}"; do
    create_resource "network" "${DEFAULT_NAMES[i]}" "${FALLBACK_NAMES[i]}"
    echo ""
done

# Create Docker Volumes
for volume_name in "${DEFAULT_VOLUMES[@]}"; do
    create_resource "volume" "$volume_name" "modmail_${volume_name}"
    echo ""
done

# Next steps
echo "${YELLOW}[NOTICE] Next steps:${RESET}"
missing_items=false

for i in "${!DEFAULT_NAMES[@]}"; do
    if ! docker network ls --format '{{.Name}}' | grep -qw "${DEFAULT_NAMES[i]}"; then
        echo "${YELLOW} - Update docker-compose files to use ${FALLBACK_NAMES[i]} for ${DEFAULT_NAMES[i]}${RESET}"
        missing_items=true
    fi
done

for volume in "${DEFAULT_VOLUMES[@]}"; do
    if ! docker volume ls --format '{{.Name}}' | grep -qw "$volume"; then
        echo "${YELLOW} - Update docker-compose files to use modmail_${volume} for $volume${RESET}"
        missing_items=true
    fi
done

if [ "$missing_items" = false ]; then
    echo "${GREEN}🎉 All networks and volumes are set up correctly, no docker-compose.yml updates needed!${RESET}"
fi