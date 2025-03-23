# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# ✅ Ensure `requests` is installed
RUN pip install requests  # ✅ Moved BEFORE CMD

# Command to run when container starts
CMD ["python", "main.py"]
