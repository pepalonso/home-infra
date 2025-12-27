# 🏠 HomeInfra - Personal Home Infrastructure

A comprehensive Docker-based home infrastructure setup featuring Home Assistant, N8N automation, Netdata monitoring, and more.

## 📋 Table of Contents

- [Overview](#overview)
- [Services](#services)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Development vs Production](#development-vs-production)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This project provides a complete home infrastructure stack using Docker Compose, featuring:

- **Home Assistant** - Smart home automation hub
- **N8N** - Workflow automation platform
- **Netdata** - Real-time system monitoring
- **Cloudflare Tunnel** - Secure connection without open ports
- **Terminus** - Terminal access

## 🚀 Services

| Service            | Port (Dev) | Port (Prod)            | Description                 |
| ------------------ | ---------- | ---------------------- | --------------------------- |
| **N8N**            | 8080       | HTTPS (via Cloudflare) | Workflow automation         |
| **Home Assistant** | 8123       | HTTPS (via Cloudflare) | Smart home hub              |
| **Netdata**        | 19999      | HTTPS (via Cloudflare) | System monitoring           |
| **Cloudflared**    | N/A        | N/A (no ports exposed) | Cloudflare Tunnel connector |

## 📋 Prerequisites

- Docker and Docker Compose
- A domain name managed by Cloudflare
- Cloudflare account (free tier works)
- Basic knowledge of Docker and networking

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd HomeInfra
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 3. Generate Configuration Files

```bash
# Run the setup script to generate configuration from templates
./setup.sh
```

This will create your `cloudflared/config.yml` and `configuration.yaml` files from templates using your domain settings.

### 4. Set Up Cloudflare Tunnel (CLI Method)

1. **Install cloudflared:**

   ```bash
   # On Linux (amd64)
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
   chmod +x cloudflared-linux-amd64
   sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

   # Or use package manager (if available)
   # For Debian/Ubuntu:
   # wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   # sudo dpkg -i cloudflared-linux-amd64.deb
   ```

2. **Authenticate cloudflared:**

   ```bash
   cloudflared tunnel login
   ```

   This will open a browser window. Log in to your Cloudflare account and authorize the connection.

3. **Create the tunnel:**

   ```bash
   cloudflared tunnel create home-infra
   ```

   This will:

   - Create a tunnel named "home-infra"
   - Generate a credentials file at `~/.cloudflared/<tunnel-id>.json`
   - Display the Tunnel ID (UUID format) - **note this down!**

4. **Copy credentials file to project:**

   ```bash
   # Replace <tunnel-id> with the actual UUID shown in step 3
   cp ~/.cloudflared/<tunnel-id>.json /home/pep/home-infra/cloudflared/credentials.json
   ```

   Or if you know the tunnel ID, you can use:

   ```bash
   cp ~/.cloudflared/$(cloudflared tunnel list | grep home-infra | awk '{print $1}').json \
      /home/pep/home-infra/cloudflared/credentials.json
   ```

5. **Add Tunnel ID to `.env` file:**

   ```bash
   # Add this line to your .env file (replace with your actual Tunnel ID)
   CLOUDFLARE_TUNNEL_ID=your-tunnel-id-here
   ```

   You can also get the tunnel ID with:

   ```bash
   cloudflared tunnel list
   ```

6. **Routes are configured in `cloudflared/config.yml`:**
   - Routes are automatically generated from the template when you run `./setup.sh`
   - The config file defines:
     - `ha.your-domain.com` → `http://172.30.0.4:8123`
     - `n8n.your-domain.com` → `http://172.30.0.3:5678`
     - `analytics.your-domain.com` → `http://172.30.0.6:19999`
   - Cloudflare will automatically create DNS records based on the config

**📚 For detailed instructions, see [Cloudflare Tunnel CLI Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/get-started/create-local-tunnel/)**

### 6. Start the Services

#### Development Mode

```bash
# Start all services with exposed ports
docker-compose up

# Access services:
# - N8N: http://localhost:8080
# - Home Assistant: http://localhost:8123
# - Netdata: http://localhost:19999
```

#### Production Mode

```bash
# Start services with Cloudflare Tunnel
docker-compose -f docker-compose.yml up -d

# Access via your domain with SSL (automatically handled by Cloudflare)
# - N8N: https://n8n.your-domain.com
# - Home Assistant: https://ha.your-domain.com
# - Netdata: https://analytics.your-domain.com
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Domain Configuration
DOMAIN=your-domain.com
HA_DOMAIN=ha.your-domain.com
N8N_DOMAIN=n8n.your-domain.com
TRMNL_DOMAIN=trmnl.your-domain.com

# Cloudflare Tunnel (get Tunnel ID from Cloudflare Dashboard when creating tunnel)
CLOUDFLARE_TUNNEL_ID=your_tunnel_id_here

# Authentication Credentials
N8N_BASIC_AUTH_USER=your_username
N8N_BASIC_AUTH_PASSWORD=your_secure_password
NETDATA_BASIC_AUTH_USER=your_username
NETDATA_BASIC_AUTH_PASSWORD=your_secure_password

# API Keys
TRMNL_API_KEY=your_api_key
```

### Cloudflare Tunnel Configuration

The Cloudflare Tunnel configuration (`cloudflared/config.yml`) handles:

- Secure connection to Cloudflare's network
- Routing of subdomains to internal services (defined in config file)
- Automatic SSL/TLS termination (handled by Cloudflare)

**Note:**

- SSL certificates are automatically managed by Cloudflare - no manual certificate setup required!
- Routes are defined in `cloudflared/config.yml` (generated from template)
- You need `cloudflared/credentials.json` file from Cloudflare Dashboard

### Configuration Templates

The project uses template files that are processed with environment variables:

- `cloudflared/config.yml` - Tunnel routing configuration
- `config/homeassistant/configuration.yaml.template` → `config/homeassistant/configuration.yaml`

Run `./setup.sh` to generate configuration files from templates.

## 🔄 Development vs Production

### Development Mode (`docker-compose.override.yml`)

- Services exposed directly on localhost
- Nginx disabled
- Easy debugging and development

### Production Mode (`docker-compose.yml`)

- Services exposed via Cloudflare Tunnel
- Automatic SSL/TLS (handled by Cloudflare)
- Application-level authentication (N8N basic auth, HA login)
- No open ports required
- Optimized for security and performance

## 🔒 Security

### Included Security Features

- SSL/TLS encryption (automatic via Cloudflare)
- No open ports on your router/firewall
- Application-level authentication (N8N basic auth, HA login)
- Isolated Docker networks
- Environment variable-based configuration
- DDoS protection (via Cloudflare)

### Security Best Practices

- ✅ Sensitive files excluded via `.gitignore`
- ✅ Environment variables for credentials
- ✅ Cloudflare Tunnel credentials kept secure
- ✅ Application authentication enabled
- ✅ No direct exposure to internet
- ⚠️ Regular security updates recommended
- ⚠️ Strong passwords required
- ⚠️ Keep `cloudflared/credentials.json` secure and never commit it

## 🔧 Troubleshooting

### Common Issues

**Services not accessible:**

```bash
# Check if containers are running
docker-compose ps

# View logs
docker-compose logs [service-name]
```

**Cloudflare Tunnel connection issues:**

```bash
# Check tunnel logs
docker-compose logs cloudflared

# Verify tunnel ID is set correctly
echo $CLOUDFLARE_TUNNEL_ID

# Verify credentials file exists
ls -la cloudflared/credentials.json

# Verify config file is generated correctly
cat cloudflared/config.yml

# Test tunnel connectivity
docker-compose exec cloudflared cloudflared tunnel info
```

**Port conflicts (development mode only):**

```bash
# Check what's using a port
netstat -tulpn | grep :8080

# Stop conflicting services
sudo systemctl stop [service-name]
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs cloudflared
docker-compose logs homeassistant
```

## 📝 License

This project is for personal use. Please ensure you comply with the licenses of all included software.

## 🤝 Contributing

This is a personal infrastructure project. If you find it useful, feel free to fork and adapt it to your needs.

---
