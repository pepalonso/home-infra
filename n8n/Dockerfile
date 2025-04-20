# Use the official n8n image as the base
FROM n8nio/n8n:latest

# Install required dependencies
RUN cd /usr/local/lib/node_modules/n8n && npm install axios cheerio

# Expose the default n8n port
EXPOSE 5678
