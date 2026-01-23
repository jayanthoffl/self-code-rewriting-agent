FROM python:3.10-slim

WORKDIR /app

# Install Git (Required for cloning)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Libs
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy App
COPY . .

# Start Server
# Run without reload to prevent crashing during cloning
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]