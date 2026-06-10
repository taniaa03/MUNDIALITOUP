from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd

from mundial_processing import cargar_o_procesar_mundial


ALIASES_RENDIMIENTO = {
    "cabo verde": "cape verde islands",
    "czechia": "czech republic",
    "cote d ivoire": "ivory coast",
    "curacao": "curacao",
    "turkiye": "turkey",
    "united states": "usa",
    "korea republic": "south korea",
}

STADIUM_FALLBACKS = {
    "Estadio Azteca": {
        "estadio": "Estadio Azteca",
        "ciudad": "Mexico City",
        "pais": "Mexico",
        "capacidad_aprox": 87523,
        "cantidad_partidos": 5,
    }
}


def normalizar_texto(valor: object) -> str:
    texto = "" if pd.isna(valor) else str(valor).strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"[^a-zA-Z0-9]+", " ", texto).lower()
    return re.sub(r"\s+", " ", texto).strip()


def cargar_datos(project_root: Path) -> dict[str, pd.DataFrame]:
    datos = cargar_o_procesar_mundial()
    equipos_path = project_root / "data" / "processed" / "equipos_procesado.csv"
    enfrentamientos_path = project_root / "data" / "processed" / "enfrentamientos_procesado.csv"
    datos["rendimiento_companero"] = (
        pd.read_csv(equipos_path) if equipos_path.exists() else pd.DataFrame()
    )
    datos["enfrentamientos_companero"] = (
        pd.read_csv(enfrentamientos_path) if enfrentamientos_path.exists() else pd.DataFrame()
    )
    return datos


def resumen_torneo(
    equipos: pd.DataFrame,
    jugadores: pd.DataFrame,
    fixture: pd.DataFrame,
    sedes: pd.DataFrame,
) -> dict[str, int]:
    return {
        "selecciones": int(equipos["seleccion"].nunique()),
        "jugadores": int(jugadores["id_jugador"].nunique()),
        "partidos": int(fixture["match_no"].nunique()),
        "sedes": int(max(sedes["estadio"].nunique(), fixture["estadio"].nunique())),
    }


def opciones_filtros(
    fixture: pd.DataFrame,
    equipos: pd.DataFrame,
) -> dict[str, list[str]]:
    return {
        "grupos": ["Todos"] + sorted(fixture["grupo"].dropna().unique().tolist()),
        "paises": ["Todos"] + sorted(equipos["seleccion"].dropna().unique().tolist()),
        "fechas": ["Todas"] + sorted(fixture["fecha_peru"].dropna().unique().tolist()),
        "ciudades": ["Todas"] + sorted(fixture["ciudad"].dropna().unique().tolist()),
        "estadios": ["Todos"] + sorted(fixture["estadio"].dropna().unique().tolist()),
        "fases": ["Todas"] + sorted(fixture["fase"].dropna().unique().tolist()),
    }


def filtrar_fixture(
    fixture: pd.DataFrame,
    grupo: str = "Todos",
    pais: str = "Todos",
    fecha: str = "Todas",
    ciudad: str = "Todas",
    estadio: str = "Todos",
    fase: str = "Todas",
) -> pd.DataFrame:
    df = fixture.copy()
    if grupo != "Todos":
        df = df[df["grupo"].fillna("") == grupo]
    if pais != "Todos":
        df = df[(df["equipo_local"] == pais) | (df["equipo_visitante"] == pais)]
    if fecha != "Todas":
        df = df[df["fecha_peru"] == fecha]
    if ciudad != "Todas":
        df = df[df["ciudad"] == ciudad]
    if estadio != "Todos":
        df = df[df["estadio"] == estadio]
    if fase != "Todas":
        df = df[df["fase"] == fase]
    return df.sort_values("match_no")


def proximos_partidos(fixture: pd.DataFrame, limit: int = 4) -> pd.DataFrame:
    return fixture.sort_values(["fecha_peru", "match_no"]).head(limit).copy()


