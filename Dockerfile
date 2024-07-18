FROM python:3.10-slim

# Dependencia do PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
    
WORKDIR /app

# Requisitos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Codigo
COPY . .
EXPOSE 8000

# Incializa o servidor Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "weather_api.wsgi:application"]
