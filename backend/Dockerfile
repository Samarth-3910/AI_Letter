# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirement file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (Cloud Run defaults to 8080)
ENV PORT=8080
EXPOSE 8080

# Run the command to start uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
