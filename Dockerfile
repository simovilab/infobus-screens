# Etapa única (suficiente para el curso)
FROM python:3.12-slim

# Evitar prompts interactivos
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # uv usará este entorno virtual dentro del proyecto
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    DJANGO_SETTINGS_MODULE=config.settings

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema mínimas
# (curl solo por si luego quieres debuggear desde adentro, opcional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Copiar archivos de definición del proyecto para que uv pueda resolver deps
# (ajusta si tu pyproject o lock se llaman distinto)
COPY pyproject.toml uv.lock ./ 

# Instalar uv y dependencias del proyecto (solo producción, sin dev)
RUN pip install --no-cache-dir uv \
  && uv sync --frozen --no-dev

# Copiar el resto del código del proyecto
COPY . .

# Exponer puerto interno de daphne
EXPOSE 8000

# Comando de arranque:
# - usamos uv run para ejecutar dentro del entorno gestionado por uv (.venv)
# - daphne sirve HTTP + WebSocket, y asgi.py ya envuelve estáticos
CMD ["uv", "run", "daphne", "config.asgi:application", "--port", "8000", "--bind", "0.0.0.0"]
