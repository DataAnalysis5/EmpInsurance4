# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install waitress

# Expose the port Waitress will run on
EXPOSE 8000

# Start the app using Waitress
CMD ["waitress-serve", "--port=8000", "--call", "app:create_app"]
