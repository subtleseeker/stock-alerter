FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set timezone
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create .env file if it doesn't exist
RUN touch .env

# Run the application
CMD ["python", "-m", "src.main"]
