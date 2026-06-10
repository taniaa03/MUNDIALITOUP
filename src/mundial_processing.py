from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "mundial_2026" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "mundial_2026" / "processed"

TOURNAMENT_START = date(2026, 6, 11)

COORDENADAS_SEDES = {
    "Boston": (42.0909, -71.2643),
    "Dallas": (32.7473, -97.0945),
    "Guadalajara": (20.6819, -103.4620),
    "Kansas City": (39.0490, -94.4839),
    "Los Angeles": (33.9535, -118.3392),
    "Mexico City": (19.3029, -99.1505),
    "Monterrey": (25.6682, -100.2445),
    "New York New Jersey": (40.8135, -74.0745),
    "San Francisco Bay Area": (37.4030, -121.9700),
}

POSICIONES = {
    "GK": "Arquero",
    "DF": "Defensa",
    "MF": "Mediocampista",
    "FW": "Delantero",
}

ALIAS_SELECCIONES_FIXTURE = {
    "turkey": "Türkiye",
    "the netherlands": "Netherlands",
}

FUENTE_SEDES = "https://fifaworldcup26.suites.fifa.com/venues/"
NOTA_SEDE = (
    "Sede complementada desde el fixture del bloque Mundial 2026. "
    "Capacidad y coordenadas aproximadas para visualizacion."
)

SEDES_COMPLEMENTARIAS = [
    {
        "id_sede": 12,
        "ciudad": "Los Angeles",
        "pais": "United States",
        "estadio": "SoFi Stadium",
        "nombre_fifa_estadio": "Los Angeles Stadium",
        "capacidad_aprox": 70240,
        "cantidad_partidos": 0,
        "latitud": 33.9535,
        "longitud": -118.3392,
        "fuente_sedes": FUENTE_SEDES,
        "nota": NOTA_SEDE,
    },
    {
        "id_sede": 13,
        "ciudad": "New York New Jersey",
        "pais": "United States",
        "estadio": "MetLife Stadium",
        "nombre_fifa_estadio": "New York New Jersey Stadium",
        "capacidad_aprox": 82500,
        "cantidad_partidos": 0,
        "latitud": 40.8135,
        "longitud": -74.0745,
        "fuente_sedes": FUENTE_SEDES,
        "nota": NOTA_SEDE,
    },
    {
        "id_sede": 14,
        "ciudad": "San Francisco Bay Area",
        "pais": "United States",
        "estadio": "Levi's Stadium",
        "nombre_fifa_estadio": "San Francisco Bay Area Stadium",
        "capacidad_aprox": 68500,
        "cantidad_partidos": 0,
        "latitud": 37.4030,
        "longitud": -121.9700,
        "fuente_sedes": FUENTE_SEDES,
        "nota": NOTA_SEDE,
    },
    {
        "id_sede": 15,
        "ciudad": "Kansas City",
        "pais": "United States",
        "estadio": "Arrowhead Stadium",
        "nombre_fifa_estadio": "Kansas City Stadium",
        "capacidad_aprox": 76416,
        "cantidad_partidos": 0,
        "latitud": 39.0490,
        "longitud": -94.4839,
        "fuente_sedes": FUENTE_SEDES,
        "nota": NOTA_SEDE,
    },
    {
        "id_sede": 16,
        "ciudad": "Mexico City",
        "pais": "Mexico",
        "estadio": "Estadio Azteca",
        "nombre_fifa_estadio": "Mexico City Stadium",
        "capacidad_aprox": 87523,
        "cantidad_partidos": 0,
        "latitud": 19.3029,
        "longitud": -99.1505,
        "fuente_sedes": FUENTE_SEDES,
        "nota": NOTA_SEDE,
    },
]

