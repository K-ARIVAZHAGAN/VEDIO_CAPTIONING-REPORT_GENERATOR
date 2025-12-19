# 🚀 QUICK START - Video Captioning System

## ⚡ Zero-Setup Deployment (Docker Method)

**Requirements:** Only Docker needs to be installed on the server

### Step 1: Clone Repository
```bash
git clone https://github.com/K-ARIVAZHAGAN/VEDIO_CAPTIONING-REPORT_GENERATOR.git
cd VEDIO_CAPTIONING-REPORT_GENERATOR
```

### Step 2: Download Models
```bash
git lfs pull
```

### Step 3: Start Application
```bash
docker-compose up -d
```

**That's it!** The application will:
- ✅ Automatically install ALL dependencies (ffmpeg, Python, libraries)
- ✅ Build the container (first time takes 15-20 minutes)
- ✅ Start the service on port 5000

### Access Application
```
http://localhost:5000
```
or
```
http://YOUR_SERVER_IP:5000
```

---

## 🔍 Check Status

```bash
# Check if container is running
docker-compose ps

# View logs
docker-compose logs -f

# Check health
curl http://localhost:5000/health
```

---

## 🛑 Stop/Restart

```bash
# Stop
docker-compose down

# Restart
docker-compose restart

# Update and restart
git pull
docker-compose up -d --build
```

---

## 📋 System Requirements

- **Docker & Docker Compose** (only requirement!)
- **8GB RAM** minimum
- **20GB disk space** for models and Docker image
- **Port 5000** must be available

---

## 🔧 Configuration

Edit `docker-compose.yml` to customize:
- **Port:** Change `5000:5000` to `8080:5000` for port 8080
- **Memory:** Adjust `memory: 8G` as needed

---

## ❓ Troubleshooting

**Port already in use:**
```bash
# Change port in docker-compose.yml
ports:
  - "8080:5000"  # Use port 8080 instead
```

**Container not starting:**
```bash
docker-compose logs
```

**Out of memory:**
```bash
# Increase Docker memory limit
# Windows/Mac: Docker Desktop → Settings → Resources
```

---

## 🎯 What Docker Does Automatically

- ✅ Installs Python 3.11
- ✅ Installs ffmpeg for video processing
- ✅ Installs ALL system libraries (libsm6, libxext6, etc.)
- ✅ Installs ALL Python packages (PyTorch, Whisper, etc.)
- ✅ Compiles llama-cpp-python with C++ compiler
- ✅ Sets up proper permissions
- ✅ Configures networking and ports
- ✅ Handles process management

**NO MANUAL INSTALLATION REQUIRED!**

---

## 📞 Support

For issues: Check logs with `docker-compose logs -f`

GitHub: https://github.com/K-ARIVAZHAGAN/VEDIO_CAPTIONING-REPORT_GENERATOR
