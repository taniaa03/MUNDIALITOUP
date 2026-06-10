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

## Estructura

```text
MUNDIALITOUP2/
|-- assets/
|   |-- branding/
|   |   |-- mundialito_hero.png
|   |   `-- trophy_final.png
|   `-- estadios/
|-- data/
|   `-- mundial_2026/
|       |-- raw/
|       `-- processed/
|-- docs/
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

## Datos

### Archivos fuente

Ubicados en `data/mundial_2026/raw/`:

- `mundial_2026_equipos.csv`
- `mundial_2026_fixture.csv`
- `mundial_2026_jugadores.csv`
- `mundial_2026_sedes.csv`

### Archivos procesados

Ubicados en `data/mundial_2026/processed/`:

- `dim_selecciones.csv`
- `dim_sedes.csv`
- `fact_fixture.csv`
- `fact_jugadores.csv`
- `dataset_dashboard.csv`

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
