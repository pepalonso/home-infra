#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set default domain if not provided
DOMAIN=${DOMAIN:-your-domain.duckdns.org}

echo "�� Setting up HomeInfra configuration..."
echo "�� Using domain: $DOMAIN"

# Create cloudflared configuration from template
if [ -f cloudflared/config.yml.template ]; then
    echo "📄 Generating cloudflared config.yml from template..."
    envsubst '$DOMAIN $CLOUDFLARE_TUNNEL_ID' < cloudflared/config.yml.template > cloudflared/config.yml
    echo "✅ cloudflared config.yml generated"
else
    echo "⚠️  cloudflared/config.yml.template not found, using existing config.yml..."
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
echo "2. Set up Cloudflare Tunnel (see README.md for instructions)"
echo "3. Add CLOUDFLARE_TUNNEL_ID to your .env file"
echo "4. Place credentials.json in cloudflared/ directory"
echo "5. Run: docker-compose up -d"
echo ""
echo "🔧 To customize further, edit your .env file and run this script again"