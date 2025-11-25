# SIMOVILAB
# Proyecto: Screens Server

Gonzalo Gutiérrez Mata

B53279

## Para Contruir y correr el contenedor

```
docker compose up --build
```

## Modos

Admin: http://127.0.0.1:8000/admin/

Home: http://127.0.0.1:8000/

## Pantallas:

Onboard: /api/screens/<UUID_ONBOARD>/

Stop: /api/screens/<UUID_STOP>/

## Para correr comandos dentro del contenedor web:

```
docker-compose exec web uv run python manage.py migrate
docker-compose exec web uv run python manage.py createsuperuser
docker-compose exec web uv run python manage.py generate_demo_messages --device-id <UUID>
```