PARTIDOS_ELIMINACION_COMPLEMENTARIOS = [
    (89, "Octavos de final", "Round of 16", "2026-07-04", "16:00", "2026-07-04", "15:00", "W73", "W74", "Philadelphia", "United States", "Lincoln Financial Field"),
    (90, "Octavos de final", "Round of 16", "2026-07-04", "16:00", "2026-07-04", "16:00", "W75", "W76", "Houston", "United States", "NRG Stadium"),
    (91, "Octavos de final", "Round of 16", "2026-07-05", "16:00", "2026-07-05", "15:00", "W77", "W78", "New York New Jersey", "United States", "MetLife Stadium"),
    (92, "Octavos de final", "Round of 16", "2026-07-05", "16:00", "2026-07-05", "16:00", "W79", "W80", "Mexico City", "Mexico", "Estadio Azteca"),
    (93, "Octavos de final", "Round of 16", "2026-07-06", "16:00", "2026-07-06", "16:00", "W81", "W82", "Dallas", "United States", "AT&T Stadium"),
    (94, "Octavos de final", "Round of 16", "2026-07-06", "16:00", "2026-07-06", "18:00", "W83", "W84", "Seattle", "United States", "Lumen Field"),
    (95, "Octavos de final", "Round of 16", "2026-07-07", "16:00", "2026-07-07", "15:00", "W85", "W86", "Atlanta", "United States", "Mercedes-Benz Stadium"),
    (96, "Octavos de final", "Round of 16", "2026-07-07", "16:00", "2026-07-07", "18:00", "W87", "W88", "Vancouver", "Canada", "BC Place"),
    (97, "Cuartos de final", "Quarter-finals", "2026-07-09", "16:00", "2026-07-09", "15:00", "W89", "W90", "Boston", "United States", "Gillette Stadium"),
    (99, "Cuartos de final", "Quarter-finals", "2026-07-10", "16:00", "2026-07-10", "16:00", "W91", "W92", "Miami", "United States", "Hard Rock Stadium"),
    (101, "Semifinal", "Semi-finals", "2026-07-14", "16:00", "2026-07-14", "15:00", "W97", "W98", "Dallas", "United States", "AT&T Stadium"),
    (102, "Semifinal", "Semi-finals", "2026-07-15", "16:00", "2026-07-15", "15:00", "W99", "W100", "Atlanta", "United States", "Mercedes-Benz Stadium"),
    (103, "Tercer puesto", "Third-place play-off", "2026-07-18", "16:00", "2026-07-18", "15:00", "L101", "L102", "Miami", "United States", "Hard Rock Stadium"),
    (104, "Final", "Final", "2026-07-19", "16:00", "2026-07-19", "15:00", "W101", "W102", "New York New Jersey", "United States", "MetLife Stadium"),
]


def normalizar_texto(valor: object) -> str:
    texto = "" if pd.isna(valor) else str(valor).strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"[^a-zA-Z0-9]+", " ", texto).lower()
    return re.sub(r"\s+", " ", texto).strip()


def limpiar_nombre_jugador(valor: object) -> str:
    texto = "" if pd.isna(valor) else str(valor).strip()
    partes = re.split(r"\s+", texto)
    limpias = []
    vistas = set()
    for parte in partes:
        clave = normalizar_texto(parte)
        if clave and clave not in vistas:
            limpias.append(parte)
            vistas.add(clave)
    return " ".join(limpias)


def extraer_pais_club(club: object) -> str:
    texto = "" if pd.isna(club) else str(club)
    match = re.search(r"\(([A-Z]{2,3})\)\s*$", texto)
    return match.group(1) if match else ""


def limpiar_club(club: object) -> str:
    texto = "" if pd.isna(club) else str(club).strip()
    texto = re.sub(r"\s*\([A-Z]{2,3}\)\s*$", "", texto)
    return re.sub(r"\s+", " ", texto).strip()


def calcular_edad(fecha_nacimiento: object) -> int | pd.NA:
    fecha = pd.to_datetime(fecha_nacimiento, format="%d/%m/%Y", errors="coerce")
    if pd.isna(fecha):
        return pd.NA
    cumple = (TOURNAMENT_START.month, TOURNAMENT_START.day) >= (
        fecha.month,
        fecha.day,
    )
    return TOURNAMENT_START.year - fecha.year - (0 if cumple else 1)


def cargar_csv(nombre: str) -> pd.DataFrame:
    path = RAW_DIR / nombre
    if not path.exists():
        raise FileNotFoundError(f"No se encontro el archivo requerido: {path}")
    return pd.read_csv(path)


