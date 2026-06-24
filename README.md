# Mundialito UP 2026

Dashboard interactivo desarrollado con Streamlit para explorar el fixture, las
selecciones, los jugadores y las sedes del Mundial 2026.

## Funcionalidades

### Inicio

- Portada oficial y resumen general del torneo.
- Cantidad de selecciones, jugadores, partidos y sedes.
- Partidos por ciudad.
- Jugadores por confederacion en barras horizontales.
- Distribucion de posiciones en grafico pastel.
- Edad promedio por grupo en grafico de lineas, con grupos A-L, ejes y valores.
- Proximos partidos.
- Representacion del camino hacia la final.

### Partidos

- Filtro unico por grupo.
- Proximos partidos del grupo seleccionado.
- Previa de cada encuentro.
- Comparacion entre selecciones.
- Planteles, rendimiento reciente y datos del estadio.
- Listado completo de partidos por fecha.

### Paises

- Selector de las 48 selecciones.
- Informacion general de cada equipo.
- Edad, altura y cantidad de jugadores.
- Partidos programados.
- Plantel y clubes mas representados.

### Sedes

- Mapa interactivo de las sedes.
- Informacion del estadio, ciudad, pais y capacidad.
- Imagen de cada estadio disponible.
- Partidos programados por sede.

## Tecnologias

- Python
- Streamlit
- Pandas
- HTML y CSS
- OpenPyXL

## Estructura del proyecto

```text
MUNDIALITOUP/
|-- assets/
|   |-- branding/
|   |   |-- mundialito_hero.png
|   |   `-- trophy_final.png
|   `-- estadios/
|-- data/
|   |-- equipos.xlsx
|   |-- enfrentamientos.xlsx
|   |-- processed/
|   |   |-- equipos_procesado.csv
|   |   `-- enfrentamientos_procesado.csv
|   `-- mundial_2026/
|       |-- raw/
|       `-- processed/
|-- docs/
|-- scripts/
|   `-- scraping/
|       |-- scraper_equipos_jugadores_sedes.py
|       `-- scraper_fixture.py
|-- src/
|   |-- app.py
|   |-- api_or_scraper.py
|   |-- data_service.py
|   |-- db.py
|   |-- mundial_processing.py
|   |-- processing.py
|   |-- styles.py
|   |-- ui_components.py
|   `-- viz.py
|-- requirements.txt
`-- README.md
```

## Modulos principales

- `src/app.py`: punto de entrada de la aplicacion Streamlit y navegacion principal.
- `src/data_service.py`: consultas, filtros y funciones para obtener informacion del torneo.
- `src/mundial_processing.py`: procesamiento de archivos fuente del Mundial 2026.
- `src/processing.py`: procesamiento de datos complementarios del proyecto.
- `src/ui_components.py`: componentes visuales reutilizables como tarjetas, banderas y previas.
- `src/viz.py`: graficos, bracket del torneo y mapa interactivo de sedes.
- `src/styles.py`: estilos globales del dashboard.
- `src/db.py`: utilidades relacionadas con almacenamiento o acceso a datos.
- `src/api_or_scraper.py`: registro de la etapa de scraping y archivos generados.
- `scripts/scraping/scraper_equipos_jugadores_sedes.py`: obtiene selecciones, jugadores y sedes desde fuentes FIFA/On Location.
- `scripts/scraping/scraper_fixture.py`: obtiene el fixture del Mundial 2026 y convierte horarios a zona Peru.

## Datos

### Obtencion inicial por scraping

La obtencion de datos externos se realizo antes del procesamiento principal:

- `scraper_equipos_jugadores_sedes.py` descarga el PDF oficial de planteles FIFA, extrae equipos y jugadores con `pdfplumber`, y obtiene sedes desde la pagina FIFA/On Location con `requests` y `BeautifulSoup`.
- `scraper_fixture.py` extrae el calendario desde FIFA World Cup 2026 Hospitality / On Location, identifica partidos, fases, grupos, sedes y horarios, y convierte la hora local de cada sede a hora de Peru.

Los scripts generan CSV crudos. La aplicacion no depende del scraping en vivo para abrir el dashboard; primero guarda datos fuente en `data/mundial_2026/raw/` y luego `src/mundial_processing.py` los limpia y transforma.

### Archivos fuente

Ubicados en `data/mundial_2026/raw/`:

- `mundial_2026_equipos.csv`
- `mundial_2026_fixture.csv`
- `mundial_2026_jugadores.csv`
- `mundial_2026_sedes.csv`

Tambien se incluyen archivos complementarios en `data/`:

- `equipos.xlsx`
- `enfrentamientos.xlsx`

### Archivos procesados

Ubicados en `data/mundial_2026/processed/`:

- `dim_selecciones.csv`
- `dim_sedes.csv`
- `fact_fixture.csv`
- `fact_jugadores.csv`
- `dataset_dashboard.csv`

Ubicados en `data/processed/`:

- `equipos_procesado.csv`
- `enfrentamientos_procesado.csv`

## Instalacion

Crear el entorno virtual:

```powershell
python -m venv venv
```

Activarlo en Windows:

```powershell
venv\Scripts\activate
```

Instalar las dependencias:

```powershell
pip install -r requirements.txt
```

## Ejecucion

Procesar nuevamente los datos, cuando sea necesario:

```powershell
python src\mundial_processing.py
```

Iniciar el dashboard:

```powershell
streamlit run src/app.py
```

La aplicacion estara disponible normalmente en:

```text
http://localhost:8501
```

## Division sugerida para cinco integrantes

1. Procesamiento, limpieza y validacion de datos.
2. Portada, resumen general y recursos visuales.
3. Graficos y panel de indicadores.
4. Fixture, filtros y previa de partidos.
5. Perfiles de paises, sedes, documentacion y pruebas.

Cada integrante debe trabajar en una rama propia y crear un commit con cambios
relacionados exclusivamente con su responsabilidad.

## Fuentes de referencia

- FIFA Squad Lists: planteles y selecciones.
- FIFA World Cup 2026 Hospitality / On Location: fixture y sedes.
- FIFA Scores and Fixtures: verificacion del calendario.

## Estado

El dashboard cuenta con navegacion entre Inicio, Partidos, Paises y Sedes,
visualizaciones adaptadas a la tematica deportiva y datos procesados del Mundial
2026.
