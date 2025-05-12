#!/bin/bash
# Navigate to the tasks-server directory
cd /home/palonso/tasks-server

# Stop the NGINX container to free up port 80 for Certbot
docker-compose stop nginx

# Renew the certificates quietly
sudo certbot renew --quiet --cert-name palonso-pi.duckdns.org

# Start the NGINX container again
docker-compose start nginx
