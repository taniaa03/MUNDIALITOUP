import re
import logging
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import pandas as pd
from bs4 import BeautifulSoup
from unidecode import unidecode

logging.getLogger("urllib3").setLevel(logging.WARNING)


# ============================================================
# CONFIGURACIÓN
# ============================================================

OUT_DIR = Path("bloque_a_mundial_2026")
OUT_DIR.mkdir(exist_ok=True)

CSV_FIXTURE = OUT_DIR / "mundial_2026_fixture.csv"
CSV_EQUIPOS = OUT_DIR / "mundial_2026_equipos.csv"
CSV_SEDES = OUT_DIR / "mundial_2026_sedes.csv"
DEBUG_FIXTURE = OUT_DIR / "debug_fixture_html_text.txt"

# Fuente principal: FIFA World Cup 2026 Hospitality / On Location
# Es la página oficial de hospitalidad del Mundial y publica los 104 partidos.
FIFA_HOSPITALITY_HOME = "https://fifaworldcup26.hospitality.fifa.com/"

# Fuente informativa oficial FIFA
FIFA_SCORES_FIXTURES = "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AnderProyectoMundial2026-Fixture/3.0)",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}


# ============================================================
# MAPAS DE TORNEO
# ============================================================

MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}

WEEKDAYS = {
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
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

TEAM_ALIASES = {
    "usa": "United States",
    "u s a": "United States",
    "united states": "United States",

    "iran": "Iran",
    "ir iran": "Iran",

    "south korea": "Korea Republic",
    "korea republic": "Korea Republic",

    "czech republic": "Czechia",
    "czechia": "Czechia",

    "cape verde": "Cabo Verde",
    "cabo verde": "Cabo Verde",

    "ivory coast": "Côte D'Ivoire",
    "cote d ivoire": "Côte D'Ivoire",
    "côte d ivoire": "Côte D'Ivoire",

    "dr congo": "Congo DR",
    "congo dr": "Congo DR",

    "turkiye": "Türkiye",
    "türkiye": "Türkiye",

    "curacao": "Curaçao",
    "curaçao": "Curaçao",

    "bosnia herzegovina": "Bosnia And Herzegovina",
    "bosnia and herzegovina": "Bosnia And Herzegovina",
}

TEAM_CODES = {
    "Algeria": "ALG",
    "Argentina": "ARG",
    "Australia": "AUS",
    "Austria": "AUT",
    "Belgium": "BEL",
    "Bosnia And Herzegovina": "BIH",
    "Brazil": "BRA",
    "Cabo Verde": "CPV",
    "Canada": "CAN",
    "Colombia": "COL",
    "Congo DR": "COD",
    "Côte D'Ivoire": "CIV",
    "Croatia": "CRO",
    "Curaçao": "CUW",
    "Czechia": "CZE",
    "Ecuador": "ECU",
    "Egypt": "EGY",
    "England": "ENG",
    "France": "FRA",
    "Germany": "GER",
    "Ghana": "GHA",
    "Haiti": "HAI",
    "Iran": "IRN",
    "Iraq": "IRQ",
    "Japan": "JPN",
    "Jordan": "JOR",
    "Korea Republic": "KOR",
    "Mexico": "MEX",
    "Morocco": "MAR",
    "Netherlands": "NED",
    "New Zealand": "NZL",
    "Norway": "NOR",
    "Panama": "PAN",
    "Paraguay": "PAR",
    "Portugal": "POR",
    "Qatar": "QAT",
    "Saudi Arabia": "KSA",
    "Scotland": "SCO",
    "Senegal": "SEN",
    "South Africa": "RSA",
    "Spain": "ESP",
    "Sweden": "SWE",
    "Switzerland": "SUI",
    "Tunisia": "TUN",
    "Türkiye": "TUR",
    "United States": "USA",
    "Uruguay": "URU",
    "Uzbekistan": "UZB",
}

VENUE_INFO = {
    "Atlanta Stadium": {
        "ciudad": "Atlanta",
        "pais_sede": "United States",
        "estadio": "Mercedes-Benz Stadium",
        "timezone_sede": "America/New_York",
    },
    "Boston Stadium": {
        "ciudad": "Boston",
        "pais_sede": "United States",
        "estadio": "Gillette Stadium",
        "timezone_sede": "America/New_York",
    },
    "Dallas Stadium": {
        "ciudad": "Dallas",
        "pais_sede": "United States",
        "estadio": "AT&T Stadium",
        "timezone_sede": "America/Chicago",
    },
    "Houston Stadium": {
        "ciudad": "Houston",
        "pais_sede": "United States",
        "estadio": "NRG Stadium",
        "timezone_sede": "America/Chicago",
    },
    "Kansas City Stadium": {
        "ciudad": "Kansas City",
        "pais_sede": "United States",
        "estadio": "Arrowhead Stadium",
        "timezone_sede": "America/Chicago",
    },
    "Los Angeles Stadium": {
        "ciudad": "Los Angeles",
        "pais_sede": "United States",
        "estadio": "SoFi Stadium",
        "timezone_sede": "America/Los_Angeles",
    },
    "Miami Stadium": {
        "ciudad": "Miami",
        "pais_sede": "United States",
        "estadio": "Hard Rock Stadium",
        "timezone_sede": "America/New_York",
    },
    "New York New Jersey Stadium": {
        "ciudad": "New York New Jersey",
        "pais_sede": "United States",
        "estadio": "MetLife Stadium",
        "timezone_sede": "America/New_York",
    },
    "Philadelphia Stadium": {
        "ciudad": "Philadelphia",
        "pais_sede": "United States",
        "estadio": "Lincoln Financial Field",
        "timezone_sede": "America/New_York",
    },
    "San Francisco Bay Area Stadium": {
        "ciudad": "San Francisco Bay Area",
        "pais_sede": "United States",
        "estadio": "Levi's Stadium",
        "timezone_sede": "America/Los_Angeles",
    },
    "Seattle Stadium": {
        "ciudad": "Seattle",
        "pais_sede": "United States",
        "estadio": "Lumen Field",
        "timezone_sede": "America/Los_Angeles",
    },
    "Toronto Stadium": {
        "ciudad": "Toronto",
        "pais_sede": "Canada",
        "estadio": "BMO Field",
        "timezone_sede": "America/Toronto",
    },
    "BC Place Vancouver": {
        "ciudad": "Vancouver",
        "pais_sede": "Canada",
        "estadio": "BC Place",
        "timezone_sede": "America/Vancouver",
    },
    "Mexico City Stadium": {
        "ciudad": "Mexico City",
        "pais_sede": "Mexico",
        "estadio": "Estadio Azteca",
        "timezone_sede": "America/Mexico_City",
    },
    "Guadalajara Stadium": {
        "ciudad": "Guadalajara",
        "pais_sede": "Mexico",
        "estadio": "Estadio Akron",
        "timezone_sede": "America/Mexico_City",
    },
    "Monterrey Stadium": {
        "ciudad": "Monterrey",
        "pais_sede": "Mexico",
        "estadio": "Estadio BBVA",
        "timezone_sede": "America/Monterrey",
    },
}

# Nombres alternativos que la web puede mostrar.
# Ejemplos reales: "Estadio Guadalajara" y "Estadio Monterrey".
VENUE_ALIASES = {
    "atlanta stadium": "Atlanta Stadium",
    "boston stadium": "Boston Stadium",
    "dallas stadium": "Dallas Stadium",
    "houston stadium": "Houston Stadium",
    "kansas city stadium": "Kansas City Stadium",
    "los angeles stadium": "Los Angeles Stadium",
    "miami stadium": "Miami Stadium",
    "new york new jersey stadium": "New York New Jersey Stadium",
    "new york/new jersey stadium": "New York New Jersey Stadium",
    "philadelphia stadium": "Philadelphia Stadium",
    "san francisco bay area stadium": "San Francisco Bay Area Stadium",
    "seattle stadium": "Seattle Stadium",
    "toronto stadium": "Toronto Stadium",
    "bc place vancouver": "BC Place Vancouver",
    "vancouver stadium": "BC Place Vancouver",
    "vancouver": "BC Place Vancouver",
    "mexico city stadium": "Mexico City Stadium",
    "estadio azteca": "Mexico City Stadium",
    "guadalajara stadium": "Guadalajara Stadium",
    "estadio guadalajara": "Guadalajara Stadium",
    "estadio akron": "Guadalajara Stadium",
    "monterrey stadium": "Monterrey Stadium",
    "estadio monterrey": "Monterrey Stadium",
    "estadio bbva": "Monterrey Stadium",
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


def canon_team(nombre):
    nombre = limpiar(nombre)
    key = normalizar(nombre)

    # Knockout placeholders: W73, L101, 1A, 2B, etc.
    if re.fullmatch(r"[WL]\d{1,3}", nombre, flags=re.I):
        return nombre.upper()
    if re.fullmatch(r"\d[A-L]", nombre, flags=re.I):
        return nombre.upper()
    if nombre.upper() == "TBD":
        return "TBD"

    return TEAM_ALIASES.get(key, nombre)


def canon_venue(nombre):
    key = normalizar(nombre)
    if key in VENUE_ALIASES:
        return VENUE_ALIASES[key]
    for v in VENUE_INFO.keys():
        if normalizar(v) == key:
            return v
    return ""


def crear_lookup_grupo():
    lookup = {}
    for grupo, equipos in GRUPOS_2026.items():
        for e in equipos:
            lookup[normalizar(e)] = grupo
    return lookup


def fase_por_match_no(match_no):
    n = int(match_no)

    if 1 <= n <= 72:
        return "Fase de grupos", "Group Stage"
    if 73 <= n <= 88:
        return "Dieciseisavos de final", "Round of 32"
    if 89 <= n <= 96:
        return "Octavos de final", "Round of 16"
    if 97 <= n <= 100:
        return "Cuartos de final", "Quarter-finals"
    if 101 <= n <= 102:
        return "Semifinales", "Semi-finals"
    if n == 103:
        return "Tercer puesto", "Bronze Final"
    if n == 104:
        return "Final", "Final"

    return "", ""


def convertir_hora_12_a_24(hora_12):
    hora_12 = limpiar(hora_12).lower()
    dt = datetime.strptime(hora_12, "%I:%M %p")
    return dt.strftime("%H:%M")


def buscar_atras(lines, start_idx, predicate, limite=60):
    for j in range(start_idx - 1, max(-1, start_idx - limite), -1):
        if predicate(lines[j]):
            return j, lines[j]
    return None, ""


def buscar_adelante(lines, start_idx, end_idx, predicate):
    for j in range(start_idx + 1, min(len(lines), end_idx)):
        if predicate(lines[j]):
            return j, lines[j]
    return None, ""


def cargar_ids_equipos():
    if not CSV_EQUIPOS.exists():
        return {}, {}

    try:
        df = pd.read_csv(CSV_EQUIPOS)
        id_map = {}
        code_map = {}

        for _, r in df.iterrows():
            seleccion = canon_team(r.get("seleccion", ""))
            if seleccion:
                id_map[normalizar(seleccion)] = r.get("id_equipo", "")
                code_map[normalizar(seleccion)] = r.get("codigo_fifa", "")

            original = canon_team(r.get("seleccion_original_fifa", ""))
            if original:
                id_map[normalizar(original)] = r.get("id_equipo", "")
                code_map[normalizar(original)] = r.get("codigo_fifa", "")

        return id_map, code_map
    except Exception:
        return {}, {}


def cargar_ids_sedes():
    if not CSV_SEDES.exists():
        return {}

    try:
        df = pd.read_csv(CSV_SEDES)
        id_map = {}

        for _, r in df.iterrows():
            for col in ["nombre_fifa_estadio", "estadio"]:
                val = limpiar(r.get(col, ""))
                if val:
                    id_map[normalizar(val)] = r.get("id_sede", "")

        return id_map
    except Exception:
        return {}


# ============================================================
# SCRAPER FIXTURE
# ============================================================

def descargar_html_fixture():
    print(f"Descargando fixture desde: {FIFA_HOSPITALITY_HOME}")
    r = requests.get(FIFA_HOSPITALITY_HOME, headers=HEADERS, timeout=90)
    r.raise_for_status()
    return r.text


def extraer_fixture_desde_hospitality(html):
    soup = BeautifulSoup(html, "html.parser")
    lines = [limpiar(x) for x in soup.get_text("\n").splitlines() if limpiar(x)]

    DEBUG_FIXTURE.write_text("\n".join(lines), encoding="utf-8")

    grupo_lookup = crear_lookup_grupo()
    id_equipo_map, codigo_equipo_map = cargar_ids_equipos()
    id_sede_map = cargar_ids_sedes()

    venue_norm_map = {normalizar(k): k for k in VENUE_INFO.keys()}
    for alias, canonical in VENUE_ALIASES.items():
        venue_norm_map[normalizar(alias)] = canonical

    filas = []
    vistos = set()

    for idx, line in enumerate(lines):
        m = re.match(r"^M(\d{1,3})\s*:\s*(.+?)\s+vs\.?\s*(.+)$", line, flags=re.I)
        if not m:
            continue

        match_no = int(m.group(1))
        local_original = limpiar(m.group(2))
        visitante_original = limpiar(m.group(3))

        # Evitar duplicados por cards repetidos
        if match_no in vistos:
            continue
        vistos.add(match_no)

        equipo_local = canon_team(local_original)
        equipo_visitante = canon_team(visitante_original)

        # Buscar hora hacia atrás.
        # En la web, cada card tiene: Weekday, Month, Day, at, Time, Venue, Country, Mxx.
        time_idx, hora_12 = buscar_atras(
            lines,
            idx,
            lambda x: re.fullmatch(r"\d{1,2}:\d{2}\s*(am|pm)", x.lower()) is not None,
            limite=100,
        )

        # Buscar fecha hacia atrás desde la hora.
        weekday = ""
        month_name = ""
        day = ""

        if time_idx is not None:
            _, weekday = buscar_atras(lines, time_idx, lambda x: x in WEEKDAYS, limite=30)
            _, month_name = buscar_atras(lines, time_idx, lambda x: x in MONTHS, limite=30)
            _, day = buscar_atras(lines, time_idx, lambda x: re.fullmatch(r"\d{1,2}", x) is not None, limite=30)

        # Buscar estadio entre la hora y la línea Mxx.
        # Ahora reconoce alias como "Estadio Guadalajara" y "Estadio Monterrey".
        nombre_fifa_estadio = ""
        if time_idx is not None:
            for j in range(time_idx + 1, idx):
                possible = venue_norm_map.get(normalizar(lines[j]))
                if possible:
                    nombre_fifa_estadio = possible
                    break

        # Fallback por búsqueda cerca del Mxx
        if not nombre_fifa_estadio:
            for j in range(max(0, idx - 30), min(len(lines), idx + 3)):
                possible = venue_norm_map.get(normalizar(lines[j]))
                if possible:
                    nombre_fifa_estadio = possible
                    break

        venue = VENUE_INFO.get(nombre_fifa_estadio, {})
        ciudad = venue.get("ciudad", "")
        pais_sede = venue.get("pais_sede", "")
        estadio = venue.get("estadio", "")
        timezone_sede = venue.get("timezone_sede", "")

        fecha_local = ""
        hora_24 = ""
        datetime_local_iso = ""
        datetime_utc_iso = ""
        fecha_peru = ""
        hora_peru = ""
        datetime_peru_iso = ""

        if month_name and day and hora_12:
            try:
                year = 2026
                mes = MONTHS[month_name]
                dia = int(day)
                hora_24 = convertir_hora_12_a_24(hora_12)

                # Aunque falle la zona horaria, fecha_local y hora_local_24h no deben quedar vacías.
                fecha_local = f"{year:04d}-{mes:02d}-{dia:02d}"

                if timezone_sede:
                    h, minute = map(int, hora_24.split(":"))
                    tz_local = ZoneInfo(timezone_sede)
                    dt_local = datetime(year, mes, dia, h, minute, tzinfo=tz_local)

                    dt_utc = dt_local.astimezone(ZoneInfo("UTC"))
                    dt_peru = dt_local.astimezone(ZoneInfo("America/Lima"))

                    datetime_local_iso = dt_local.isoformat()
                    datetime_utc_iso = dt_utc.isoformat()
                    fecha_peru = dt_peru.strftime("%Y-%m-%d")
                    hora_peru = dt_peru.strftime("%H:%M")
                    datetime_peru_iso = dt_peru.isoformat()
                else:
                    # Último recurso: no inventa conversión horaria, pero no deja la fecha vacía.
                    datetime_local_iso = f"{fecha_local}T{hora_24}:00"
                    fecha_peru = fecha_local
                    hora_peru = hora_24
                    datetime_peru_iso = f"{fecha_peru}T{hora_peru}:00"
            except Exception:
                pass

        fase, ronda = fase_por_match_no(match_no)

        grupo = ""
        if 1 <= match_no <= 72:
            g1 = grupo_lookup.get(normalizar(equipo_local), "")
            g2 = grupo_lookup.get(normalizar(equipo_visitante), "")
            if g1 and g1 == g2:
                grupo = g1
            elif g1:
                grupo = g1

        codigo_local = codigo_equipo_map.get(normalizar(equipo_local), TEAM_CODES.get(equipo_local, ""))
        codigo_visitante = codigo_equipo_map.get(normalizar(equipo_visitante), TEAM_CODES.get(equipo_visitante, ""))

        id_equipo_local = id_equipo_map.get(normalizar(equipo_local), "")
        id_equipo_visitante = id_equipo_map.get(normalizar(equipo_visitante), "")
        id_sede = id_sede_map.get(normalizar(nombre_fifa_estadio), "") or id_sede_map.get(normalizar(estadio), "")

        filas.append({
            "id_partido": match_no,
            "match_no": match_no,
            "fase": fase,
            "ronda": ronda,
            "grupo": grupo,

            "fecha_local": fecha_local,
            "dia_semana_en": weekday,
            "hora_local_12h": hora_12,
            "hora_local_24h": hora_24,
            "timezone_sede": timezone_sede,
            "datetime_local_iso": datetime_local_iso,

            "datetime_utc_iso": datetime_utc_iso,
            "fecha_peru": fecha_peru,
            "hora_peru": hora_peru,
            "datetime_peru_iso": datetime_peru_iso,

            "id_equipo_local": id_equipo_local,
            "equipo_local": equipo_local,
            "equipo_local_original": local_original,
            "codigo_local": codigo_local,

            "id_equipo_visitante": id_equipo_visitante,
            "equipo_visitante": equipo_visitante,
            "equipo_visitante_original": visitante_original,
            "codigo_visitante": codigo_visitante,

            "id_sede": id_sede,
            "ciudad": ciudad,
            "pais_sede": pais_sede,
            "estadio": estadio,
            "nombre_fifa_estadio": nombre_fifa_estadio,

            "partido_nombre": f"{equipo_local} vs {equipo_visitante}",
            "estado": "To be played",
            "resultado": "",
            "goles_local": "",
            "goles_visitante": "",

            "fuente_fixture": FIFA_HOSPITALITY_HOME,
            "fuente_verificacion_fifa": FIFA_SCORES_FIXTURES,
            "nota": "Fixture extraído de FIFA World Cup 2026 Hospitality/On Location. Horas interpretadas como hora local de la sede y convertidas a UTC y America/Lima.",
        })

    df = pd.DataFrame(filas)

    if df.empty:
        return df

    df = df.sort_values("match_no").reset_index(drop=True)

    columnas = [
        "id_partido",
        "match_no",
        "fase",
        "ronda",
        "grupo",

        "fecha_local",
        "dia_semana_en",
        "hora_local_12h",
        "hora_local_24h",
        "timezone_sede",
        "datetime_local_iso",

        "datetime_utc_iso",
        "fecha_peru",
        "hora_peru",
        "datetime_peru_iso",

        "id_equipo_local",
        "equipo_local",
        "equipo_local_original",
        "codigo_local",

        "id_equipo_visitante",
        "equipo_visitante",
        "equipo_visitante_original",
        "codigo_visitante",

        "id_sede",
        "ciudad",
        "pais_sede",
        "estadio",
        "nombre_fifa_estadio",

        "partido_nombre",
        "estado",
        "resultado",
        "goles_local",
        "goles_visitante",

        "fuente_fixture",
        "fuente_verificacion_fifa",
        "nota",
    ]

    return df[columnas]


def reparar_fechas_vacias(df):
    """
    Última capa de seguridad:
    si por cualquier cambio del HTML queda alguna fecha vacía,
    intenta rellenarla mirando partidos vecinos y el orden del torneo.
    No debería activarse casi nunca con los alias de sedes corregidos.
    """
    if df.empty:
        return df

    # Normalizar NaN a cadena vacía
    for col in ["fecha_local", "hora_local_12h", "hora_local_24h", "timezone_sede",
                "datetime_local_iso", "fecha_peru", "hora_peru", "datetime_peru_iso"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    faltantes = df[df["fecha_local"] == ""]
    if faltantes.empty:
        return df

    print("AVISO: reparando fechas vacías con fallback por contexto...")

    # Fallback conservador: busca en filas vecinas por match_no.
    df = df.sort_values("match_no").reset_index(drop=True)

    for idx in df.index:
        if df.at[idx, "fecha_local"] != "":
            continue

        # Busca hacia atrás y adelante un partido con fecha.
        fecha_ref = ""
        hora_ref = ""
        for j in range(idx - 1, -1, -1):
            if df.at[j, "fecha_local"] != "":
                fecha_ref = df.at[j, "fecha_local"]
                hora_ref = df.at[j, "hora_local_24h"]
                break

        if not fecha_ref:
            for j in range(idx + 1, len(df)):
                if df.at[j, "fecha_local"] != "":
                    fecha_ref = df.at[j, "fecha_local"]
                    hora_ref = df.at[j, "hora_local_24h"]
                    break

        # Esto evita vacío, pero deja nota clara.
        if fecha_ref:
            df.at[idx, "fecha_local"] = fecha_ref
            if df.at[idx, "hora_local_24h"] == "":
                df.at[idx, "hora_local_24h"] = hora_ref
            if df.at[idx, "fecha_peru"] == "":
                df.at[idx, "fecha_peru"] = fecha_ref
            if df.at[idx, "hora_peru"] == "":
                df.at[idx, "hora_peru"] = df.at[idx, "hora_local_24h"]
            df.at[idx, "nota"] = str(df.at[idx, "nota"]) + " FECHA_REPARADA_POR_CONTEXTO_REVISAR."

    return df


def validar_fixture(df):
    print("\nVALIDACIÓN FIXTURE")
    print("------------------")

    if df.empty:
        print("ERROR: no se extrajo ningún partido.")
        print(f"Revisa el archivo debug: {DEBUG_FIXTURE}")
        return

    print(f"Partidos extraídos: {len(df)}")

    faltantes = sorted(set(range(1, 105)) - set(df["match_no"].astype(int).tolist()))
    duplicados = df[df.duplicated("match_no", keep=False)]["match_no"].tolist()

    if faltantes:
        print("ALERTA: faltan match_no:", faltantes)
    else:
        print("OK: no falta ningún match_no del 1 al 104.")

    if duplicados:
        print("ALERTA: match_no duplicados:", duplicados)
    else:
        print("OK: no hay match_no duplicados.")

    if len(df) == 104:
        print("VALIDADO: salieron 104 partidos.")
    else:
        print("ALERTA: no salieron 104 partidos exactos.")

    print("\nConteo por fase:")
    print(df["fase"].value_counts(dropna=False).to_string())

    print("\nConteo por sede FIFA:")
    print(df["nombre_fifa_estadio"].value_counts(dropna=False).to_string())

    problemas_fecha = df[
        (df["fecha_local"] == "") |
        (df["hora_local_24h"] == "") |
        (df["nombre_fifa_estadio"] == "")
    ]

    if not problemas_fecha.empty:
        print("\nALERTA: hay partidos con fecha/hora/sede incompleta:")
        print(problemas_fecha[["match_no", "partido_nombre", "fecha_local", "hora_local_24h", "nombre_fifa_estadio"]].to_string(index=False))
    else:
        print("\nOK: todos tienen fecha, hora y sede.")


def main():
    print("=======================================")
    print("BLOQUE A - MUNDIAL 2026")
    print("SCRAPER FIXTURE SUPER COMPLETO V4 SIN FECHAS VACÍAS")
    print("=======================================")

    html = descargar_html_fixture()
    fixture = extraer_fixture_desde_hospitality(html)
    fixture = reparar_fechas_vacias(fixture)

    fixture.to_csv(CSV_FIXTURE, index=False, encoding="utf-8-sig")
    print(f"\nCSV generado: {CSV_FIXTURE}")

    validar_fixture(fixture)

    print("\nColumnas generadas:")
    for c in fixture.columns:
        print("-", c)

    print("\n=======================================")
    print("PROCESO TERMINADO")
    print("=======================================")


if __name__ == "__main__":
    main()
