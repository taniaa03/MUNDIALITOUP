# Rubrica del proyecto

Curso: Programacion Avanzada para la Ciencia de Datos  
Seccion: A-PRE-PRE2026_IPER-170107

## Nota operativa del equipo

Los archivos `.xlsx` y `.csv` que actualmente estan dentro de `data/` y `data/processed/` pertenecen a la parte del companero y no se deben modificar.

La primera parte del trabajo corresponde al bloque Mundial 2026 generado con:

- `C:/Users/braya/Music/scramer.py`
- `C:/Users/braya/Music/scramer2.py`
- `C:/Users/braya/Music/bloque_a_mundial_2026/`

Ese bloque contiene los archivos de equipos, fixture, jugadores y sedes del Mundial 2026.

## 1. Objetivo

Desarrollar una app en Streamlit para ciencia de datos que:

- En la entrega parcial cargue y procese archivos `.csv` y muestre un prototipo de dashboard.
- En la entrega final incorpore datos externos mediante API o scraping, persistencia en SQL y un dashboard interactivo completo.

## 2. Entregables y cronograma

### Entrega parcial: 40%

Enfoque:

- CSV.
- Procesamiento basico.
- Prototipo en Streamlit.

Entregables:

- Documento breve de maximo 4 paginas.
- Repositorio publico en GitHub.

### Entrega final: 60%

Enfoque:

- API o scraping.
- SQL.
- Dashboard completo.
- Manejo de errores.
- Decoradores.

Entregables:

- Documento tecnico de maximo 10 paginas.
- Repositorio publico en GitHub.
- App funcional.

## 3. Requerimientos minimos por etapa

### 3.1. Parcial

Debe incluir:

- Datos:
  - Carga de uno o mas `.csv`.
  - Cita de fuente y licencia si corresponde.
  - Breve descripcion de procedencia y variables clave.
- Procesamiento basico:
  - Limpieza de faltantes, tipos y duplicados.
  - Metricas descriptivas como promedios, conteos u otras.
- Prototipo Streamlit:
  - Visualizacion en tabla.
  - Al menos 1 grafico sencillo: barras, histograma, linea u otro.
  - Al menos 1 control: selector de columna, rango, categoria u otro.
- Referencias:
  - 1 o 2 apps, repos o articulos que el equipo busca imitar parcialmente.
  - Justificacion breve de 1 o 2 lineas.
- Repositorio GitHub publico:
  - Codigo.
  - `README.md` con pasos para ejecutar localmente.

Opcional:

- Pruebas unitarias de funciones de carga o procesamiento.
- Esquema inicial de carpetas para escalar a la entrega final.

Checklist parcial:

- Citar la fuente de los `.csv`.
- Implementar limpieza y metricas descriptivas.
- Mostrar tabla y 1 grafico en Streamlit.
- Incluir 1 control de usuario funcional.
- Agregar 1 o 2 referencias con breve justificacion.
- Tener repo publico con `README.md` e instrucciones locales.

### 3.2. Final

Debe incluir:

- Datos externos:
  - API con endpoints, autenticacion y rate limits si aplica.
  - O web scraping responsable.
- Persistencia:
  - SQLite o SQL equivalente.
  - Esquema con 2 o mas tablas relacionadas recomendado.
  - Consultas integradas.
- Procesamiento y analisis:
  - Transformaciones relevantes.
  - Opcional: modelo simple como regresion o clustering.
- Streamlit:
  - Dashboard completo.
  - Varias visualizaciones interactivas.
  - Navegacion clara.
  - Multiples controles que afecten consultas y graficos.
  - KPIs si aplica.
- Calidad de codigo:
  - Manejo de errores con `try/except`.
  - Al menos un decorador para logging, tiempos o debug.
  - Estructura modular con paquetes o modulos.
- Documento tecnico:
  - Flujo de datos: API/scraping -> SQL -> dashboard.
  - Diseno de base de datos.
  - Evidencias y capturas explicadas.
  - Limitaciones y mejoras.
- Repositorio GitHub publico:
  - Codigo final.
  - `README.md` con dependencias e instrucciones de despliegue local o Streamlit Cloud.

Opcional:

- Cache con `st.cache_data` e invalidacion controlada.
- Pruebas unitarias para funciones criticas.
- Linter o formateo con herramientas como `flake8`, `ruff` o `black`.