def grupos_torneo(equipos: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
    return list(equipos.sort_values(["grupo", "seleccion"]).groupby("grupo"))


def get_match(fixture: pd.DataFrame, match_no: int | None) -> pd.Series:
    if match_no is not None:
        found = fixture[fixture["match_no"].astype(int) == int(match_no)]
        if not found.empty:
            return found.iloc[0]
    return fixture.sort_values("match_no").iloc[0]


def get_team(equipos: pd.DataFrame, seleccion: str) -> pd.Series:
    found = equipos[equipos["seleccion"] == seleccion]
    if not found.empty:
        return found.iloc[0]
    return pd.Series(
        {
            "seleccion": seleccion,
            "codigo_fifa": "",
            "confederacion": "-",
            "grupo": "-",
            "cantidad_jugadores": 0,
            "edad_promedio": 0,
            "altura_promedio": 0,
            "arqueros": 0,
            "defensas": 0,
            "mediocampistas": 0,
            "delanteros": 0,
            "partidos_fixture": 0,
            "rivales_grupo": "-",
        }
    )


def get_stadium(sedes: pd.DataFrame, estadio: str, fixture: pd.DataFrame | None = None) -> pd.Series:
    found = sedes[sedes["estadio"] == estadio]
    if not found.empty:
        return found.iloc[0]
    if estadio in STADIUM_FALLBACKS:
        return pd.Series(STADIUM_FALLBACKS[estadio])
    fixture_row = pd.Series(dtype=object)
    if fixture is not None:
        matches = fixture[fixture["estadio"] == estadio]
        if not matches.empty:
            fixture_row = matches.iloc[0]
    return pd.Series(
        {
            "estadio": estadio,
            "ciudad": fixture_row.get("ciudad", ""),
            "pais": fixture_row.get("pais_sede", ""),
            "capacidad_aprox": "",
            "cantidad_partidos": len(fixture[fixture["estadio"] == estadio]) if fixture is not None else "",
        }
    )


def fixture_por_equipo(fixture: pd.DataFrame, seleccion: str) -> pd.DataFrame:
    return fixture[
        (fixture["equipo_local"] == seleccion) | (fixture["equipo_visitante"] == seleccion)
    ].sort_values("match_no")


def fixture_por_estadio(fixture: pd.DataFrame, estadio: str) -> pd.DataFrame:
    return fixture[fixture["estadio"] == estadio].sort_values("match_no")


def fixture_por_ciudad(fixture: pd.DataFrame, ciudad: str) -> pd.DataFrame:
    return fixture[fixture["ciudad"] == ciudad].sort_values("match_no")


def jugadores_por_equipo(jugadores: pd.DataFrame, seleccion: str) -> pd.DataFrame:
    return jugadores[jugadores["seleccion"] == seleccion].sort_values(
        ["posicion", "jugador_nombre_limpio"]
    )


def clubes_por_seleccion(jugadores: pd.DataFrame, seleccion: str, limit: int = 5) -> pd.DataFrame:
    df = jugadores[jugadores["seleccion"] == seleccion]
    if df.empty:
        return pd.DataFrame(columns=["club_limpio", "jugadores"])
    return (
        df.groupby("club_limpio", dropna=False)
        .agg(jugadores=("id_jugador", "count"))
        .reset_index()
        .sort_values(["jugadores", "club_limpio"], ascending=[False, True])
        .head(limit)
    )


def candidatos_equipo(nombre: str) -> set[str]:
    base = normalizar_texto(nombre)
    candidatos = {base}
    alias = ALIASES_RENDIMIENTO.get(base)
    if alias:
        candidatos.add(alias)
    for key, value in ALIASES_RENDIMIENTO.items():
        if value == base:
            candidatos.add(key)
    return {item for item in candidatos if item}


def _coincide_equipo(valor: object, candidatos: set[str]) -> bool:
    texto = normalizar_texto(valor)
    return any(candidato == texto or candidato in texto for candidato in candidatos)


def rendimiento_equipo(nombre: str, rendimiento: pd.DataFrame) -> dict[str, str]:
    if rendimiento.empty:
        return {}
    objetivo = ALIASES_RENDIMIENTO.get(normalizar_texto(nombre), normalizar_texto(nombre))
    df = rendimiento.copy()
    for col in ["team_name", "common_name", "country"]:
        if col not in df.columns:
            df[col] = ""
    mask = (
        df["team_name"].apply(normalizar_texto).str.contains(objetivo, regex=False, na=False)
        | df["common_name"].apply(normalizar_texto).str.contains(objetivo, regex=False, na=False)
        | df["country"].apply(normalizar_texto).eq(objetivo)
    )
    if not mask.any():
        return {}
    row = df[mask].iloc[0]
    return {
        "PPG": _fmt(row.get("points_per_game", "")),
        "GF/P": _fmt(row.get("goals_scored_per_match", "")),
        "GC/P": _fmt(row.get("goals_conceded_per_match", "")),
        "Victorias": _fmt(row.get("wins", "")),
    }


def historial_equipo(
    nombre: str,
    enfrentamientos: pd.DataFrame,
    limit: int = 4,
) -> list[dict[str, str]]:
    if enfrentamientos.empty:
        return []
    candidatos = candidatos_equipo(nombre)
    if not {"home_team_name", "away_team_name"}.issubset(enfrentamientos.columns):
        return []
    mask = enfrentamientos["home_team_name"].apply(
        lambda value: _coincide_equipo(value, candidatos)
    ) | enfrentamientos["away_team_name"].apply(lambda value: _coincide_equipo(value, candidatos))
    df = enfrentamientos[mask].copy()
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp", ascending=False)
    items: list[dict[str, str]] = []
    for _, row in df.head(limit).iterrows():
        es_local = _coincide_equipo(row.get("home_team_name", ""), candidatos)
        rival = row.get("away_team_name" if es_local else "home_team_name", "-")
        gf = row.get("home_team_goal_count" if es_local else "away_team_goal_count", "-")
        gc = row.get("away_team_goal_count" if es_local else "home_team_goal_count", "-")
        estado = "Empate"
        clase = "draw"
        try:
            favor = int(float(gf))
            contra = int(float(gc))
            if favor > contra:
                estado, clase = "Gano", "win"
            elif favor < contra:
                estado, clase = "Cayo", "loss"
        except (TypeError, ValueError):
            pass
        items.append(
            {
                "estado": estado,
                "clase": clase,
                "marcador": f"{_fmt(gf)}-{_fmt(gc)}",
                "rival": str(rival),
                "competencia": str(row.get("competici_n", "")),
            }
        )
    return items


def busqueda_global(
    query: str,
    equipos: pd.DataFrame,
    jugadores: pd.DataFrame,
    fixture: pd.DataFrame,
    sedes: pd.DataFrame,
    limit: int = 5,
) -> dict[str, list[dict[str, Any]]]:
    q = normalizar_texto(query)
    if not q:
        return {"equipos": [], "jugadores": [], "partidos": [], "sedes": []}
    equipos_mask = _contains(equipos["seleccion"], q) | _contains(equipos["confederacion"], q)
    jugadores_mask = (
        _contains(jugadores["jugador_nombre_limpio"], q)
        | _contains(jugadores["club_limpio"], q)
        | _contains(jugadores["seleccion"], q)
    )
    partidos_mask = (
        _contains(fixture["equipo_local"], q)
        | _contains(fixture["equipo_visitante"], q)
        | _contains(fixture["ciudad"], q)
        | _contains(fixture["estadio"], q)
        | _contains(fixture["fase"], q)
    )
    sedes_mask = (
        _contains(sedes["ciudad"], q)
        | _contains(sedes["estadio"], q)
        | _contains(sedes["pais"], q)
    )
    return {
        "equipos": equipos[equipos_mask].head(limit).to_dict("records"),
        "jugadores": jugadores[jugadores_mask].head(limit).to_dict("records"),
        "partidos": fixture[partidos_mask].head(limit).to_dict("records"),
        "sedes": sedes[sedes_mask].head(limit).to_dict("records"),
    }


def _contains(series: pd.Series, query: str) -> pd.Series:
    return series.fillna("").apply(normalizar_texto).str.contains(query, regex=False, na=False)


def _fmt(value: object) -> str:
    if pd.isna(value) or value == "":
        return "-"
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)
