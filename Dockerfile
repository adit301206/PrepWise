# Use a lightweight Python image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file from the backend folder
# We use 'backend/requirements.txt' because that's where your file lives
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from your local directory into the container
COPY . .

# Move into the backend directory where app.py lives
WORKDIR /app/backend

# Render uses the PORT environment variable
# We point gunicorn to 'app:app' because your file is app.py
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT app:app"]