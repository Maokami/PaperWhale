# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install uv, a fast Python package installer
RUN pip install uv

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install dependencies using uv
RUN uv pip install --no-cache --system -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . .

# Command to run the application using socket mode
CMD ["python", "run_socket_mode.py"]
