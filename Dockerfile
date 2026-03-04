# ============================================
# Stage 1: Build Frontend
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files first (better caching)
COPY frontend/package*.json ./

# Install dependencies (include optional for rollup)
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build production bundle
RUN npm run build

# ============================================
# Stage 2: Python Backend + Serve Frontend
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if needed for psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY app.py .

# Copy scripts for data loading jobs
COPY scripts/ ./scripts/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy minimal data needed for runtime (if any)
# Note: In production, course data should be in Cloud SQL, not copied
COPY data/ ./data/

# Create logs directory with proper permissions
RUN mkdir -p /tmp/logs && chmod 777 /tmp/logs

# Cloud Run will inject PORT environment variable (default 8080)
ENV PORT=8080
ENV FLASK_ENV=production

# Expose the port (documentation only)
EXPOSE 8080

# Health check (optional but recommended)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=2)" || exit 1

# Use gunicorn for production with dynamic port binding
CMD exec gunicorn --bind :$PORT --workers 4 --threads 2 --timeout 0 app:app