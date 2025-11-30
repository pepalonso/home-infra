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
- **Nginx** - Reverse proxy with SSL termination
- **Terminus** - Terminal access

## 🚀 Services

| Service            | Port (Dev) | Port (Prod)     | Description         |
| ------------------ | ---------- | --------------- | ------------------- |
| **N8N**            | 8080       | 443 (via Nginx) | Workflow automation |
| **Home Assistant** | 8123       | 443 (via Nginx) | Smart home hub      |
| **Netdata**        | 19999      | 443 (via Nginx) | System monitoring   |
| **Nginx**          | Disabled   | 80/443          | Reverse proxy       |

## 📋 Prerequisites

- Docker and Docker Compose
- A domain name (e.g., DuckDNS)
- SSL certificates (Let's Encrypt recommended)
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

This will create your `nginx.conf` and `configuration.yaml` files from templates using your domain settings.

### 4. Set Up SSL Certificates

```bash
# Install certbot and obtain certificates
sudo certbot certonly --standalone -d your-domain.com
```

### 5. Start the Services

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
# Start services with Nginx reverse proxy
docker-compose -f docker-compose.yml up -d

# Access via your domain with SSL
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

# Authentication Credentials
N8N_BASIC_AUTH_USER=your_username
N8N_BASIC_AUTH_PASSWORD=your_secure_password
NETDATA_BASIC_AUTH_USER=your_username
NETDATA_BASIC_AUTH_PASSWORD=your_secure_password

# API Keys
TRMNL_API_KEY=your_api_key
```

### SSL Certificates

The setup expects SSL certificates in `/etc/letsencrypt/live/your-domain.com/`:

- `fullchain.pem` - Full certificate chain
- `privkey.pem` - Private key

### Configuration Templates

The project uses template files that are processed with environment variables:

- `nginx/nginx.conf.template` → `nginx/nginx.conf`
- `config/homeassistant/configuration.yaml.template` → `config/homeassistant/configuration.yaml`

Run `./setup.sh` to generate configuration files from templates.

### Nginx Configuration

The Nginx configuration (`nginx/nginx.conf`) handles:

- SSL termination
- Reverse proxy routing
- Basic authentication
- CORS headers
- Security headers

## 🔄 Development vs Production

### Development Mode (`docker-compose.override.yml`)

- Services exposed directly on localhost
- Nginx disabled
- Easy debugging and development

### Production Mode (`docker-compose.yml`)

- Services behind Nginx reverse proxy
- SSL termination
- Basic authentication enabled
- Optimized for security and performance

## 🔒 Security

### Included Security Features

- SSL/TLS encryption
- Basic authentication for sensitive services
- Reverse proxy with security headers
- Isolated Docker networks
- Environment variable-based configuration

### Security Best Practices

- ✅ Sensitive files excluded via `.gitignore`
- ✅ Environment variables for credentials
- ✅ SSL certificates properly configured
- ✅ Basic authentication enabled
- ⚠️ Regular security updates recommended
- ⚠️ Strong passwords required

## 🔧 Troubleshooting

### Common Issues

**Services not accessible:**

```bash
# Check if containers are running
docker-compose ps

# View logs
docker-compose logs [service-name]
```

**SSL certificate issues:**

```bash
# Renew certificates
sudo certbot renew --cert-name your-domain.com

# Check certificate validity
openssl x509 -in /etc/letsencrypt/live/your-domain.com/fullchain.pem -text -noout
```

**Port conflicts:**

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
docker-compose logs nginx
docker-compose logs homeassistant
```

## 📝 License

This project is for personal use. Please ensure you comply with the licenses of all included software.

## 🤝 Contributing

This is a personal infrastructure project. If you find it useful, feel free to fork and adapt it to your needs.

---
