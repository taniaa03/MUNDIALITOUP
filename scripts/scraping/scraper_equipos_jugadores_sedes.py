import re
import json
import time
import logging
from pathlib import Path

import requests
import pandas as pd
import pdfplumber
from bs4 import BeautifulSoup
from unidecode import unidecode

# Silencia los avisos feos de pdfminer:
# "Could not get FontBBox..."
logging.getLogger("pdfminer").setLevel(logging.ERROR)


# ============================================================
# CONFIGURACIÓN
# ============================================================

OUT_DIR = Path("bloque_a_mundial_2026")
RAW_DIR = OUT_DIR / "raw"
OUT_DIR.mkdir(exist_ok=True)
RAW_DIR.mkdir(exist_ok=True)

FIFA_SQUAD_PDF = "https://fdp.fifa.org/assetspublic/ce281/pdf/SquadLists-English.pdf"
FIFA_VENUES = "https://fifaworldcup26.suites.fifa.com/venues/"

CSV_EQUIPOS = OUT_DIR / "mundial_2026_equipos.csv"
CSV_SEDES = OUT_DIR / "mundial_2026_sedes.csv"
CSV_JUGADORES = OUT_DIR / "mundial_2026_jugadores.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AnderProyectoMundial2026/2.0; +https://example.com)",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}


# ============================================================
# MAPAS DE APOYO
# IMPORTANTE:
# - Los equipos se extraen del PDF FIFA.
# - Estos mapas SOLO enriquecen grupo/confederación/debut.
# - Si FIFA cambia nombres, los alias corrigen IR Iran / USA.
# ============================================================

ALIASES_EQUIPO = {
    "ir iran": "Iran",
    "iran": "Iran",
    "usa": "United States",
    "united states": "United States",
    "u s a": "United States",
    "cote d ivoire": "Côte D'Ivoire",
    "côte d ivoire": "Côte D'Ivoire",
    "curacao": "Curaçao",
    "curaçao": "Curaçao",
    "turkiye": "Türkiye",
    "türkiye": "Türkiye",
    "cabo verde": "Cabo Verde",
    "congo dr": "Congo DR",
    "korea republic": "Korea Republic",
    "bosnia and herzegovina": "Bosnia And Herzegovina",
}

