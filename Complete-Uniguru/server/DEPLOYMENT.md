# UniGuru Backend Deployment Guide

## 🚀 Production Deployment Checklist

### 1. Environment Configuration

Create a production `.env` file with the following required variables:

```bash
# Database Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/uniguru

# JWT Configuration (IMPORTANT: Use strong secrets in production)
JWT_SECRET=your-super-secure-jwt-secret-key-here
JWT_EXPIRES_IN=7d
JWT_COOKIE_EXPIRE=7

# Ollama Configuration (REQUIRED for AI features)
OLLAMA_BASE_URL=http://localhost:11434
# Optional: Ngrok URL for external access (takes priority over local URL)
OLLAMA_NGROK_URL=https://your-ngrok-url.ngrok-free.app/api/generate

# Google OAuth Configuration (Optional)
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# Server Configuration
PORT=8000
NODE_ENV=production

# CORS Configuration
FRONTEND_URL=https://your-frontend-domain.com

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# File Upload Configuration
MAX_FILE_SIZE=10485760
UPLOAD_PATH=./uploads

# Security Configuration
SESSION_SECRET=your-session-secret-here
```

### 2. Database Setup

1. **MongoDB Atlas** (Recommended):
   - Create a MongoDB Atlas cluster
   - Create a database user
   - Whitelist your server IP
   - Get the connection string

2. **Local MongoDB**:
   - Install MongoDB
   - Start MongoDB service
   - Create database: `uniguru`

### 3. API Keys Setup

1. **Ollama Setup**:
   - Install Ollama from https://ollama.ai/
   - Pull the llama3.1 model: `ollama pull llama3.1`
   - Ensure Ollama is running on http://localhost:11434
   - Configure OLLAMA_BASE_URL in environment variables
   - Optional: Expose via ngrok for external access: `ngrok http 11434`
   - If using ngrok, set OLLAMA_NGROK_URL to your ngrok URL + `/api/generate`

2. **Google OAuth** (Optional):
   - Go to Google Cloud Console
   - Create OAuth 2.0 credentials
   - Add authorized domains

### 4. Server Deployment

#### Option A: Traditional VPS/Server

```bash
# Clone and setup
git clone <your-repo>
cd uniguru/server
npm install --production

# Set environment variables
cp .env.example .env
# Edit .env with your production values

# Start with PM2 (recommended)
npm install -g pm2
pm2 start server.js --name "uniguru-backend"
pm2 startup
pm2 save
```

#### Option B: Docker Deployment

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

EXPOSE 8000

CMD ["npm", "start"]
```

```bash
# Build and run
docker build -t uniguru-backend .
docker run -d -p 8000:8000 --env-file .env uniguru-backend
```

#### Option C: Cloud Platforms

**Heroku**:
```bash
heroku create uniguru-backend
heroku config:set MONGODB_URI=your-mongodb-uri
heroku config:set OLLAMA_BASE_URL=your-ollama-url
# ... set other env vars
git push heroku main
```

**Railway/Render/DigitalOcean App Platform**:
- Connect your GitHub repository
- Set environment variables in the platform dashboard
- Deploy automatically

### 5. Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 80;
    server_name your-api-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 6. SSL Certificate

```bash
# Using Certbot (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-api-domain.com
```

### 7. Monitoring & Logging

```bash
# PM2 monitoring
pm2 monit

# View logs
pm2 logs uniguru-backend

# Restart if needed
pm2 restart uniguru-backend
```

### 8. Security Considerations

- ✅ Use HTTPS in production
- ✅ Set strong JWT secrets
- ✅ Configure CORS properly
- ✅ Use rate limiting
- ✅ Keep dependencies updated
- ✅ Use environment variables for secrets
- ✅ Enable MongoDB authentication
- ✅ Use a firewall

### 9. Performance Optimization

- Use PM2 cluster mode for multiple CPU cores
- Enable gzip compression
- Set up CDN for static files
- Monitor memory usage
- Use database indexing

### 10. Backup Strategy

- Regular MongoDB backups
- Environment variables backup
- Code repository backup
- File uploads backup

## 🔧 Troubleshooting

### Common Issues:

1. **MongoDB Connection Failed**:
   - Check connection string
   - Verify network access
   - Check credentials

2. **Groq API Errors**:
   - Verify API key
   - Check rate limits
   - Monitor usage

3. **CORS Issues**:
   - Update FRONTEND_URL
   - Check allowed origins

4. **File Upload Issues**:
   - Check upload directory permissions
   - Verify file size limits

### Health Check Endpoints:

- `GET /health` - Server status
- `GET /api/v1/guru/models` - Available AI models
- `GET /api/v1/feature/tools` - Available features

## 📞 Support

For deployment issues, check:
1. Server logs
2. Database connectivity
3. Environment variables
4. API key validity
5. Network configuration
