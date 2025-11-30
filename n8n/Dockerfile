# Use the official n8n image as the base
FROM n8nio/n8n:latest

USER root
# Install required dependencies globally
RUN npm install -g axios cheerio
USER node

# Expose the default n8n port
EXPOSE 5678
