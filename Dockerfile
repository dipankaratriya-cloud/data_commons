# Dockerfile for License Finder Streamlit App
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY license_finder_app.py .
COPY src/ ./src/

# Expose Streamlit port (Cloud Run expects 8080)
EXPOSE 8080

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the app
CMD ["streamlit", "run", "license_finder_app.py", "--server.port=8080", "--server.address=0.0.0.0"]
