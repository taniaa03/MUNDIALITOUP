# Mundialito UP

Dashboard en Streamlit para analizar datos del Mundial 2026 y datos historicos de rendimiento/enfrentamientos.

## Estructura principal

```text
data/
+-- equipos.xlsx
+-- enfrentamientos.xlsx
+-- processed/
|   +-- equipos_procesado.csv
|   +-- enfrentamientos_procesado.csv
+-- mundial_2026/
|   +-- raw/
|   +-- processed/
docs/
+-- rubrica_proyecto.md
+-- parcial.docx
src/
+-- app.py
+-- processing.py
+-- mundial_processing.py
+-- viz.py
```

## Division de trabajo

- Los archivos `data/equipos.xlsx`, `data/enfrentamientos.xlsx` y sus CSV procesados corresponden a la parte del companero.
- La carpeta `data/mundial_2026/` corresponde al bloque Mundial 2026.
- El dashboard mantiene ambas partes separadas para evitar modificar datos que no pertenecen a la primera parte.

## Datos del bloque Mundial 2026

Archivos fuente en `data/mundial_2026/raw/`:

- `mundial_2026_equipos.csv`
- `mundial_2026_fixture.csv`
- `mundial_2026_jugadores.csv`
- `mundial_2026_sedes.csv`

Tablas procesadas en `data/mundial_2026/processed/`:

- `dim_selecciones.csv`
- `dim_sedes.csv`
- `fact_fixture.csv`
- `fact_jugadores.csv`
- `dataset_dashboard.csv`

## Fuentes usadas

- FIFA Squad Lists PDF: planteles y selecciones.
- FIFA World Cup 2026 Hospitality / On Location: fixture y sedes disponibles.
- FIFA scores and fixtures: referencia de verificacion del fixture.

## Ejecutar localmente

Crear y activar entorno virtual:

```powershell
python -m venv venv
venv\Scripts\activate
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Procesar el bloque Mundial 2026:

```powershell
python src\mundial_processing.py
```

Ejecutar dashboard:

```powershell
streamlit run src/app.py
```

## Entrega parcial

El prototipo incluye:

- Carga de CSV.
- Limpieza de datos y normalizacion.
- Tabla integrada para dashboard.
- Metricas descriptivas.
- Graficos de barras.
- Controles por seleccion, grupo, sede, posicion y club.
