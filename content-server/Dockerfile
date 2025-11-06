FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .
COPY pages/ ./pages/

# Expose port
EXPOSE 8181

# Run the server
CMD ["python", "server.py"]
