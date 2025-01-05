# Use official Python image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy only the current service (context is already correct)
COPY . /app

# Copy the shared `utils/` directory
COPY ../utils /app/utils

# Set PYTHONPATH so the app can access `utils`
ENV PYTHONPATH="/app:/app/utils"

# Install dependencies
RUN pip install --no-cache-dir -r /app/services/auth/requirements.txt

# Run the service
CMD ["python", "/app/services/auth/app.py"]
