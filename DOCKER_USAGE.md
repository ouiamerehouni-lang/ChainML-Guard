# Docker Usage Guide - ChainML Guard Explanation Feature

## Overview

This guide explains how to use the explanation feature when running ChainML Guard in Docker containers.

---

## Quick Start (Docker)

### Step 1: Compute Thresholds in Docker

**Easiest Method - Use the Helper Script:**
```bash
cd /home/mahmoud/Desktop/ChainML-Guard
./docker_compute_thresholds.sh
```

This script will:
- Build the Docker image with all dependencies
- Run the threshold computation inside the container
- Save `thresholds.json` to your project directory
- Show success message with next steps

**Manual Method:**
```bash
cd /home/mahmoud/Desktop/ChainML-Guard

# Build the image
docker build -t chainml-guard .

# Run the threshold script
docker run --rm -v $(pwd):/app chainml-guard python scripts/compute_thresholds.py
```

### Step 2: Verify Thresholds Were Created

```bash
cat thresholds.json
```

You should see JSON with 5 keys: age_p10, tx_p90, bal_p05, bal_p95, rate_p90

### Step 3: Run the Flask App in Docker

```bash
docker run -p 5000:5000 -v $(pwd):/app chainml-guard
```

Then visit: http://localhost:5000

---

## Detailed Docker Commands

### Building the Image

```bash
cd /home/mahmoud/Desktop/ChainML-Guard
docker build -t chainml-guard .
```

**What this does:**
- Uses the Dockerfile in the project root
- Installs all Python dependencies from requirements.txt
- Creates an image named `chainml-guard`

**Troubleshooting:**
- If build fails, check that requirements.txt is present
- Ensure you have internet connection for pip downloads
- Check Docker has enough disk space: `docker system df`

---

### Running Scripts in Docker

#### Compute Thresholds

```bash
docker run --rm -v $(pwd):/app chainml-guard python scripts/compute_thresholds.py
```

**Explanation:**
- `--rm`: Remove container after execution
- `-v $(pwd):/app`: Mount current directory to /app in container
- `chainml-guard`: The image name
- `python scripts/compute_thresholds.py`: Command to run inside container

**Expected Output:**
```
Loading dataset_final.csv...
✓ Loaded 10000 records
✓ Split into train (8000) and test (2000) sets

Computing percentile thresholds from training data...

Computed thresholds:
  age_p10  (very new wallet):           45.20 days
  tx_p90   (high tx count):             156 transactions
  ...

✓ Thresholds saved to thresholds.json
```

#### Test the Feature

```bash
docker run --rm -v $(pwd):/app chainml-guard python test_explanation_feature.py
```

#### Run Any Python Script

```bash
docker run --rm -v $(pwd):/app chainml-guard python <your_script.py>
```

---

### Running the Flask App in Docker

#### Basic Run (Development)

```bash
docker run -p 5000:5000 -v $(pwd):/app chainml-guard
```

**Explanation:**
- `-p 5000:5000`: Map port 5000 from container to host
- `-v $(pwd):/app`: Mount current directory (for hot reload)
- Container will start Flask app automatically

**Access:**
- From local machine: http://localhost:5000
- From network: http://<your-ip>:5000

#### Run with Name (Easier Management)

```bash
docker run -d \
  --name chainml-guard-app \
  -p 5000:5000 \
  -v $(pwd):/app \
  chainml-guard
```

**Explanation:**
- `-d`: Run in detached mode (background)
- `--name chainml-guard-app`: Give container a name

**Check logs:**
```bash
docker logs chainml-guard-app
```

**Stop:**
```bash
docker stop chainml-guard-app
docker rm chainml-guard-app
```

#### Run in Interactive Mode (Debugging)

```bash
docker run -it \
  -p 5000:5000 \
  -v $(pwd):/app \
  chainml-guard \
  /bin/bash
```

**Inside the container:**
```bash
# Manually run scripts
python scripts/compute_thresholds.py
python test_explanation_feature.py
python app.py

# Check files
ls -la
cat thresholds.json

# Exit
exit
```

---

## Docker Compose (Optional)

If you prefer using docker-compose, I've created a `docker-compose.yml` file for you.

### Using docker-compose

**Compute Thresholds:**
```bash
docker-compose run --rm compute-thresholds
```

**Run the Flask App:**
```bash
docker-compose up
```

**Run in Background:**
```bash
docker-compose up -d
```

**View Logs:**
```bash
docker-compose logs -f
```

**Stop:**
```bash
docker-compose down
```

---

## Common Docker Scenarios

### Scenario 1: First Time Setup

```bash
# 1. Build the image
docker build -t chainml-guard .

# 2. Compute thresholds
./docker_compute_thresholds.sh
# OR manually:
docker run --rm -v $(pwd):/app chainml-guard python scripts/compute_thresholds.py

# 3. Verify thresholds
cat thresholds.json

# 4. Run the app
docker run -p 5000:5000 -v $(pwd):/app chainml-guard

# 5. Visit http://localhost:5000
```

### Scenario 2: Rebuild After Code Changes

```bash
# Rebuild the image
docker build -t chainml-guard .

# Restart the app
docker run -p 5000:5000 -v $(pwd):/app chainml-guard
```

### Scenario 3: Update Thresholds After Retraining Model

```bash
# Retrain model (if needed)
docker run --rm -v $(pwd):/app chainml-guard python train_model.py

# Recompute thresholds
docker run --rm -v $(pwd):/app chainml-guard python scripts/compute_thresholds.py

# Restart Flask app to reload thresholds
docker restart chainml-guard-app
```

