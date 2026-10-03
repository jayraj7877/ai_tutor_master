# VPS Deployment Guide (Hostinger KVM / Ubuntu / Debian)

Follow this step-by-step guide to deploy your AI English Tutor SaaS Backend on your VPS using Docker Compose, NGINX, and free SSL (Certbot).

---

## Step 1: Connect to your VPS via SSH

Open your terminal or PowerShell and SSH into your VPS server:
```bash
ssh root@YOUR_VPS_IP
```

---

## Step 2: Install Docker & Docker Compose on VPS

Run the official Docker installation script on your VPS:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

Verify Docker installation:
```bash
docker --version
docker compose version
```

---

## Step 3: Clone Project & Configure `.env`

1. Clone your project code onto the VPS:
   ```bash
   git clone <YOUR_GIT_REPO_URL> ai_tutor_backend
   cd ai_tutor_backend
   ```

2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   nano .env
   ```

3. Update settings inside `.env`:
   ```env
   APP_NAME="AI English Tutor Backend"
   ENVIRONMENT="production"
   DEBUG=false
   SECRET_KEY="your-random-secure-production-key"

   DATABASE_URL="postgresql+asyncpg://postgres:postgres@db:5432/ai_tutor_db"
   DATABASE_URL_SYNC="postgresql://postgres:postgres@db:5432/ai_tutor_db"
   REDIS_URL="redis://redis:6379/0"

   # LLM & TTS Settings
   LLM_PROVIDER="mock"       # Or "openai", "gemini"
   LLM_API_KEY=""            # Your API Key if using OpenAI/Gemini
   TTS_PROVIDER="gtts"       # High-quality local neural TTS
   ```

---

## Step 4: Build & Start Containers

Run Docker Compose in detached mode (`-d`):
```bash
docker compose up -d --build
```

Check running container status:
```bash
docker compose ps
```

---

## Step 5: Run Database Migrations

Apply Alembic migrations to set up PostgreSQL database tables:
```bash
docker compose exec api alembic upgrade head
```

---

## Step 6: Configure NGINX Reverse Proxy & Free SSL (HTTPS + WSS)

1. Install NGINX & Certbot:
   ```bash
   apt update && apt install -y nginx certbot python3-certbot-nginx
   ```

2. Create an NGINX configuration file for your domain (e.g., `api.yourdomain.com`):
   ```bash
   nano /etc/nginx/sites-available/ai_tutor
   ```

3. Paste the following NGINX block (with WebSocket support):
   ```nginx
   server {
       server_name api.yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_http_version 1.1;

           # WebSocket Support
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "Upgrade";

           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;

           # Timeouts for streaming
           proxy_read_timeout 3600s;
           proxy_send_timeout 3600s;
       }
   }
   ```

4. Enable the configuration and test NGINX:
   ```bash
   ln -s /etc/nginx/sites-available/ai_tutor /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

5. Enable HTTPS SSL with Certbot:
   ```bash
   certbot --nginx -d api.yourdomain.com
   ```

---

## Step 7: Verify Production Deployment

1. **Health Check**:
   ```bash
   curl https://api.yourdomain.com/api/v1/health
   ```
   *Response*: `{"status":"ok","service":"ai-english-tutor-backend"}`

2. **Readiness Check**:
   ```bash
   curl https://api.yourdomain.com/api/v1/ready
   ```
   *Response*: `{"status":"ready","database":"ok","redis":"ok"}`

3. **Android Client Production Base URLs**:
   - HTTP Base URL: `https://api.yourdomain.com/api/v1`
   - WebSocket URL: `wss://api.yourdomain.com/api/v1/conversation/stream`
