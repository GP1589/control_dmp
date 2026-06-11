# Usa una imagen base slim para optimizar el peso
FROM python:3.12-slim

# Instala uv copiando los binarios desde la imagen oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Configuraciones para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Capa de dependencias: se copia primero para aprovechar el caché de Docker
COPY pyproject.toml uv.lock README.md ./

# Instalar dependencias con uv de forma ultrarrápida, usando el lockfile y sin dev deps
RUN uv sync --frozen --no-dev

# Copiar el código de la app
COPY app/ ./app/

# Exponer el puerto
EXPOSE 8000

# Comando para correr la aplicación usando el entorno gestionado por uv
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
