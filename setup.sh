#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set default domain if not provided
DOMAIN=${DOMAIN:-your-domain.duckdns.org}

echo "�� Setting up HomeInfra configuration..."
echo "�� Using domain: $DOMAIN"

# Create nginx configuration from template
if [ -f nginx/nginx.conf.template ]; then
    echo "📄 Generating nginx.conf from template..."
    envsubst '$DOMAIN' < nginx/nginx.conf.template > nginx/nginx.conf
    echo "✅ nginx.conf generated"
else
    echo "⚠️  nginx.conf.template not found, skipping..."
fi

# Create Home Assistant configuration from template
if [ -f config/homeassistant/configuration.yaml.template ]; then
    echo "📄 Generating Home Assistant configuration from template..."
    envsubst '$DOMAIN' < config/homeassistant/configuration.yaml.template > config/homeassistant/configuration.yaml
    echo "✅ Home Assistant configuration generated"
else
    echo "⚠️  configuration.yaml.template not found, skipping..."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review the generated configuration files"
echo "2. Set up SSL certificates for your domain"
echo "3. Run: docker-compose up -d"
echo ""
echo "🔧 To customize further, edit your .env file and run this script again"