def crear_dim_selecciones() -> pd.DataFrame:
    df = cargar_csv("mundial_2026_equipos.csv").copy()
    df["seleccion_normalizada"] = df["seleccion"].apply(normalizar_texto)
    df["clasificado"] = df["clasificado"].fillna("Si")
    df["debut_mundial"] = pd.to_numeric(df["debut_mundial"], errors="coerce").astype(
        "Int64"
    )

    columnas = [
        "id_equipo",
        "seleccion",
        "seleccion_normalizada",
        "seleccion_original_fifa",
        "confederacion",
        "grupo",
        "codigo_fifa",
        "pais",
        "clasificado",
        "debut_mundial",
        "fuente_equipos",
    ]
    return df[columnas].drop_duplicates(subset=["id_equipo"]).sort_values("id_equipo")


def crear_dim_sedes() -> pd.DataFrame:
    df = cargar_csv("mundial_2026_sedes.csv").copy()
    df = pd.concat([df, pd.DataFrame(SEDES_COMPLEMENTARIAS)], ignore_index=True)
    df["ciudad_normalizada"] = df["ciudad"].apply(normalizar_texto)
    df["capacidad_aprox"] = pd.to_numeric(df["capacidad_aprox"], errors="coerce").astype(
        "Int64"
    )
    df["cantidad_partidos"] = pd.to_numeric(
        df["cantidad_partidos"], errors="coerce"
    ).astype("Int64")

    for ciudad, (latitud, longitud) in COORDENADAS_SEDES.items():
        mask = df["ciudad"].eq(ciudad)
        df.loc[mask & df["latitud"].isna(), "latitud"] = latitud
        df.loc[mask & df["longitud"].isna(), "longitud"] = longitud

    columnas = [
        "id_sede",
        "ciudad",
        "ciudad_normalizada",
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
    return df[columnas].drop_duplicates(subset=["id_sede"]).sort_values("id_sede")


def corregir_equipos_fixture(df: pd.DataFrame) -> pd.DataFrame:
    equipos = crear_dim_selecciones()
    equipos_lookup = equipos.set_index("seleccion_normalizada")[
        ["id_equipo", "seleccion", "grupo", "codigo_fifa"]
    ].to_dict("index")

    for lado in ["local", "visitante"]:
        equipo_col = f"equipo_{lado}"
        normalizado_col = f"equipo_{lado}_normalizado"
        codigo_col = f"codigo_{lado}"
        id_col = f"id_equipo_{lado}"
        grupo_col = f"grupo_{lado}"

        df[equipo_col] = df[equipo_col].apply(
            lambda valor: ALIAS_SELECCIONES_FIXTURE.get(normalizar_texto(valor), valor)
        )
        df[normalizado_col] = df[equipo_col].apply(normalizar_texto)
        df[grupo_col] = df[normalizado_col].map(
            lambda valor: equipos_lookup.get(valor, {}).get("grupo", pd.NA)
        )

        mask = df[normalizado_col].isin(equipos_lookup.keys())
        df.loc[mask, id_col] = df.loc[mask, normalizado_col].map(
            lambda valor: equipos_lookup[valor]["id_equipo"]
        )
        df.loc[mask, equipo_col] = df.loc[mask, normalizado_col].map(
            lambda valor: equipos_lookup[valor]["seleccion"]
        )
        df.loc[mask, codigo_col] = df.loc[mask, normalizado_col].map(
            lambda valor: equipos_lookup[valor]["codigo_fifa"]
        )
        df.loc[mask, normalizado_col] = df.loc[mask, equipo_col].apply(normalizar_texto)

    grupo_vacio = df["grupo"].isna() | df["grupo"].astype(str).str.strip().eq("")
    mismo_grupo = (
        df["grupo_local"].notna()
        & df["grupo_visitante"].notna()
        & df["grupo_local"].astype(str).eq(df["grupo_visitante"].astype(str))
    )
    df.loc[grupo_vacio & mismo_grupo, "grupo"] = df.loc[
        grupo_vacio & mismo_grupo, "grupo_local"
    ]
    df = df.drop(columns=["grupo_local", "grupo_visitante"])
    df["partido_nombre"] = df["equipo_local"].astype(str) + " vs " + df[
        "equipo_visitante"
    ].astype(str)
    return df


def asignar_sedes_fixture(df: pd.DataFrame, dim_sedes: pd.DataFrame) -> pd.DataFrame:
    sedes = dim_sedes.copy()
    sedes["sede_normalizada"] = sedes["estadio"].apply(normalizar_texto)
    sedes_lookup = sedes.set_index("sede_normalizada")[
        ["id_sede", "ciudad", "pais"]
    ].to_dict("index")

    df["sede_normalizada"] = df["estadio"].apply(normalizar_texto)
    for idx, row in df.iterrows():
        sede = sedes_lookup.get(row["sede_normalizada"])
        if not sede:
            continue
        if pd.isna(row.get("id_sede")):
            df.at[idx, "id_sede"] = sede["id_sede"]
        if pd.isna(row.get("ciudad")) or not str(row.get("ciudad")).strip():
            df.at[idx, "ciudad"] = sede["ciudad"]
        if pd.isna(row.get("pais_sede")) or not str(row.get("pais_sede")).strip():
            df.at[idx, "pais_sede"] = sede["pais"]

    return df


def completar_fixture_eliminacion(
    fixture: pd.DataFrame,
    dim_sedes: pd.DataFrame,
    columnas: list[str],
) -> pd.DataFrame:
    existentes = set(pd.to_numeric(fixture["match_no"], errors="coerce").dropna().astype(int))
    sedes = dim_sedes.copy()
    sedes["sede_normalizada"] = sedes["estadio"].apply(normalizar_texto)
    sedes_lookup = sedes.set_index("sede_normalizada").to_dict("index")
    fuente_fixture = fixture["fuente_fixture"].dropna().iloc[0] if not fixture.empty else ""
    fuente_fifa = (
        fixture["fuente_verificacion_fifa"].dropna().iloc[0] if not fixture.empty else ""
    )

    filas = []
    for (
        match_no,
        fase,
        ronda,
        fecha_local,
        hora_local,
        fecha_peru,
        hora_peru,
        local,
        visitante,
        ciudad,
        pais_sede,
        estadio,
    ) in PARTIDOS_ELIMINACION_COMPLEMENTARIOS:
        if match_no in existentes:
            continue
        sede = sedes_lookup.get(normalizar_texto(estadio), {})
        filas.append(
            {
                "id_partido": match_no,
                "match_no": match_no,
                "fase": fase,
                "ronda": ronda,
                "grupo": "",
                "fecha_local": fecha_local,
                "hora_local_24h": hora_local,
                "fecha_peru": fecha_peru,
                "hora_peru": hora_peru,
                "id_equipo_local": pd.NA,
                "equipo_local": local,
                "equipo_local_normalizado": normalizar_texto(local),
                "codigo_local": "",
                "id_equipo_visitante": pd.NA,
                "equipo_visitante": visitante,
                "equipo_visitante_normalizado": normalizar_texto(visitante),
                "codigo_visitante": "",
                "id_sede": sede.get("id_sede", pd.NA),
                "ciudad": ciudad,
                "pais_sede": pais_sede,
                "estadio": estadio,
                "sede_normalizada": normalizar_texto(estadio),
                "partido_nombre": f"{local} vs {visitante}",
                "estado": "Programado",
                "resultado": "",
                "goles_local": "",
                "goles_visitante": "",
                "fuente_fixture": fuente_fixture,
                "fuente_verificacion_fifa": fuente_fifa,
                "nota": "Placeholder estructural para completar la llave final de 104 partidos.",
            }
        )

    if filas:
        nuevos = pd.DataFrame(filas, columns=columnas).dropna(axis=1, how="all")
        fixture = pd.concat([fixture, nuevos], ignore_index=True)

    return fixture


def actualizar_cantidad_partidos_sedes(
    dim_sedes: pd.DataFrame,
    fact_fixture: pd.DataFrame,
) -> pd.DataFrame:
    conteo = fact_fixture.groupby("sede_normalizada")["id_partido"].count().to_dict()
    dim_sedes = dim_sedes.copy()
    dim_sedes["sede_normalizada"] = dim_sedes["estadio"].apply(normalizar_texto)
    dim_sedes["cantidad_partidos"] = dim_sedes["sede_normalizada"].map(conteo).fillna(0)
    dim_sedes["cantidad_partidos"] = dim_sedes["cantidad_partidos"].astype("Int64")
    return dim_sedes.drop(columns=["sede_normalizada"])


def crear_fact_fixture(dim_sedes: pd.DataFrame | None = None) -> pd.DataFrame:
    df = cargar_csv("mundial_2026_fixture.csv").copy()
    if dim_sedes is None:
        dim_sedes = crear_dim_sedes()

    for col in ["id_partido", "match_no", "id_equipo_local", "id_equipo_visitante", "id_sede"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    for col in ["fecha_local", "fecha_peru"]:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

    for col in ["resultado", "goles_local", "goles_visitante"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    df["equipo_local_normalizado"] = df["equipo_local"].apply(normalizar_texto)
    df["equipo_visitante_normalizado"] = df["equipo_visitante"].apply(normalizar_texto)
    df["sede_normalizada"] = df["estadio"].apply(normalizar_texto)
    df = corregir_equipos_fixture(df)
    df = asignar_sedes_fixture(df, dim_sedes)

    columnas = [
        "id_partido",
        "match_no",
        "fase",
        "ronda",
        "grupo",
        "fecha_local",
        "hora_local_24h",
        "fecha_peru",
        "hora_peru",
        "id_equipo_local",
        "equipo_local",
        "equipo_local_normalizado",
        "codigo_local",
        "id_equipo_visitante",
        "equipo_visitante",
        "equipo_visitante_normalizado",
        "codigo_visitante",
        "id_sede",
        "ciudad",
        "pais_sede",
        "estadio",
        "sede_normalizada",
        "partido_nombre",
        "estado",
        "resultado",
        "goles_local",
        "goles_visitante",
        "fuente_fixture",
        "fuente_verificacion_fifa",
        "nota",
    ]
    fact_fixture = df[columnas].drop_duplicates(subset=["id_partido"]).sort_values("match_no")
    fact_fixture = completar_fixture_eliminacion(fact_fixture, dim_sedes, columnas)
    for col in ["id_partido", "match_no", "id_equipo_local", "id_equipo_visitante", "id_sede"]:
        fact_fixture[col] = pd.to_numeric(fact_fixture[col], errors="coerce").astype("Int64")
    return fact_fixture.sort_values("match_no").reset_index(drop=True)


def crear_fact_jugadores(dim_selecciones: pd.DataFrame) -> pd.DataFrame:
    df = cargar_csv("mundial_2026_jugadores.csv").copy()
    ids = dim_selecciones[["id_equipo", "codigo_fifa", "seleccion_normalizada"]].copy()

    df["seleccion_normalizada"] = df["seleccion"].apply(normalizar_texto)
    df = df.merge(ids, on=["codigo_fifa", "seleccion_normalizada"], how="left")
    df["posicion_nombre"] = df["posicion"].map(POSICIONES).fillna(df["posicion"])
    df["jugador_nombre_limpio"] = df["bloque_nombre_fifa"].apply(limpiar_nombre_jugador)
    df["club_limpio"] = df["club"].apply(limpiar_club)
    df["pais_club"] = df["club"].apply(extraer_pais_club)
    df["edad"] = df["fecha_nacimiento"].apply(calcular_edad).astype("Int64")
    df["altura_cm"] = pd.to_numeric(df["altura_cm"], errors="coerce").astype("Int64")

    columnas = [
        "id_jugador",
        "id_equipo",
        "seleccion",
        "seleccion_normalizada",
        "codigo_fifa",
        "posicion",
        "posicion_nombre",
        "jugador_nombre_limpio",
        "fecha_nacimiento",
        "edad",
        "club_limpio",
        "pais_club",
        "altura_cm",
        "fuente_jugadores",
    ]
    return df[columnas].drop_duplicates(subset=["id_jugador"]).sort_values("id_jugador")


def crear_dataset_dashboard(
    dim_selecciones: pd.DataFrame,
    fact_jugadores: pd.DataFrame,
    fact_fixture: pd.DataFrame,
) -> pd.DataFrame:
    base = dim_selecciones.copy()

    jugadores_resumen = (
        fact_jugadores.groupby("id_equipo", dropna=False)
        .agg(
            cantidad_jugadores=("id_jugador", "count"),
            edad_promedio=("edad", "mean"),
            altura_promedio=("altura_cm", "mean"),
            arqueros=("posicion", lambda s: (s == "GK").sum()),
            defensas=("posicion", lambda s: (s == "DF").sum()),
            mediocampistas=("posicion", lambda s: (s == "MF").sum()),
            delanteros=("posicion", lambda s: (s == "FW").sum()),
        )
        .reset_index()
    )

    fixture_grupos = fact_fixture[fact_fixture["fase"].eq("Fase de grupos")].copy()

    local = fixture_grupos[["id_partido", "id_equipo_local", "equipo_visitante"]].rename(
        columns={
            "id_equipo_local": "id_equipo",
            "equipo_visitante": "rival",
        }
    )
    visita = fixture_grupos[["id_partido", "id_equipo_visitante", "equipo_local"]].rename(
        columns={
            "id_equipo_visitante": "id_equipo",
            "equipo_local": "rival",
        }
    )
    fixture_largo = pd.concat([local, visita], ignore_index=True)
    fixture_largo = fixture_largo.dropna(subset=["id_equipo"])

    fixture_resumen = (
        fixture_largo.groupby("id_equipo")
        .agg(
            partidos_fixture=("id_partido", "count"),
            rivales_grupo=(
                "rival",
                lambda s: ", ".join(sorted({str(x) for x in s.dropna() if str(x)})),
            ),
        )
        .reset_index()
    )

    dataset = base.merge(jugadores_resumen, on="id_equipo", how="left")
    dataset = dataset.merge(fixture_resumen, on="id_equipo", how="left")

    dataset["cantidad_jugadores"] = dataset["cantidad_jugadores"].fillna(0).astype(int)
    for col in ["arqueros", "defensas", "mediocampistas", "delanteros", "partidos_fixture"]:
        dataset[col] = dataset[col].fillna(0).astype(int)

    dataset["edad_promedio"] = dataset["edad_promedio"].round(1)
    dataset["altura_promedio"] = dataset["altura_promedio"].round(1)
    dataset["rivales_grupo"] = dataset["rivales_grupo"].fillna("")

    return dataset.sort_values(["grupo", "seleccion"]).reset_index(drop=True)


def procesar_mundial() -> dict[str, pd.DataFrame]:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    dim_selecciones = crear_dim_selecciones()
    dim_sedes = crear_dim_sedes()
    fact_fixture = crear_fact_fixture(dim_sedes)
    dim_sedes = actualizar_cantidad_partidos_sedes(dim_sedes, fact_fixture)
    fact_jugadores = crear_fact_jugadores(dim_selecciones)
    dataset_dashboard = crear_dataset_dashboard(
        dim_selecciones,
        fact_jugadores,
        fact_fixture,
    )

    salidas = {
        "dim_selecciones": dim_selecciones,
        "dim_sedes": dim_sedes,
        "fact_fixture": fact_fixture,
        "fact_jugadores": fact_jugadores,
        "dataset_dashboard": dataset_dashboard,
    }

    for nombre, df in salidas.items():
        df.to_csv(PROCESSED_DIR / f"{nombre}.csv", index=False, encoding="utf-8-sig")

    return salidas


def raw_csv_actualizados(archivos_procesados: dict[str, Path]) -> bool:
    raw_files = [
        RAW_DIR / "mundial_2026_equipos.csv",
        RAW_DIR / "mundial_2026_fixture.csv",
        RAW_DIR / "mundial_2026_jugadores.csv",
        RAW_DIR / "mundial_2026_sedes.csv",
    ]
    if not all(path.exists() for path in raw_files):
        return False
    ultimo_raw = max(path.stat().st_mtime for path in raw_files)
    ultimo_procesado = min(path.stat().st_mtime for path in archivos_procesados.values())
    return ultimo_raw > ultimo_procesado


def cargar_o_procesar_mundial() -> dict[str, pd.DataFrame]:
    esperados = {
        "dim_selecciones": PROCESSED_DIR / "dim_selecciones.csv",
        "dim_sedes": PROCESSED_DIR / "dim_sedes.csv",
        "fact_fixture": PROCESSED_DIR / "fact_fixture.csv",
        "fact_jugadores": PROCESSED_DIR / "fact_jugadores.csv",
        "dataset_dashboard": PROCESSED_DIR / "dataset_dashboard.csv",
    }

    if not all(path.exists() for path in esperados.values()) or raw_csv_actualizados(esperados):
        return procesar_mundial()

    return {nombre: pd.read_csv(path) for nombre, path in esperados.items()}


if __name__ == "__main__":
    inicio = datetime.now()
    salidas = procesar_mundial()
    for nombre, df in salidas.items():
        print(f"{nombre}: {df.shape[0]} filas, {df.shape[1]} columnas")
    print(f"Procesamiento terminado en {(datetime.now() - inicio).total_seconds():.2f}s")
