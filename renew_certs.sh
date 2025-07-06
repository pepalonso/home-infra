#!/bin/bash

# Load environment variables if .env file exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set defaults if environment variables are not set
PROJECT_DIR=${PROJECT_DIR:-$(pwd)}
DOMAIN=${DOMAIN:-your-domain.duckdns.org}

# Navigate to the project directory
cd "$PROJECT_DIR"

# Stop the NGINX container to free up port 80 for Certbot
docker-compose stop nginx

# Renew the certificates quietly
sudo certbot renew --quiet --cert-name "$DOMAIN"

# Start the NGINX container again
docker-compose start nginx
