# Use a single, simple stage
FROM python:3.10-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy requirements first for caching
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire 'app' directory into the working directory
COPY ./app ./app

# Expose the port
EXPOSE 8000

# This command runs uvicorn correctly, telling it where to find the 'app' module
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
