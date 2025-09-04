#!/bin/sh

set -e

echo "Host de la base de datos: $POSTGRES_HOST"
echo "Puerto de la base de datos: $POSTGRES_PORT"
echo "Usuario de la base de datos: $POSTGRES_USER"

echo "Esperando a que la base de datos esté disponible..."

# Bucle que espera hasta que la base de datos acepte conexiones
# Se utiliza 'pg_isready', que es una herramienta para comprobar la disponibilidad de PostgreSQL
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -q; do
  sleep 0.1 # Espera 100 milisegundos entre intentos
done

echo "Base de datos disponible."

# --- Sección de Migraciones ---
# Una vez que la DB está disponible, aplica las migraciones de Alembic
echo "Aplicando migraciones de la base de datos..."
alembic upgrade head

# --- Ejecución del Comando Principal ---
# Finalmente, ejecuta el comando que se pasó al contenedor
# (en nuestro caso, será 'uvicorn app.main:app ...')
exec "$@"