GRUPOS_2026 = {
    "A": ["Mexico", "South Africa", "Korea Republic", "Czechia"],
    "B": ["Canada", "Switzerland", "Qatar", "Bosnia And Herzegovina"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Türkiye"],
    "E": ["Germany", "Curaçao", "Côte D'Ivoire", "Ecuador"],
    "F": ["Netherlands", "Japan", "Tunisia", "Sweden"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cabo Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Norway", "Iraq"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "Uzbekistan", "Colombia", "Congo DR"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

CONFEDERACIONES = {
    "AFC": [
        "Australia", "Iran", "Iraq", "Japan", "Jordan", "Korea Republic",
        "Qatar", "Saudi Arabia", "Uzbekistan"
    ],
    "CAF": [
        "Algeria", "Cabo Verde", "Congo DR", "Côte D'Ivoire", "Egypt",
        "Ghana", "Morocco", "Senegal", "South Africa", "Tunisia"
    ],
    "CONCACAF": [
        "Canada", "Curaçao", "Haiti", "Mexico", "Panama", "United States"
    ],
    "CONMEBOL": [
        "Argentina", "Brazil", "Colombia", "Ecuador", "Paraguay", "Uruguay"
    ],
    "OFC": [
        "New Zealand"
    ],
    "UEFA": [
        "Austria", "Belgium", "Bosnia And Herzegovina", "Croatia", "Czechia",
        "England", "France", "Germany", "Netherlands", "Norway", "Portugal",
        "Scotland", "Spain", "Sweden", "Switzerland", "Türkiye"
    ],
}

DEBUT_MUNDIAL = {
    "Algeria": 1982,
    "Argentina": 1930,
    "Australia": 1974,
    "Austria": 1934,
    "Belgium": 1930,
    "Bosnia And Herzegovina": 2014,
    "Brazil": 1930,
    "Cabo Verde": 2026,
    "Canada": 1986,
    "Colombia": 1962,
    "Congo DR": 1974,
    "Côte D'Ivoire": 2006,
    "Croatia": 1998,
    "Curaçao": 2026,
    "Czechia": 2006,
    "Ecuador": 2002,
    "Egypt": 1934,
    "England": 1950,
    "France": 1930,
    "Germany": 1934,
    "Ghana": 2006,
    "Haiti": 1974,
    "Iran": 1978,
    "Iraq": 1986,
    "Japan": 1998,
    "Jordan": 2026,
    "Korea Republic": 1954,
    "Mexico": 1930,
    "Morocco": 1970,
    "Netherlands": 1934,
    "New Zealand": 1982,
    "Norway": 1938,
    "Panama": 2018,
    "Paraguay": 1930,
    "Portugal": 1966,
    "Qatar": 2022,
    "Saudi Arabia": 1994,
    "Scotland": 1954,
    "Senegal": 2002,
    "South Africa": 1998,
    "Spain": 1934,
    "Sweden": 1934,
    "Switzerland": 1934,
    "Tunisia": 1978,
    "Türkiye": 1954,
    "United States": 1930,
    "Uruguay": 1930,
    "Uzbekistan": 2026,
}

# FIFA usa nombres comerciales/neutrales para sedes.
# Esto sirve para dashboard, no para reemplazar la fuente FIFA.
ESTADIOS_REALES = {
    "Atlanta Stadium": "Mercedes-Benz Stadium",
    "Boston Stadium": "Gillette Stadium",
    "Dallas Stadium": "AT&T Stadium",
    "Houston Stadium": "NRG Stadium",
    "Kansas City Stadium": "Arrowhead Stadium",
    "Los Angeles Stadium": "SoFi Stadium",
    "Miami Stadium": "Hard Rock Stadium",
    "New York New Jersey Stadium": "MetLife Stadium",
    "Philadelphia Stadium": "Lincoln Financial Field",
    "San Francisco Bay Area Stadium": "Levi's Stadium",
    "Seattle Stadium": "Lumen Field",
    "Toronto Stadium": "BMO Field",
    "BC Place Vancouver": "BC Place",
    "Mexico City Stadium": "Estadio Azteca",
    "Guadalajara Stadium": "Estadio Akron",
    "Monterrey Stadium": "Estadio BBVA",
}

CAPACIDADES_APROX = {
    "Atlanta Stadium": 71000,
    "Boston Stadium": 65878,
    "Dallas Stadium": 80000,
    "Houston Stadium": 72220,
    "Kansas City Stadium": 76416,
    "Los Angeles Stadium": 70240,
    "Miami Stadium": 65326,
    "New York New Jersey Stadium": 82500,
    "Philadelphia Stadium": 67594,
    "San Francisco Bay Area Stadium": 68500,
    "Seattle Stadium": 68740,
    "Toronto Stadium": 45000,
    "BC Place Vancouver": 54500,
    "Mexico City Stadium": 72766,
    "Guadalajara Stadium": 48071,
    "Monterrey Stadium": 53500,
}


# ============================================================
# UTILIDADES
# ============================================================

def limpiar(txt):
    if txt is None:
        return ""
    return re.sub(r"\s+", " ", str(txt).replace("\xa0", " ")).strip()


def normalizar(txt):
    txt = limpiar(txt)
    txt = unidecode(txt).lower()
    txt = re.sub(r"[^a-z0-9]+", " ", txt)
    return re.sub(r"\s+", " ", txt).strip()


def canon_equipo(nombre):
    key = normalizar(nombre)
    return ALIASES_EQUIPO.get(key, limpiar(nombre))


def descargar(url, destino):
    print(f"Descargando: {url}")
    r = requests.get(url, headers=HEADERS, timeout=90)
    r.raise_for_status()
    destino.write_bytes(r.content)
    print(f"Guardado: {destino}")
    return destino


def crear_lookup_grupo():
    out = {}
    for grupo, equipos in GRUPOS_2026.items():
        for e in equipos:
            out[normalizar(e)] = grupo
    return out


def crear_lookup_conf():
    out = {}
    for conf, equipos in CONFEDERACIONES.items():
        for e in equipos:
            out[normalizar(e)] = conf
    return out


# ============================================================
# EQUIPOS DESDE PDF FIFA
# ============================================================

def extraer_equipos_pdf(pdf_path):
    filas = []

    # Ejemplo de línea del PDF:
    # Algeria (ALG)
    patron_linea = re.compile(r"^(.+?)\s+\(([A-Z]{3})\)$")

    # Fallback por si aparece pegado:
    # SQUAD LISTArgentina (ARG)
    patron_texto = re.compile(r"(?:SQUAD LIST\s*)?([A-Za-zÀ-ÿÇç'’.\-\s]+?)\s*\(([A-Z]{3})\)")

    with pdfplumber.open(pdf_path) as pdf:
        for pagina, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            lines = [limpiar(x) for x in text.splitlines() if limpiar(x)]

            seleccion = ""
            codigo = ""

            for line in lines[:12]:
                m = patron_linea.match(line)
                if m:
                    seleccion = limpiar(m.group(1))
                    codigo = limpiar(m.group(2))
                    break

            if not seleccion:
                m = patron_texto.search(text[:500])
                if m:
                    seleccion = limpiar(m.group(1))
                    codigo = limpiar(m.group(2))

            if not seleccion or not codigo:
                print(f"AVISO: no pude detectar selección en página {pagina}")
                continue

            filas.append({
                "seleccion_original_fifa": seleccion,
                "seleccion": canon_equipo(seleccion),
                "codigo_fifa": codigo,
                "pagina_pdf": pagina,
                "fuente_equipos": FIFA_SQUAD_PDF,
            })

    df = pd.DataFrame(filas).drop_duplicates(subset=["codigo_fifa"])
    df = df.sort_values("seleccion").reset_index(drop=True)
    df.insert(0, "id_equipo", range(1, len(df) + 1))
    return df


def enriquecer_equipos(df):
    lookup_grupo = crear_lookup_grupo()
    lookup_conf = crear_lookup_conf()
    lookup_debut = {normalizar(k): v for k, v in DEBUT_MUNDIAL.items()}

    df["pais"] = df["seleccion"]
    df["grupo"] = df["seleccion"].apply(lambda x: lookup_grupo.get(normalizar(x), ""))
    df["confederacion"] = df["seleccion"].apply(lambda x: lookup_conf.get(normalizar(x), ""))
    df["clasificado"] = "Sí"
    df["debut_mundial"] = df["seleccion"].apply(lambda x: lookup_debut.get(normalizar(x), ""))

    faltan_grupo = df.loc[df["grupo"] == "", "seleccion"].tolist()
    faltan_conf = df.loc[df["confederacion"] == "", "seleccion"].tolist()

    if faltan_grupo:
        print("AVISO: equipos sin grupo:", faltan_grupo)
    if faltan_conf:
        print("AVISO: equipos sin confederación:", faltan_conf)

    return df[
        [
            "id_equipo",
            "seleccion",
            "seleccion_original_fifa",
            "confederacion",
            "grupo",
            "codigo_fifa",
            "pais",
            "clasificado",
            "debut_mundial",
            "fuente_equipos",
        ]
    ]


# ============================================================
# JUGADORES DESDE PDF FIFA
# ============================================================

def extraer_jugadores_pdf(pdf_path):
    filas = []

    patron_equipo = re.compile(r"^(.+?)\s+\(([A-Z]{3})\)$")

    # Robusto:
    # Acepta:
    # GK MASTIL Melvin ... 19/02/2000 FC Stade Nyonnais (SUI) 194
    # 1 GK MASTIL Melvin ... 19/02/2000 FC Stade Nyonnais (SUI) 194
    patron_jugador = re.compile(
        r"^(?:\d+\s+)?(GK|DF|MF|FW)\s+(.+?)\s+(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(\d{2,3})$"
    )

    debug_fechas = []

    with pdfplumber.open(pdf_path) as pdf:
        for pagina, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            lines = [limpiar(x) for x in text.splitlines() if limpiar(x)]

            seleccion_original = ""
            codigo = ""

            for line in lines[:12]:
                m = patron_equipo.match(line)
                if m:
                    seleccion_original = limpiar(m.group(1))
                    codigo = limpiar(m.group(2))
                    break

            seleccion = canon_equipo(seleccion_original)

            for line in lines:
                if re.search(r"\d{2}/\d{2}/\d{4}", line):
                    debug_fechas.append(line)

                m = patron_jugador.match(line)
                if not m:
                    continue

                filas.append({
                    "seleccion": seleccion,
                    "seleccion_original_fifa": seleccion_original,
                    "codigo_fifa": codigo,
                    "posicion": m.group(1),
                    "bloque_nombre_fifa": limpiar(m.group(2)),
                    "fecha_nacimiento": m.group(3),
                    "club": limpiar(m.group(4)),
                    "altura_cm": int(m.group(5)),
                    "pagina_pdf": pagina,
                    "fila_original": line,
                    "fuente_jugadores": FIFA_SQUAD_PDF,
                })

    df = pd.DataFrame(filas)
    if not df.empty:
        df.insert(0, "id_jugador", range(1, len(df) + 1))
    else:
        # Si algo raro pasa, guarda líneas con fechas para diagnosticar rápido.
        debug_path = OUT_DIR / "debug_lineas_con_fechas_pdf.txt"
        debug_path.write_text("\n".join(debug_fechas[:300]), encoding="utf-8")
        print(f"AVISO: no salieron jugadores. Revisa muestra en: {debug_path}")

    return df


# ============================================================
# SEDES DESDE PÁGINA PRINCIPAL DE FIFA VENUES
# Esta versión NO entra a cada link interno.
# La home ya tiene las 16 sedes + ciudad + cantidad de partidos.
# ============================================================

def pais_largo(pais_txt):
    p = limpiar(pais_txt).replace(".", "")
    mapa = {
        "U.S": "United States",
        "US": "United States",
        "USA": "United States",
        "U.S.A": "United States",
        "Canada": "Canada",
        "Mexico": "Mexico",
    }
    return mapa.get(p, p)


def geocode_nominatim(query):
    """
    No es FIFA. Solo se usa para llenar latitud/longitud aproximada del dashboard.
    """
    if not query:
        return "", ""

    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            return "", ""
        return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        return "", ""


def extraer_sedes_desde_home(geocodificar=True):
    print(f"Scrapeando sedes desde: {FIFA_VENUES}")

    r = requests.get(FIFA_VENUES, headers=HEADERS, timeout=90)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")
    lines = [limpiar(x) for x in soup.get_text("\n").splitlines() if limpiar(x)]

    nombres_validos = set(ESTADIOS_REALES.keys())
    nombres_norm = {normalizar(x): x for x in nombres_validos}

    filas = []
    vistos = set()

    for i, line in enumerate(lines):
        nombre = nombres_norm.get(normalizar(line))
        if not nombre:
            continue

        if nombre in vistos:
            continue
        vistos.add(nombre)

        ciudad = ""
        pais = ""
        cantidad_partidos = ""

        # En la página principal la estructura es:
        # Nombre sede
        # Ciudad, País
        # 8 Matches
        ventana = lines[i:i + 8]

        for item in ventana[1:]:
            if "," in item and not ciudad:
                partes = [limpiar(p) for p in item.split(",")]
                ciudad = partes[0]
                pais = pais_largo(partes[-1])
                break

        for item in ventana[1:]:
            m = re.search(r"(\d+)\s+Matches", item, re.I)
            if m:
                cantidad_partidos = int(m.group(1))
                break

        estadio_real = ESTADIOS_REALES.get(nombre, nombre)
        capacidad = CAPACIDADES_APROX.get(nombre, "")

        lat, lon = "", ""
        if geocodificar:
            consulta_geo = f"{estadio_real}, {ciudad}, {pais}"
            lat, lon = geocode_nominatim(consulta_geo)
            time.sleep(1)

        filas.append({
            "ciudad": ciudad,
            "pais": pais,
            "estadio": estadio_real,
            "nombre_fifa_estadio": nombre,
            "capacidad_aprox": capacidad,
            "cantidad_partidos": cantidad_partidos,
            "latitud": lat,
            "longitud": lon,
            "fuente_sedes": FIFA_VENUES,
            "nota": "Sede, ciudad, país y cantidad de partidos extraídos de FIFA/On Location. Capacidad y coordenadas son aproximadas para dashboard.",
        })

    df = pd.DataFrame(filas)

    if not df.empty:
        orden = list(ESTADIOS_REALES.keys())
        df["orden"] = df["nombre_fifa_estadio"].apply(lambda x: orden.index(x) if x in orden else 999)
        df = df.sort_values("orden").drop(columns=["orden"]).reset_index(drop=True)
        df.insert(0, "id_sede", range(1, len(df) + 1))

    return df[
        [
            "id_sede",
            "ciudad",
            "pais",
            "estadio",
            "nombre_fifa_estadio",
            "capacidad_aprox",
            "cantidad_partidos",
            "latitud",
            "longitud",
            "fuente_sedes",
            "nota",
        ]
    ]


# ============================================================
# MAIN
# ============================================================

def main():
    print("=======================================")
    print("BLOQUE A - MUNDIAL 2026")
    print("SCRAPER EQUIPOS + SEDES V2 CORREGIDO")
    print("=======================================")

    pdf_path = RAW_DIR / "SquadLists-English.pdf"

    descargar(FIFA_SQUAD_PDF, pdf_path)

    print("\n[1] Extrayendo equipos desde PDF FIFA...")
    equipos_base = extraer_equipos_pdf(pdf_path)
    equipos = enriquecer_equipos(equipos_base)
    equipos.to_csv(CSV_EQUIPOS, index=False, encoding="utf-8-sig")
    print(f"OK: {CSV_EQUIPOS} -> {len(equipos)} equipos")

    if len(equipos) != 48:
        print("ALERTA: no salieron 48 equipos. Revisar extracción del PDF.")
    else:
        print("VALIDADO: salieron 48 equipos.")

    print("\n[2] Extrayendo jugadores desde PDF FIFA...")
    jugadores = extraer_jugadores_pdf(pdf_path)
    jugadores.to_csv(CSV_JUGADORES, index=False, encoding="utf-8-sig")
    print(f"OK: {CSV_JUGADORES} -> {len(jugadores)} jugadores detectados")

    if len(jugadores) != 1248:
        print("AVISO: no salieron 1248 jugadores exactos. Igual revisa el CSV/debug.")
    else:
        print("VALIDADO: salieron 1248 jugadores.")

    print("\n[3] Scrapeando sedes desde página principal FIFA/On Location...")
    sedes = extraer_sedes_desde_home(geocodificar=True)
    sedes.to_csv(CSV_SEDES, index=False, encoding="utf-8-sig")
    print(f"OK: {CSV_SEDES} -> {len(sedes)} sedes")

    if len(sedes) != 16:
        print("ALERTA: no salieron 16 sedes. Revisar estructura de la página.")
    else:
        print("VALIDADO: salieron 16 sedes.")

    print("\n=======================================")
    print("ARCHIVOS GENERADOS")
    print(CSV_EQUIPOS)
    print(CSV_SEDES)
    print(CSV_JUGADORES)
    print("=======================================")


if __name__ == "__main__":
    main()
