#!/bin/bash

# Set colors with -e flag for echo to interpret escape sequences
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

# Default and fallback names for networks and volumes
MODMAIL_NETWORKS=("postgres" "backend" "frontend")          # Database, API, and Web UI networks
MODMAIL_NETWORK_FALLBACKS=("modmail_postgres" "modmail_backend" "modmail_frontend")
MODMAIL_DB_VOLUMES=("postgres")                            # Persistent storage for ModMail database

# Description mappings for networks and volumes
declare -A NETWORK_DESCRIPTIONS=(
    ["postgres"]="Database Network"
    ["backend"]="API Network"
    ["frontend"]="Web UI Network"
)

declare -A VOLUME_DESCRIPTIONS=(
    ["postgres"]="Database Storage"
)

# Arrays to store chosen names
declare -A CHOSEN_NETWORKS
declare -A CHOSEN_VOLUMES

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
    docker "$type" ls -q --filter "name=^${name}$" | grep -q .
    return $?
}

# Function to display existing resources
display_resources() {
    local type="$1"
    local resources=$(docker "$type" ls --format "{{.Name}} ({{.Driver}})" | grep -v "^NAME" | tr '\n' ',' | sed 's/,\s*$//')
    
    echo -ne "${YELLOW}Current Docker ${type^}s: ${RESET}"
    if [ -z "$resources" ]; then
        echo "No ${type}s found"
    else
        echo "$resources"
    fi
}

# Function to display naming options
display_naming_options() {
    local type="$1"
    local -n default_arr="$2"
    local -n fallback_arr="$3"
    local -n descriptions="$4"
    
    echo -e "${YELLOW}Available naming schemes for ModMail ${type}s:${RESET}"
    for i in "${!default_arr[@]}"; do
        local fallback_name
        if [ "$type" = "volume" ]; then
            fallback_name="modmail_${default_arr[$i]}"
        else
            fallback_name="${fallback_arr[$i]}"
        fi
        
        echo "${descriptions[${default_arr[$i]}]} (${default_arr[$i]}):"
        echo "  [d]efault  : ${default_arr[$i]}"
        echo "  [e]xplicit : ${fallback_name}"
        echo "  [c]ustom   : Enter your own name"
        echo ""
    done
}

# Function to get resource name based on naming scheme
get_resource_name() {
    local type="$1"
    local default_name="$2"
    local fallback_name="$3"
    local description="$4"
    
    while true; do
        read -p "$description ($default_name) Choice [d/e/c]: " choice
        case ${choice,,} in  # ${choice,,} converts to lowercase
            "d"|"default")
                if resource_exists "$type" "$default_name"; then
                    echo -e "${RED}[ERROR] $type '$default_name' already exists!${RESET}"
                    continue
                fi
                echo "$default_name"
                return
                ;;
            "e"|"explicit")
                if resource_exists "$type" "$fallback_name"; then
                    echo -e "${RED}[ERROR] $type '$fallback_name' already exists!${RESET}"
                    continue
                fi
                echo "$fallback_name"
                return
                ;;
            "c"|"custom")
                while true; do
                    read -p "Enter custom name for $description ($default_name): " custom_name
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
                echo -e "${RED}Invalid choice. Please enter 'd', 'e', or 'c'${RESET}"
                ;;
        esac
    done
}

# Function to collect all resource names
collect_resource_names() {
    echo -e "${GREEN}🎯 Pick Resource Names${RESET}"
    
    echo -e "\n${YELLOW}Networks to be created:${RESET}"
    display_naming_options "network" MODMAIL_NETWORKS MODMAIL_NETWORK_FALLBACKS NETWORK_DESCRIPTIONS
    
    for name in "${MODMAIL_NETWORKS[@]}"; do
        CHOSEN_NETWORKS[$name]=$(get_resource_name "network" "$name" "modmail_$name" "${NETWORK_DESCRIPTIONS[$name]}")
    done

    echo -e "\n${YELLOW}Volumes to be created:${RESET}"
    display_naming_options "volume" MODMAIL_DB_VOLUMES MODMAIL_DB_VOLUMES VOLUME_DESCRIPTIONS
    
    for volume in "${MODMAIL_DB_VOLUMES[@]}"; do
        CHOSEN_VOLUMES[$volume]=$(get_resource_name "volume" "$volume" "modmail_${volume}" "${VOLUME_DESCRIPTIONS[$volume]}")
    done
}

