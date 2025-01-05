# Use an official Python image as the base
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy all services and utils into the container
COPY ./services /app/services
COPY ./services/utils /app/utils

# Set PYTHONPATH so services can import from utils
ENV PYTHONPATH="/app:/app/services:/app/utils"

# Install dependencies for all services
RUN pip install --no-cache-dir -r /app/services/auth/requirements.txt \
    && pip install --no-cache-dir -r /app/services/cart/requirements.txt \
    && pip install --no-cache-dir -r /app/services/categories/requirements.txt \
    && pip install --no-cache-dir -r /app/services/orders/requirements.txt \
    && pip install --no-cache-dir -r /app/services/pets/requirements.txt \
    && pip install --no-cache-dir -r /app/services/products/requirements.txt \
    && pip install --no-cache-dir -r /app/services/reviews/requirements.txt \
    && pip install --no-cache-dir -r /app/services/search/requirements.txt \
    && pip install --no-cache-dir -r /app/services/api-gateway/requirements.txt

# Expose a port for the service (default 5000, but overridden at runtime)
EXPOSE 5000

# Run the service dynamically based on the SERVICE_NAME environment variable
CMD ["sh", "-c", "python /app/services/${SERVICE_NAME}/app.py"]
