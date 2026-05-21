FROM python:3.14.3-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container.
WORKDIR /app

# Install dependencies first, in a separate layer.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code.
COPY src/ ./src/

# Expose the TCP port the platform listens on.
EXPOSE 9000

# Run the platform.
ENTRYPOINT ["python", "-m", "src.main"]