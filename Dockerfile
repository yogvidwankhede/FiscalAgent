# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Expose the port Render expects
EXPOSE 10000

# Command to run the app
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:10000"]