Checklist final:

- API o scraping funcional y documentado.
- SQL con esquema y consultas.
- Dashboard completo con multiples visualizaciones.
- Controles que cambian consultas y graficos.
- Manejo de errores y decoradores.
- Documento tecnico con flujo, base de datos, capturas y mejoras.
- Repo publico con instrucciones de instalacion y ejecucion.

## 4. Estructura sugerida del repositorio

```text
project-root/
+-- README.md
+-- requirements.txt
+-- data/
+-- src/
|   +-- app.py
|   +-- processing.py
|   +-- viz.py
|   +-- api_or_scraper.py
|   +-- db.py
+-- docs/
|   +-- parcial.pdf
|   +-- final.pdf
+-- tests/
```

Uso sugerido:

- `data/`: CSV del parcial y dumps o exports de la entrega final.
- `src/app.py`: entrada de Streamlit.
- `src/processing.py`: limpieza y transformaciones.
- `src/viz.py`: funciones de graficacion.
- `src/api_or_scraper.py`: API o scraping de la entrega final.
- `src/db.py`: conexion y consultas SQL de la entrega final.
- `tests/`: pruebas opcionales.

## 5. Reglas de citacion y uso de recursos

- Citar fuentes de datos y trabajos de inspiracion con URL y descripcion breve.
- Indicar licencias si aplica para datos, imagenes o logos.
- Si se usa IA para refactor, documentacion u otra parte, declarar:
  - herramienta,
  - version,
  - partes asistidas.

## 6. Rubricas de evaluacion

### 6.1. Entrega parcial: 40%

| Criterio | Excelente 100% | Aceptable 70% | Deficiente 40% |
|---|---|---|---|
| Obtencion de datos | `.csv` bien seleccionados y explicados | Archivos basicos con poca justificacion | Sin datos claros |
| Procesamiento basico | Limpieza y metricas correctas | Procesamiento minimo o superficial | Inexistente |
| Dashboard inicial | Tabla y al menos 1 grafico claro | Visualizacion muy simple | Sin visualizacion |
| Control de usuario | Control funcional y relevante | Control basico o poco util | Sin control |
| Referencias | Pertinentes y bien justificadas | Referencias poco claras | Ausentes |
| Repo GitHub | Publico, organizado y con `README.md` util | Publico pero poco documentado | Inexistente o privado |

### 6.2. Entrega final: 60%

| Criterio | Excelente 100% | Aceptable 70% | Deficiente 40% |
|---|---|---|---|
| Obtencion de datos | API/scraping estable y documentado | Flujo parcial o poco robusto | No funciona |
| Persistencia en SQL | Esquema y consultas correctas e integradas | Base minima o poco documentada | No existe |
| Procesamiento/analisis | Relevante y bien documentado | Basico o superficial | Inexistente |
| Dashboard Streamlit | Completo, interactivo y navegable | Funcional pero limitado | Fallido o incompleto |
| Controles de usuario | Varios y utiles | Uno o pocos | Ninguno |
| Errores/decoradores | `try/except` robusto y decoradores utiles | Implementacion parcial o superficial | Ausentes |
| Documento tecnico | Completo, claro y critico | Parcial o poco detallado | Escaso |
| Repo GitHub | Publico, limpio y bien documentado | Publico con fallos de documentacion | Desordenado o privado |

## 7. Formato de entrega en Blackboard

Para el parcial:

- Subir PDF de maximo 4 paginas.
- Incluir enlace al repo publico.
- Nombre sugerido: `Parcial_ProgAvanzada_GrupoX.pdf`.

Para el final:

- Subir PDF de maximo 10 paginas.
- Incluir enlace al repo publico.
- Incluir URL de la app si se despliega en Streamlit Cloud.
- Nombre sugerido: `Final_ProgAvanzada_GrupoX.pdf`.

La portada del PDF debe incluir:

- Curso.
- Seccion.
- Integrantes.
- Emails.
- Fecha.
- Nombre del proyecto.

## 8. Integridad academica

- El trabajo debe ser original del equipo.
- Todo recurso externo debe citarse.
- No se permite copiar codigo sin referencia.
- El uso de IA esta permitido solo si se declara que herramienta se uso, como se uso y por que.
- El equipo sigue siendo responsable del codigo entregado.
