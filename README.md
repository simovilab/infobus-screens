# SIMOVILAB
# Proyecto: Screens Server

Gonzalo Gutiérrez Mata

B53279

## Para Contruir y correr el contenedor

```
docker build -t simovilab-screens .
```

## Correr el contenedor

```
docker run --rm -p 8000:8000 simovilab-screens
```

## Modos

Admin: http://127.0.0.1:8000/admin/

Home: http://127.0.0.1:8000/

## Pantallas:

Onboard: /api/screens/<UUID_ONBOARD>/

Stop: /api/screens/<UUID_STOP>/

## Configuración adicional para Redis

```
docker compose up --build
```