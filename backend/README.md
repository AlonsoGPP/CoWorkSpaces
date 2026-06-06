# Backend - Sistema de Gestion de Reservas CoWork Spaces

## Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic (migraciones)

## Arquitectura

El backend sigue Clean Architecture con la estructura:

backend/src

- domain
- application
- infrastructure
- presentation

## Reglas de negocio clave

- No permitir reservas solapadas.
- Duracion minima: 30 minutos.
- Duracion maxima: 8 horas.
- Espacios en mantenimiento no aceptan reservas.
- Motor de tarifas desacoplado de FastAPI/SQLAlchemy/PostgreSQL.
- Politica de cancelacion desacoplada de infraestructura.

## Garantia de concurrencia

La garantia final de no solapamiento se implementa en PostgreSQL mediante
Exclusion Constraint sobre el rango temporal de reserva.

## Comandos de desarrollo

Instalar dependencias:

pip install -e .[dev]

Ejecutar migraciones:

alembic upgrade head

Levantar API:

uvicorn main:app --app-dir src --reload

Ejecutar tests:

pytest -q

Formato y lint:

black src tests
isort src tests
ruff check src tests

## Estado actual

- Domain: entidades, value objects, servicios de pricing y cancelacion,
  excepciones e interfaces de repositorio.
- Application: DTOs, interfaces y casos de uso para espacios y reservas.
- Infrastructure: modelos SQLAlchemy, repositorios, unidad de trabajo,
  sesion de base de datos y migracion inicial con exclusion constraint.
- Presentation: routers FastAPI, schemas y manejo centralizado de errores.
