FROM python:3.11-slim

WORKDIR /app

# System dependencies install karein
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies copy aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Poora application code copy karein
COPY . .

# Port expose karein (Render ise automatic override kar leta hai)
EXPOSE 8000

# FastAPI Server start karne ki command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
