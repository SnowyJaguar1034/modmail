#!/bin/bash

# Set colors with -e flag for echo to interpret escape sequences
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

# Default and fallback names for networks and volumes
DEFAULT_NAMES=("postgres" "backend" "frontend")
FALLBACK_NAMES=("modmail_postgres" "modmail_backend" "modmail_frontend")
DEFAULT_VOLUMES=("postgres" "modmail_postgres")

# Array to store created resources for summary
declare -A CREATED_RESOURCES

# Function to check if Docker is installed
check_docker() {
    if ! [ -x "$(command -v docker)" ]; then
        echo -e "${RED}[ERROR] Docker is not installed. Please install Docker and try again.${RESET}"
        exit 1
    fi
}

# Function to check if resource exists
resource_exists() {
    local type="$1"
    local name="$2"
    docker "$type" ls --format '{{.Name}}' | grep -qw "$name"
    return $?
}

# Function to get resource name based on naming scheme
get_resource_name() {
    local type="$1"
    local default_name="$2"
    local fallback_name="$3"
    
    echo -e "${YELLOW}Choose naming scheme for $type '$default_name':${RESET}"
    echo "Options: default ($default_name)"
    echo "         explicit ($fallback_name)"
    echo "         custom (enter your own name)"
    
    while true; do
        read -p "Enter choice [default/explicit/custom]: " choice
        case ${choice,,} in  # ${choice,,} converts to lowercase
            "default")
                if resource_exists "$type" "$default_name"; then
                    echo -e "${RED}[ERROR] $type '$default_name' already exists!${RESET}"
                    continue
                fi
                echo "$default_name"
                return
                ;;
            "explicit")
                if resource_exists "$type" "$fallback_name"; then
                    echo -e "${RED}[ERROR] $type '$fallback_name' already exists!${RESET}"
                    continue
                fi
                echo "$fallback_name"
                return
                ;;
            "custom")
                while true; do
                    read -p "Enter custom name: " custom_name
                    if [ -z "$custom_name" ]; then
                        echo -e "${RED}[ERROR] Custom name cannot be empty${RESET}"
                        continue
                    fi
                    if resource_exists "$type" "$custom_name"; then
                        echo -e "${RED}[ERROR] $type '$custom_name' already exists!${RESET}"
                        continue
                    fi
                    echo "$custom_name"
                    return
                done
                ;;
            *)
                echo -e "${RED}Invalid choice. Please enter 'default', 'explicit', or 'custom'${RESET}"
                ;;
        esac
    done
}

# Function to create a Docker resource
create_resource() {
    local type="$1"
    local default_name="$2"
    local fallback_name="$3"
    
    echo -e "${YELLOW}[UPDATE] Setting up Docker $type: $default_name${RESET}"
    
    local resource_name
    resource_name=$(get_resource_name "$type" "$default_name" "$fallback_name")
    
    echo -e "${YELLOW}[UPDATE] Creating Docker $type: $resource_name${RESET}"
    if ! docker "$type" create "$resource_name"; then
        echo -e "${RED}[ERROR] Failed to create Docker $type: $resource_name${RESET}"
        exit 1
    fi
    echo -e "${GREEN}[OK] Docker $type created: $resource_name${RESET}"
    echo ""
    
    # Store the created resource for summary
    CREATED_RESOURCES["${type}_${default_name}"]="$resource_name"
}

# Function to print summary
print_summary() {
    echo -e "\n${GREEN}📋 Summary of Changes:${RESET}"
    echo -e "${YELLOW}Created Networks:${RESET}"
    for name in "${DEFAULT_NAMES[@]}"; do
        if [[ -n "${CREATED_RESOURCES[network_${name}]}" ]]; then
            echo "  - ${name} → ${CREATED_RESOURCES[network_${name}]}"
        fi
    done
    
    echo -e "\n${YELLOW}Created Volumes:${RESET}"
    for name in "${DEFAULT_VOLUMES[@]}"; do
        if [[ -n "${CREATED_RESOURCES[volume_${name}]}" ]]; then
            echo "  - ${name} → ${CREATED_RESOURCES[volume_${name}]}"
        fi
    done
    
    echo -e "\n${YELLOW}Next Steps:${RESET}"
    echo "1. Update your docker-compose.yml file with these resource names"
    echo "2. Make sure your container configurations reference these names"
    echo -e "${GREEN}🎉 Docker environment setup completed!${RESET}"
}

# Main script execution
echo -e "${GREEN}🚀 Starting Docker Prep Script${RESET}"
echo -e "${YELLOW}🛠️ Configuring Docker for ModMail Bot${RESET}"

# Check Docker installation
check_docker

# Print Docker Networks
echo -e "${YELLOW}[NOTICE] Current Docker Networks:${RESET}"
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}\t{{.Internal}}"
echo ""

# Create Docker Networks
for i in "${!DEFAULT_NAMES[@]}"; do
    create_resource "network" "${DEFAULT_NAMES[i]}" "${FALLBACK_NAMES[i]}"
done

# Create Docker Volumes
for i in "${!DEFAULT_VOLUMES[@]}"; do
    create_resource "volume" "${DEFAULT_VOLUMES[i]}" "modmail_${DEFAULT_VOLUMES[i]}"
done

# Print summary of changes
print_summary