### Scenario 4: Debugging Issues

```bash
# Run in interactive mode
docker run -it --rm -v $(pwd):/app chainml-guard /bin/bash

# Inside container, check files
ls -la data/
ls -la models/
ls -la thresholds.json

# Test components individually
python -c "from utils.explanations import load_thresholds; print(load_thresholds())"
python scripts/compute_thresholds.py
python test_explanation_feature.py

# Exit
exit
```

---

## Troubleshooting Docker Issues

### Issue: "Cannot connect to Docker daemon"

**Solution:**
```bash
# Check if Docker is running
docker info

# Start Docker service (Linux)
sudo systemctl start docker

# Or start Docker Desktop (Mac/Windows)
```

### Issue: "Permission denied" when running docker commands

**Solution:**
```bash
# Add your user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker run ...
```

### Issue: "Port 5000 already in use"

**Solution:**
```bash
# Check what's using port 5000
lsof -i :5000

# Kill the process or use a different port
docker run -p 5001:5000 -v $(pwd):/app chainml-guard
```

### Issue: "thresholds.json not created" after running script

**Solution:**
```bash
# Check volume mount is working
docker run --rm -v $(pwd):/app chainml-guard ls -la /app

# Make sure you're in the correct directory
pwd  # Should be /home/mahmoud/Desktop/ChainML-Guard

# Run with explicit path
docker run --rm -v /home/mahmoud/Desktop/ChainML-Guard:/app chainml-guard python scripts/compute_thresholds.py
```

### Issue: "dataset_final.csv not found"

**Solution:**
```bash
# Check if file exists locally
ls -la data/dataset_final.csv

# If missing, you need to generate it first
docker run --rm -v $(pwd):/app chainml-guard python data_collection.py
```

### Issue: "Model files not found"

**Solution:**
```bash
# Check if model files exist
ls -la models/fraud_model.h5
ls -la models/scaler.pkl

# If missing, train the model first
docker run --rm -v $(pwd):/app chainml-guard python train_model.py
```

### Issue: Image build fails

**Solution:**
```bash
# Clean up Docker cache
docker system prune -a

# Rebuild from scratch
docker build --no-cache -t chainml-guard .

# Check Dockerfile syntax
cat Dockerfile
```

---

## Docker Best Practices

### 1. Use Volume Mounts for Development

```bash
# Always mount current directory for development
docker run -v $(pwd):/app ...
```

This allows:
- Changes to code reflect immediately
- Generated files (thresholds.json) saved locally
- No need to rebuild image for code changes

### 2. Name Your Containers

```bash
# Use --name for easier management
docker run --name chainml-guard-app -d ...

# Then you can easily:
docker logs chainml-guard-app
docker stop chainml-guard-app
docker start chainml-guard-app
```

### 3. Clean Up After Yourself

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove everything unused
docker system prune -a
```

### 4. Check Container Status

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Check logs
docker logs <container-name>

# Follow logs in real-time
docker logs -f <container-name>
```

---

## Production Deployment with Docker

### Using Docker in Production

For production deployment, consider:

1. **Build optimized image:**
   ```bash
   docker build -t chainml-guard:production .
   ```

2. **Use environment variables:**
   ```bash
   docker run -e FLASK_ENV=production \
     -e FLASK_DEBUG=0 \
     -p 5000:5000 \
     chainml-guard:production
   ```

3. **Use gunicorn instead of Flask dev server:**
   Update Dockerfile CMD:
   ```dockerfile
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

4. **Set up health checks:**
   ```bash
   docker run --health-cmd="curl -f http://localhost:5000/ || exit 1" \
     --health-interval=30s \
     --health-timeout=10s \
     --health-retries=3 \
     chainml-guard:production
   ```

5. **Use Docker networks:**
   ```bash
   docker network create chainml-network
   docker run --network chainml-network chainml-guard
   ```

---

## Quick Reference

### Essential Commands

```bash
# Build
docker build -t chainml-guard .

# Compute thresholds (easiest)
./docker_compute_thresholds.sh

# Compute thresholds (manual)
docker run --rm -v $(pwd):/app chainml-guard python scripts/compute_thresholds.py

# Run app (development)
docker run -p 5000:5000 -v $(pwd):/app chainml-guard

# Run app (detached)
docker run -d --name chainml-guard-app -p 5000:5000 -v $(pwd):/app chainml-guard

# Interactive shell
docker run -it --rm -v $(pwd):/app chainml-guard /bin/bash

# View logs
docker logs chainml-guard-app

# Stop
docker stop chainml-guard-app

# Remove
docker rm chainml-guard-app
```

---

## Summary

✅ **Use the helper script for easiest setup:**
```bash
./docker_compute_thresholds.sh
```

✅ **For manual control, use docker run:**
```bash
docker run --rm -v $(pwd):/app chainml-guard python scripts/compute_thresholds.py
```

✅ **Always mount volumes** to save generated files (thresholds.json)

✅ **All Python dependencies are in the Docker image** - no local installation needed

✅ **Run any Python script** using the same pattern:
```bash
docker run --rm -v $(pwd):/app chainml-guard python <your-script.py>
```

For more details, see:
- `SETUP_GUIDE.md` - General setup instructions
- `QUICK_REFERENCE.txt` - Quick commands
- `README_DOCS.md` - Documentation index
