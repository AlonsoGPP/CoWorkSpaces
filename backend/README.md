# Backend - Sistema de Gestion de Reservas CoWork Spaces

## Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic (migraciones)
- JWT (PyJWT)

## Arquitectura

El backend sigue Clean Architecture con la estructura:

backend/src

- domain
- application
- infrastructure
- presentation

## Decisiones de arquitectura y trade-offs

- Se adopta Clean Architecture para separar reglas de negocio (domain) de detalles tecnicos (framework, ORM, DB).
- Los casos de uso en application orquestan la logica sin depender de FastAPI ni SQLAlchemy.
- Infrastructure implementa repositorios y unidad de trabajo para aislar persistencia.
- Presentation solo expone contratos HTTP y traduccion de errores.

Trade-offs asumidos:

- Mayor cantidad de clases/archivos para una prueba tecnica pequena.
- Curva inicial de desarrollo mas lenta por el desacople de capas.
- A cambio, se gana testabilidad, mantenibilidad y menor acoplamiento a framework/DB.

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

## Justificacion de la estrategia de concurrencia

- Se eligio una restriccion de base de datos (Exclusion Constraint) como autoridad final para evitar overbooking real bajo concurrencia.
- Esta decision evita depender de validaciones en memoria o checks previos no atomicos.
- Ante colision, la capa de infraestructura mapea el conflicto de DB a OverlappingReservationError y la API responde 409 Conflict con mensaje claro.

Trade-offs de esta estrategia:

- Depende de capacidades especificas de PostgreSQL (tstzrange, gist, extension btree_gist).
- Incrementa el acoplamiento al motor PostgreSQL frente a una estrategia portable entre motores.
- A cambio, garantiza consistencia fuerte incluso con peticiones simultaneas.

Referencia tecnica:

- Constraint: reservations_no_overlap en migracion inicial.
- Error de dominio: OverlappingReservationError.
- Respuesta HTTP: 409 con error_code reservation_overlap.

## Orden de aplicacion de las reglas de tarifas

El motor de tarifas aplica reglas en orden obligatorio y secuencial:

1. HORA_PICO: multiplicador 1.25.
2. FIN_DE_SEMANA: multiplicador 1.15.
3. RESERVA_LARGA (>= 240 minutos): descuento 10%.
4. ANTICIPACION (>= 168 horas): descuento 5%.

Notas:

- El orden importa porque las reglas se aplican de forma acumulada sobre el total intermedio.
- Este comportamiento es determinista y se valida en tests del pricing engine.

## Escenario de concurrencia (obligatorio)

Se incluye un test dedicado para demostrar el caso:

- Dos peticiones simultaneas intentan reservar el mismo espacio y horario.
- Solo una peticion debe confirmarse con 201.
- La otra peticion debe devolver 409 Conflict.
- Nunca se confirman ambas reservas al mismo tiempo.

Archivo del test:

tests/presentation/test_concurrency_scenario.py

Comando para ejecutarlo de forma aislada:

pytest tests/presentation/test_concurrency_scenario.py::test_concurrent_requests_return_201_and_409 -v

Que valida este test:

- Envia 2 requests en paralelo al endpoint POST /reservations.
- Verifica que el resultado ordenado sea exactamente [201, 409].
- El 409 corresponde al conflicto por solapamiento de reserva.

Pasos para probarlo localmente:

1. Activar entorno virtual:

    . .venv/bin/activate

2. Ejecutar migraciones:

    alembic upgrade head

3. Ejecutar el test de concurrencia:

    pytest tests/presentation/test_concurrency_scenario.py::test_concurrent_requests_return_201_and_409 -v

4. Confirmar evidencia en salida:

    - El test termina en PASSED.
    - No hay caso en el que ambas respuestas sean 201.

## Como ejecutar los tests

1. Activar entorno virtual:

    . .venv/bin/activate

2. Ejecutar toda la suite:

    pytest -q

3. Ejecutar solo concurrencia:

    pytest tests/presentation/test_concurrency_scenario.py::test_concurrent_requests_return_201_and_409 -v

4. Opcional, validar calidad de codigo:

    ruff check src tests
    black --check src tests
    isort --check-only src tests

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

## Autenticacion JWT

Se implemento autenticacion con JWT para proteger los endpoints de negocio.

Endpoint publico de autenticacion:

- POST /auth/login

Request:

```json
{
    "email": "admin@cowork.local",
    "password": "Admin123!"
}
```

Response:

```json
{
    "access_token": "<jwt>",
    "token_type": "bearer",
    "expires_in_seconds": 3600
}
```

Credenciales demo semilla (migracion 0002):

- email: admin@cowork.local
- password: Admin123!

Rutas protegidas:

- /spaces/**
- /reservations/**
- /availability/**
- /pricing/**
- /reports/**

Header requerido:

- Authorization: Bearer <access_token>

## Docker (backend + PostgreSQL)

Se agrego una configuracion Docker para ejecutar backend y base de datos con un solo comando.

Archivos involucrados:

- backend/Dockerfile
- backend/.dockerignore
- docker-compose.yml (en la raiz del repositorio)

Pasos:

1. Desde la raiz del repositorio, construir y levantar servicios:

    docker compose up --build

2. Verificar API:

    http://localhost:8000/health

3. Detener y limpiar volumen de base de datos (opcional):

    docker compose down -v

Notas:

- El servicio backend ejecuta alembic upgrade head al iniciar.
- DATABASE_URL dentro de Docker apunta al servicio db.
- Variables JWT configurables por entorno:
    - JWT_SECRET_KEY
    - JWT_ALGORITHM (default HS256)
    - JWT_ACCESS_TOKEN_TTL_SECONDS (default 3600)
    - JWT_ISSUER (default cowork-reservations)

## CI/CD con GitHub Actions

Se agregaron dos workflows:

- .github/workflows/backend-ci.yml
- .github/workflows/backend-cd.yml

Backend CI (pull_request y push):

- Configura Python 3.12.
- Levanta PostgreSQL como service container.
- Instala dependencias dev del backend.
- Ejecuta ruff, black --check, isort --check-only.
- Ejecuta alembic upgrade head.
- Ejecuta pytest -q.

Backend CD - Docker (push a main y workflow_dispatch):

- Construye imagen Docker desde backend/Dockerfile.
- Publica la imagen en GHCR con tags latest (main) y sha.

Permisos requeridos:

- El workflow de CD usa GITHUB_TOKEN con packages: write para publicar en GHCR.

## Estado actual

- Domain: entidades, value objects, servicios de pricing y cancelacion,
  excepciones e interfaces de repositorio.
- Application: DTOs, interfaces y casos de uso para espacios y reservas.
- Infrastructure: modelos SQLAlchemy, repositorios, unidad de trabajo,
  sesion de base de datos y migracion inicial con exclusion constraint.
- Presentation: routers FastAPI, schemas y manejo centralizado de errores.
