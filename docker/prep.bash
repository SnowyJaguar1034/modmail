#!/bin/bash

# Set colors with -e flag for echo to interpret escape sequences
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

# Default and fallback names for networks and volumes
DEFAULT_NAMES=("postgres" "backend" "frontend")
FALLBACK_NAMES=("modmail_postgres" "modmail_backend" "modmail_frontend")
DEFAULT_VOLUMES=("postgres")

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
    local resources=$(docker "$type" ls --format "{{.Name}} ({{.Driver}})" | grep -v "^NAME" | tr '\n' ', ' | sed 's/,\s*$//')
    
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
    local default_name="$2"
    local fallback_name="$3"
    
    echo -e "${YELLOW}Available naming schemes:${RESET}"
    echo "[d]efault  : $default_name"
    echo "[e]xplicit : $fallback_name"
    echo "[c]ustom   : Enter your own name"
    echo ""
}

# Function to get resource name based on naming scheme
get_resource_name() {
    local type="$1"
    local default_name="$2"
    local fallback_name="$3"
    
    echo -e "  - ${default_name} → \c"
    
    while true; do
        read -p "$type ($default_name) Choice [d/e/c]: " choice
        case ${choice,,} in  # ${choice,,} converts to lowercase
            "d"|"default")
                if resource_exists "$type" "$default_name"; then
                    echo -e "${RED}[ERROR] $type '$default_name' already exists!${RESET}"
                    continue
                fi
                echo -e "${CHOSEN_NETWORKS[$default_name]}"
                return
                ;;
            "e"|"explicit")
                if resource_exists "$type" "$fallback_name"; then
                    echo -e "${RED}[ERROR] $type '$fallback_name' already exists!${RESET}"
                    continue
                fi
                echo -e "${fallback_name}"
                return
                ;;
            "c"|"custom")
                while true; do
                    read -p "Enter custom name for $type ($default_name): " custom_name
                    if [ -z "$custom_name" ]; then
                        echo -e "${RED}[ERROR] Custom name cannot be empty${RESET}"
                        continue
                    fi
                    if resource_exists "$type" "$custom_name"; then
                        echo -e "${RED}[ERROR] $type '$custom_name' already exists!${RESET}"
                        continue
                    fi
                    echo -e "${custom_name}"
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
    echo -e "\n${GREEN}🎯 Pick Resource Names${RESET}"
    
    echo -e "\n${YELLOW}Networks to be created:${RESET}"
    # Display network naming options once at the start
    display_naming_options "network" "${DEFAULT_NAMES[0]}" "${FALLBACK_NAMES[0]}"
    for i in "${!DEFAULT_NAMES[@]}"; do
        CHOSEN_NETWORKS[${DEFAULT_NAMES[$i]}]=$(get_resource_name "network" "${DEFAULT_NAMES[$i]}" "${FALLBACK_NAMES[$i]}")
    done

    echo -e "\n${YELLOW}Volumes to be created:${RESET}"
    # Display volume naming options once at the start
    display_naming_options "volume" "${DEFAULT_VOLUMES[0]}" "modmail_${DEFAULT_VOLUMES[0]}"
    for volume in "${DEFAULT_VOLUMES[@]}"; do
        CHOSEN_VOLUMES[$volume]=$(get_resource_name "volume" "$volume" "modmail_${volume}")
    done
}

[Previous functions remain the same: preview_choices, create_resources, print_summary]

# Main script execution
echo -e "${GREEN}🚀 Starting Docker Prep Script${RESET}"
echo -e "${YELLOW}🛠️ Configuring Docker for ModMail Bot${RESET}"

# Check Docker installation
check_docker

# Display current resources on single lines
display_resources "network"
echo ""
display_resources "volume"
echo -e "\n"

# Collect all resource names first
collect_resource_names

# Preview and confirm choices
preview_choices

# Create all resources
create_resources

# Print final summary
print_summary