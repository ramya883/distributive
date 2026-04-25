# Multi-stage build for optimized image size
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required for building Python packages and MongoDB connectivity
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy packages.txt for Streamlit system packages
COPY packages.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    $(cat packages.txt) \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY app.py .
COPY .streamlit .streamlit/

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/health || exit 1

# Expose Streamlit port
EXPOSE 8501

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV MONGO_URI=mongodb://localhost:27017
ENV MONGO_DB_NAME=distributive_db

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--logger.level=info"]
