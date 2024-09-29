#FLEX
# Use the official Python image from the Docker Hub
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV API_ID=${API_ID}
ENV API_HASH=${API_HASH}
ENV BOT_TOKEN=${BOT_TOKEN}

# Command to run the application
CMD ["python", "app.py"]