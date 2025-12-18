# Deployment Guide - Video Captioning & Report Generator

## ⚡ Quick Deployment with Python (Recommended)

### Prerequisites
- Python 3.11+ installed
- Git and Git LFS installed
- FFmpeg installed
- Minimum 8GB RAM

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/K-ARIVAZHAGAN/VEDIO_CAPTIONING-REPORT_GENERATOR.git
cd VEDIO_CAPTIONING-REPORT_GENERATOR

# 2. Download model file
git lfs pull

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run application
python app.py
```

**Access at:** `http://localhost:5000`

---

## 🐳 Alternative: Deployment with Docker

### Prerequisites
- Docker installed (version 20.10+)
- Docker Compose installed (version 1.29+)
- Minimum 8GB RAM, 4 CPU cores recommended
- 20GB+ free disk space

### Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/K-ARIVAZHAGAN/VEDIO_CAPTIONING-REPORT_GENERATOR.git
cd VEDIO_CAPTIONING-REPORT_GENERATOR
```

#### 2. Download the Model File
The Llama model is tracked with Git LFS. Download it:
```bash
git lfs pull
```

Or manually download to `models/` folder if Git LFS is not available.

#### 3. Configure Environment Variables
Create a `.env` file or edit `docker-compose.yml`:
```bash
SECRET_KEY=your-secure-secret-key-here
FLASK_ENV=production
```

#### 4. Build and Run
```bash
# Build the Docker image
docker-compose build

# Start the application
docker-compose up -d

# Check if it's running
docker-compose ps
```

#### 5. Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```

Or replace `localhost` with your server IP address.

### Management Commands

**View Logs:**
```bash
docker-compose logs -f
```

**Stop the Application:**
```bash
docker-compose down
```

**Restart the Application:**
```bash
docker-compose restart
```

**Update the Application:**
```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

**Remove Everything (including volumes):**
```bash
docker-compose down -v
```

---

## Production Deployment (Linux Server)

### For Ubuntu/Debian

#### 1. Install Docker
```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### 2. Install Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. Deploy Application
```bash
# Clone repository
git clone https://github.com/K-ARIVAZHAGAN/VEDIO_CAPTIONING-REPORT_GENERATOR.git
cd VEDIO_CAPTIONING-REPORT_GENERATOR

# Pull model file
git lfs pull

# Start application
sudo docker-compose up -d

# Check status
sudo docker-compose ps
```

### For CentOS/RHEL

#### 1. Install Docker
```bash
# Remove old versions
sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine

# Install dependencies
sudo yum install -y yum-utils

# Add Docker repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### 2. Install Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. Deploy Application
Same as Ubuntu steps above.

---

## Configuration

### Port Configuration
To change the default port (5000), edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Change 8080 to your desired port
```

### Resource Limits
Adjust CPU and memory limits in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # Adjust based on server
      memory: 8G     # Adjust based on server
```

### Environment Variables

Create `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
MAX_CONTENT_LENGTH=500000000
UPLOAD_FOLDER=static/uploads
```

---

## Firewall Configuration

### Ubuntu/Debian (UFW)
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

### CentOS/RHEL (firewalld)
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

---

## Monitoring & Troubleshooting

### Check Container Status
```bash
docker-compose ps
```

### View Real-time Logs
```bash
docker-compose logs -f
```

### Check Resource Usage
```bash
docker stats
```

### Access Container Shell
```bash
docker-compose exec video-captioning bash
```

### Common Issues

**Issue: Port already in use**
```bash
# Find process using port 5000
sudo lsof -i :5000
# Kill the process or change port in docker-compose.yml
```

**Issue: Out of memory**
```bash
# Increase memory limits in docker-compose.yml
# Or upgrade server RAM
```

**Issue: Model file not found**
```bash
# Pull model with Git LFS
git lfs pull
# Or manually download to models/ folder
```

---

## Backup & Restore

### Backup Important Data
```bash
# Backup outputs and uploads
tar -czf backup.tar.gz outputs/ static/uploads/
```

### Restore Data
```bash
# Extract backup
tar -xzf backup.tar.gz
```

---

## Security Best Practices

1. **Change default SECRET_KEY** in `.env`
2. **Use HTTPS** with reverse proxy (nginx/Apache)
3. **Restrict file upload sizes** in config
4. **Regular updates**: `git pull && docker-compose up -d --build`
5. **Monitor logs** for suspicious activity
6. **Backup regularly** - outputs and configurations

---

## Support

For issues or questions:
- GitHub Repository: https://github.com/K-ARIVAZHAGAN/VEDIO_CAPTIONING-REPORT_GENERATOR
- Create an issue on GitHub

---

## License

See LICENSE file in the repository.
