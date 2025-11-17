# Use an official Node.js runtime to build the frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend ./
RUN npm run build

# Use an official Python runtime as the main image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY app.py .
# Copy helper modules from repo root
COPY log_writer.py .
COPY backend ./backend
COPY agreements_25-26 ./agreements_25-26

# Copy the built frontend code from the builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]