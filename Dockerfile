# Use Python 3.11 for better compatibility with TensorFlow and Scikit-Learn
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system tools needed for building certain Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt-get/lists/*

# Copy only requirements first to optimize Docker layer caching
COPY requirements.txt .

# Install dependencies without saving cache to keep the image light
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Inform Docker that the container listens on port 5000
EXPOSE 5000

# Set environment variable to ensure Flask logs are visible in real-time
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
