"""
Registro de la etapa de obtencion de datos externos.

En esta entrega, el dashboard no ejecuta scraping en vivo cada vez que abre.
Primero se usaron scripts de scraping/extraccion para generar archivos CSV
crudos y luego la aplicacion trabaja con esos CSV en data/mundial_2026/raw/.

Scripts incluidos en el proyecto:
- scripts/scraping/scraper_equipos_jugadores_sedes.py
- scripts/scraping/scraper_fixture.py
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SCRAPER_SCRIPTS = {
    "equipos_jugadores_sedes": PROJECT_ROOT
    / "scripts"
    / "scraping"
    / "scraper_equipos_jugadores_sedes.py",
    "fixture": PROJECT_ROOT / "scripts" / "scraping" / "scraper_fixture.py",
}

RAW_OUTPUTS = {
    "equipos": PROJECT_ROOT
    / "data"
    / "mundial_2026"
    / "raw"
    / "mundial_2026_equipos.csv",
    "jugadores": PROJECT_ROOT
    / "data"
    / "mundial_2026"
    / "raw"
    / "mundial_2026_jugadores.csv",
    "sedes": PROJECT_ROOT
    / "data"
    / "mundial_2026"
    / "raw"
    / "mundial_2026_sedes.csv",
    "fixture": PROJECT_ROOT
    / "data"
    / "mundial_2026"
    / "raw"
    / "mundial_2026_fixture.csv",
}


def describir_fuentes() -> list[dict[str, str]]:
    """Devuelve una descripcion corta de los datos obtenidos por scraping."""
    return [
        {
            "script": "scraper_equipos_jugadores_sedes.py",
            "tecnica": "requests, pdfplumber y BeautifulSoup",
            "fuente": "PDF oficial FIFA Squad Lists y pagina FIFA/On Location de sedes",
            "salidas": "mundial_2026_equipos.csv, mundial_2026_jugadores.csv, mundial_2026_sedes.csv",
        },
        {
            "script": "scraper_fixture.py",
            "tecnica": "requests, BeautifulSoup, expresiones regulares y conversion de zonas horarias",
            "fuente": "FIFA World Cup 2026 Hospitality / On Location",
            "salidas": "mundial_2026_fixture.csv",
        },
    ]


def archivos_raw_generados() -> dict[str, bool]:
    """Indica si los CSV generados por la etapa de scraping existen en el repo."""
    return {nombre: ruta.exists() for nombre, ruta in RAW_OUTPUTS.items()}


if __name__ == "__main__":
    print("Etapa de obtencion de datos externos")
    print("------------------------------------")
    for item in describir_fuentes():
        print(f"Script: {item['script']}")
        print(f"Tecnica: {item['tecnica']}")
        print(f"Fuente: {item['fuente']}")
        print(f"Salidas: {item['salidas']}")
        print()

    print("CSV raw disponibles:")
    for nombre, existe in archivos_raw_generados().items():
        estado = "OK" if existe else "FALTA"
        print(f"- {nombre}: {estado}")