# Function to preview chosen names
preview_choices() {
    echo -e "\n${GREEN}📋 Final Review:${RESET}"
    echo -e "${YELLOW}Networks to create:${RESET}"
    for name in "${MODMAIL_NETWORKS[@]}"; do
        echo "  ${NETWORK_DESCRIPTIONS[$name]}: ${CHOSEN_NETWORKS[$name]}"
    done
    
    echo -e "\n${YELLOW}Volumes to create:${RESET}"
    for name in "${MODMAIL_DB_VOLUMES[@]}"; do
        echo "  ${VOLUME_DESCRIPTIONS[$name]}: ${CHOSEN_VOLUMES[$name]}"
    done
    
    while true; do
        read -p $'\n'"Proceed with creation? [y/N]: " confirm
        case ${confirm,,} in
            "y"|"yes")
                return 0
                ;;
            "n"|"no"|"")
                echo -e "${RED}Operation cancelled by user${RESET}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid choice. Please enter 'y' or 'n'${RESET}"
                ;;
        esac
    done
}

# Function to create resources
create_resources() {
    echo -e "\n${YELLOW}Creating Networks:${RESET}"
    for name in "${MODMAIL_NETWORKS[@]}"; do
        echo -e "${YELLOW}[UPDATE] Creating network (${NETWORK_DESCRIPTIONS[$name]}): ${CHOSEN_NETWORKS[$name]}${RESET}"
        if ! docker network create "${CHOSEN_NETWORKS[$name]}"; then
            echo -e "${RED}[ERROR] Failed to create network: ${CHOSEN_NETWORKS[$name]}${RESET}"
            exit 1
        fi
        echo -e "${GREEN}[OK] Network created: ${CHOSEN_NETWORKS[$name]}${RESET}"
    done

    echo -e "\n${YELLOW}Creating Volumes:${RESET}"
    for name in "${MODMAIL_DB_VOLUMES[@]}"; do
        echo -e "${YELLOW}[UPDATE] Creating volume (${VOLUME_DESCRIPTIONS[$name]}): ${CHOSEN_VOLUMES[$name]}${RESET}"
        if ! docker volume create "${CHOSEN_VOLUMES[$name]}"; then
            echo -e "${RED}[ERROR] Failed to create volume: ${CHOSEN_VOLUMES[$name]}${RESET}"
            exit 1
        fi
        echo -e "${GREEN}[OK] Volume created: ${CHOSEN_VOLUMES[$name]}${RESET}"
    done
}

# Function to print final summary
print_summary() {
    echo -e "\n${GREEN}📋 Summary of Changes:${RESET}"
    echo -e "${YELLOW}Created Networks:${RESET}"
    for name in "${MODMAIL_NETWORKS[@]}"; do
        echo "  ${NETWORK_DESCRIPTIONS[$name]}: ${CHOSEN_NETWORKS[$name]}"
    done
    
    echo -e "\n${YELLOW}Created Volumes:${RESET}"
    for name in "${MODMAIL_DB_VOLUMES[@]}"; do
        echo "  ${VOLUME_DESCRIPTIONS[$name]}: ${CHOSEN_VOLUMES[$name]}"
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

# Display current resources on single lines
display_resources "network"
echo ""
display_resources "volume"
echo ""

# Collect all resource names first
collect_resource_names

# Preview and confirm choices
preview_choices

# Create all resources
create_resources

# Print final summary
print_summary