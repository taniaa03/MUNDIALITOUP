# APIs utilizadas en Mundialito UP 2026

El proyecto integra dos APIs externas:

1. **TheSportsDB**, para obtener fotografías de jugadores.
2. **Bzzoiro Sports Data**, para actualizar partidos, marcadores, estadísticas e incidencias.

## Flujo general

```text
TheSportsDB ──> API.PY ──> fotos_jugadores.csv ──> SQLite / dashboard

Bzzoiro Sports Data ──> scripts/sync_bzzoiro.py ──> mundialito.db ──> dashboard
```

Las solicitudes se realizan con `requests`, incluyen tiempo máximo de espera y
usan `raise_for_status()` para detectar respuestas HTTP fallidas.

## API 1: TheSportsDB

### Objetivo

Buscar una fotografía para cada jugador del archivo
`data/mundial_2026/processed/fact_jugadores.csv`.

### Endpoint utilizado

```http
GET https://www.thesportsdb.com/api/v1/json/123/searchplayers.php
```

| Parámetro | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `p` | texto | Nombre del jugador | `Lionel Messi` |

Ejemplo:

```http
GET https://www.thesportsdb.com/api/v1/json/123/searchplayers.php?p=Lionel%20Messi
```

### Autenticación y límite

- Usa la clave pública gratuita `123` incluida en la URL del endpoint.
- El script espera **2.1 segundos entre solicitudes**, equivalente a un máximo
  aproximado de 30 solicitudes por minuto.
- Envía el encabezado `User-Agent: MundialitoUP/1.0 (proyecto educativo)`.

### Procesamiento

`API.PY`:

- genera variantes del nombre para mejorar la búsqueda;
- acepta únicamente resultados del deporte `Soccer`;
- compara nombre y fecha de nacimiento;
- prioriza `strCutout` y usa `strThumb` como respaldo;
- evita repetir jugadores que ya fueron consultados;
- guarda avances cada 25 jugadores.

Salida:

```text
data/mundial_2026/processed/fotos_jugadores.csv
```

Campos principales: `id_jugador`, `foto_url`, `thesportsdb_id`,
`nombre_api`, `estado_foto` y `error_api`.

### Ejecución

```powershell
# Una selección
venv\Scripts\python.exe API.PY --seleccion Argentina

# Todos los jugadores
venv\Scripts\python.exe API.PY --todos

# Volver a consultar registros guardados
venv\Scripts\python.exe API.PY --seleccion Argentina --reintentar
```

### Manejo de errores

Las excepciones de red, respuestas HTTP fallidas y JSON inválido se capturan.
El error se registra en `error_api` y el jugador queda con estado
`no_encontrada`, sin detener todo el proceso.

### Prueba funcional

Prueba realizada el **24 de junio de 2026**:

```text
HTTP: 200
consulta: Lionel Messi
resultados: 1
fotografía disponible: sí
```

## API 2: Bzzoiro Sports Data

### Objetivo

Sincronizar información del Mundial 2026 con SQLite:

- estado y minuto del partido;
- marcador y resultado al descanso;
- estadísticas por selección;
- incidencias;
- alineaciones recibidas;
- clima y asistencia, cuando estén disponibles.

### URL base y endpoints

URL base predeterminada:

```text
https://sports.bzzoiro.com/api/v2
```

| Método | Endpoint | Uso |
|---|---|---|
| `GET` | `/events/` | Fixture y partidos por liga, temporada, fechas y estado |
| `GET` | `/events/live/` | Partidos en vivo |
| `GET` | `/events/{id}/stats/` | Estadísticas del partido |
| `GET` | `/events/{id}/incidents/` | Goles, tarjetas y otras incidencias |
| `GET` | `/events/{id}/lineups/` | Alineaciones disponibles |

La consulta principal usa paginación mediante `limit` y `offset`.

Parámetros configurables:

| Variable | Valor predeterminado |
|---|---|
| `BZZOIRO_WORLD_CUP_LEAGUE_ID` | `27` |
| `BZZOIRO_WORLD_CUP_SEASON_ID` | `188` |
| `BZZOIRO_WORLD_CUP_DATE_FROM` | `2026-06-11` |
| `BZZOIRO_WORLD_CUP_DATE_TO` | `2026-07-19` |

### Autenticación

La API requiere un token privado:

```http
Authorization: Token TU_TOKEN
```

Crear un archivo `.env` en la raíz a partir de `.env.example`:

```powershell
Copy-Item .env.example .env
```

Luego reemplazar `TU_TOKEN_AQUI`. El archivo `.env` está excluido de Git y no
debe subirse al repositorio.

### Ejecución

```powershell
# Sincronización general
venv\Scripts\python.exe scripts\sync_bzzoiro.py

# Solo partidos en vivo
venv\Scripts\python.exe scripts\sync_bzzoiro.py --status inprogress

# Solicitar detalle también para partidos programados
venv\Scripts\python.exe scripts\sync_bzzoiro.py --detalle-programados
```

Estados aceptados: `notstarted`, `inprogress`, `finished`, `cancelled` y
`postponed`.

### Persistencia en SQLite

Base de datos:

```text
data/mundial_2026/mundialito.db
```

Tablas actualizadas:

- `partidos`;
- `estadisticas_partido`;
- `eventos_partido`;
- `bzzoiro_eventos`;
- `sincronizaciones_api`.

Se utilizan operaciones `UPSERT`, claves foráneas y claves únicas para evitar
duplicados. La tabla `sincronizaciones_api` conserva la fecha, el estado y los
conteos de cada ejecución.

### Manejo de errores y límites

- Cada solicitud tiene un tiempo máximo de 40 segundos.
- `raise_for_status()` convierte errores HTTP en excepciones.
- Si falla un endpoint de detalle, el partido principal puede guardarse sin
  estadísticas, incidencias o alineaciones.
- El token nunca se imprime ni se almacena en el código.
- El proveedor no tiene un límite fijo codificado en el proyecto. Si el plan
  contratado devuelve `HTTP 429`, debe esperarse el tiempo indicado por el
  proveedor antes de reintentar.

### Evidencia funcional local

Verificación realizada el **24 de junio de 2026** sobre la base incluida:

```text
partidos: 104
bzzoiro_eventos: 88
estadisticas_partido: 100
sincronizaciones_api: 173
última sincronización: completada
registros recibidos: 1
registros guardados: 1
partidos con métricas: 1
```

Esta evidencia confirma el flujo completo de Bzzoiro hacia SQLite. Para una
nueva sincronización desde otra computadora se necesita configurar nuevamente
`BZZOIRO_API_TOKEN`.

## Verificación rápida

```powershell
# Validar que ambos comandos están disponibles
venv\Scripts\python.exe API.PY --help
venv\Scripts\python.exe scripts\sync_bzzoiro.py --help

# Revisar la base SQLite desde el dashboard
streamlit run src\app.py
```
