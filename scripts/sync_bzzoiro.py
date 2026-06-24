"""Sincroniza resultados y metricas de Bzzoiro Sports Data hacia SQLite.

Uso:
    python scripts/sync_bzzoiro.py
    python scripts/sync_bzzoiro.py --status inprogress

Lee el token desde .env y actualiza:
    data/mundial_2026/mundialito.db
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from db import DB_PATH, crear_base_datos  # noqa: E402


ENV_PATH = PROJECT_ROOT / ".env"
DEFAULT_BASE_URL = "https://sports.bzzoiro.com/api/v2"
LIVE_STATUSES = {"inprogress", "1st_half", "2nd_half", "halftime", "extratime", "aet", "penalties"}
FINAL_STATUSES = {"finished"}

ALIASES = {
    "usa": "united states",
    "u s a": "united states",
    "bosnia herzegovina": "bosnia and herzegovina",
    "bosnia Herzegovina": "bosnia and herzegovina",
    "czech republic": "czechia",
    "cote d ivoire": "cote d ivoire",
    "ivory coast": "cote d ivoire",
    "curacao": "curacao",
    "dr congo": "congo dr",
    "congo dr": "congo dr",
    "democratic republic of congo": "congo dr",
    "cape verde": "cabo verde",
    "cape verde islands": "cabo verde",
    "south korea": "korea republic",
    "korea republic": "korea republic",
    "turkey": "turkiye",
    "turkiye": "turkiye",
}


def cargar_env() -> dict[str, str]:
    env: dict[str, str] = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def normalizar(valor: object) -> str:
    texto = "" if valor is None else str(valor).strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"[^a-zA-Z0-9]+", " ", texto).lower()
    texto = re.sub(r"\s+", " ", texto).strip()
    return ALIASES.get(texto, texto)


def estado_visual(status: object) -> str:
    status_norm = str(status or "").lower()
    if status_norm in LIVE_STATUSES:
        return "En vivo"
    if status_norm in FINAL_STATUSES:
        return "Finalizado"
    if status_norm in {"cancelled", "postponed"}:
        return status_norm.title()
    return "Programado"


def json_text(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def nullable_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def nullable_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def nested_float(stats: dict[str, Any], *keys: str) -> float | None:
    current: Any = stats
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return nullable_float(current)


def first_value(stats: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in stats and stats.get(key) not in (None, ""):
            return stats.get(key)
    return None


def asegurar_columna(conexion: sqlite3.Connection, tabla: str, columna: str, tipo: str) -> None:
    columnas = {row[1] for row in conexion.execute(f"PRAGMA table_info({tabla})")}
    if columna not in columnas:
        conexion.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")


def asegurar_esquema(conexion: sqlite3.Connection) -> None:
    conexion.executescript(
        """
        CREATE TABLE IF NOT EXISTS bzzoiro_eventos (
            id_partido INTEGER PRIMARY KEY,
            api_event_id TEXT UNIQUE NOT NULL,
            league_id INTEGER,
            season_id INTEGER,
            home_team_id INTEGER,
            away_team_id INTEGER,
            status TEXT,
            raw_event_json TEXT,
            stats_json TEXT,
            incidents_json TEXT,
            lineups_json TEXT,
            sincronizado_en TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_partido) REFERENCES partidos(id_partido) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_bzzoiro_eventos_api
            ON bzzoiro_eventos(api_event_id);
        """
    )
    for columna, tipo in [
        ("xg", "REAL"),
        ("tiros_fuera", "INTEGER"),
        ("tiros_bloqueados", "INTEGER"),
        ("tiros_area", "INTEGER"),
        ("tiros_fuera_area", "INTEGER"),
        ("poste", "INTEGER"),
        ("ataques", "INTEGER"),
        ("ataques_peligrosos", "INTEGER"),
        ("raw_stats_json", "TEXT"),
    ]:
        asegurar_columna(conexion, "estadisticas_partido", columna, tipo)


def abrir_db() -> sqlite3.Connection:
    if not DB_PATH.exists():
        crear_base_datos(recrear=False)
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    asegurar_esquema(conexion)
    return conexion


def partidos_locales(conexion: sqlite3.Connection) -> list[sqlite3.Row]:
    return conexion.execute(
        """
        SELECT
            p.id_partido,
            p.match_no,
            p.equipo_local_id,
            p.equipo_visitante_id,
            COALESCE(sl.seleccion, p.local_pendiente) AS equipo_local,
            COALESCE(sv.seleccion, p.visitante_pendiente) AS equipo_visitante,
            p.fecha_hora_peru
        FROM partidos p
        LEFT JOIN selecciones sl ON sl.id_equipo = p.equipo_local_id
        LEFT JOIN selecciones sv ON sv.id_equipo = p.equipo_visitante_id
        ORDER BY p.match_no
        """
    ).fetchall()


def indexar_partidos(rows: list[sqlite3.Row]) -> tuple[dict[tuple[str, str], list[sqlite3.Row]], dict[frozenset[str], list[sqlite3.Row]]]:
    exactos: dict[tuple[str, str], list[sqlite3.Row]] = {}
    por_par: dict[frozenset[str], list[sqlite3.Row]] = {}
    for row in rows:
        home = normalizar(row["equipo_local"])
        away = normalizar(row["equipo_visitante"])
        exactos.setdefault((home, away), []).append(row)
        por_par.setdefault(frozenset({home, away}), []).append(row)
    return exactos, por_par


def elegir_match(
    event: dict[str, Any],
    exactos: dict[tuple[str, str], list[sqlite3.Row]],
    por_par: dict[frozenset[str], list[sqlite3.Row]],
) -> tuple[sqlite3.Row | None, bool]:
    home = normalizar(event.get("home_team"))
    away = normalizar(event.get("away_team"))
    candidatos = exactos.get((home, away), [])
    invertido = False
    if not candidatos:
        candidatos = exactos.get((away, home), [])
        invertido = bool(candidatos)
    if not candidatos:
        candidatos = por_par.get(frozenset({home, away}), [])
        invertido = bool(candidatos and normalizar(candidatos[0]["equipo_local"]) != home)
    if not candidatos:
        return None, False
    if len(candidatos) == 1:
        return candidatos[0], invertido
    event_date = str(event.get("event_date") or "")[:10]
    for row in candidatos:
        if str(row["fecha_hora_peru"] or "")[:10] == event_date:
            return row, invertido
    return candidatos[0], invertido


def api_get(session: requests.Session, base_url: str, path: str, params: dict[str, Any] | None = None) -> Any:
    url = f"{base_url.rstrip('/')}/{path.strip('/')}/"
    response = session.get(url, params=params or {}, timeout=40)
    response.raise_for_status()
    return response.json()


def eventos_api(session: requests.Session, env: dict[str, str], status: str | None = None) -> list[dict[str, Any]]:
    base_url = env.get("BZZOIRO_API_BASE", DEFAULT_BASE_URL)
    params: dict[str, Any] = {
        "league_id": int(env.get("BZZOIRO_WORLD_CUP_LEAGUE_ID", "27")),
        "season_id": int(env.get("BZZOIRO_WORLD_CUP_SEASON_ID", "188")),
        "date_from": env.get("BZZOIRO_WORLD_CUP_DATE_FROM", "2026-06-11"),
        "date_to": env.get("BZZOIRO_WORLD_CUP_DATE_TO", "2026-07-19"),
        "limit": 200,
        "offset": 0,
    }
    if status:
        params["status"] = status
    eventos: list[dict[str, Any]] = []
    while True:
        payload = api_get(session, base_url, "events", params)
        page = payload.get("results", payload if isinstance(payload, list) else [])
        eventos.extend(page)
        if not payload.get("next") or len(page) == 0:
            break
        params["offset"] += params["limit"]
    return eventos


def eventos_live(session: requests.Session, env: dict[str, str]) -> list[dict[str, Any]]:
    base_url = env.get("BZZOIRO_API_BASE", DEFAULT_BASE_URL)
    payload = api_get(
        session,
        base_url,
        "events/live",
        {
            "league_id": int(env.get("BZZOIRO_WORLD_CUP_LEAGUE_ID", "27")),
            "season_id": int(env.get("BZZOIRO_WORLD_CUP_SEASON_ID", "188")),
        },
    )
    return payload.get("events", payload if isinstance(payload, list) else [])


def guardar_partido(conexion: sqlite3.Connection, match: sqlite3.Row, event: dict[str, Any], invertido: bool) -> None:
    home_score = event.get("away_score") if invertido else event.get("home_score")
    away_score = event.get("home_score") if invertido else event.get("away_score")
    home_ht = event.get("away_score_ht") if invertido else event.get("home_score_ht")
    away_ht = event.get("home_score_ht") if invertido else event.get("away_score_ht")
    weather = event.get("weather")
    conexion.execute(
        """
        UPDATE partidos
        SET
            api_id = ?,
            estado = ?,
            goles_local = COALESCE(?, goles_local),
            goles_visitante = COALESCE(?, goles_visitante),
            goles_local_descanso = COALESCE(?, goles_local_descanso),
            goles_visitante_descanso = COALESCE(?, goles_visitante_descanso),
            minuto_actual = ?,
            periodo = ?,
            fecha_hora_utc = COALESCE(?, fecha_hora_utc),
            clima = ?,
            asistencia = COALESCE(?, asistencia),
            fuente = 'Bzzoiro Sports Data',
            actualizado_en = CURRENT_TIMESTAMP
        WHERE id_partido = ?
        """,
        (
            str(event.get("id")),
            estado_visual(event.get("status")),
            nullable_int(home_score),
            nullable_int(away_score),
            nullable_int(home_ht),
            nullable_int(away_ht),
            nullable_int(event.get("current_minute")),
            event.get("period"),
            event.get("event_date"),
            json_text(weather) if weather else None,
            nullable_int(event.get("attendance")),
            match["id_partido"],
        ),
    )


def guardar_metricas_equipo(
    conexion: sqlite3.Connection,
    id_partido: int,
    id_equipo: int | None,
    stats: dict[str, Any],
) -> None:
    if id_equipo is None:
        return
    valores = {
        "posesion": first_value(stats, ["ball_possession", "possession", "possession_pct"]),
        "tiros": first_value(stats, ["total_shots", "shots"]),
        "tiros_puerta": first_value(stats, ["shots_on_target", "on_target"]),
        "corners": first_value(stats, ["corners", "corner_kicks"]),
        "faltas": first_value(stats, ["fouls"]),
        "fueras_juego": first_value(stats, ["offsides", "fueras_juego"]),
        "tarjetas_amarillas": first_value(stats, ["yellow_cards", "cards_yellow"]),
        "tarjetas_rojas": first_value(stats, ["red_cards", "cards_red"]),
        "pases": first_value(stats, ["passes", "total_passes"]),
        "pases_correctos": first_value(stats, ["accurate_passes", "passes_accurate"]),
        "precision_pases": first_value(stats, ["pass_accuracy_pct", "accurate_passes_pct"]),
        "atajadas": first_value(stats, ["saves", "goalkeeper_saves"]),
        "xg": nested_float(stats, "xg", "actual") if isinstance(stats.get("xg"), dict) else first_value(stats, ["xg"]),
        "tiros_fuera": first_value(stats, ["shots_off_target"]),
        "tiros_bloqueados": first_value(stats, ["blocked_shots"]),
        "tiros_area": first_value(stats, ["shots_inside_box"]),
        "tiros_fuera_area": first_value(stats, ["shots_outside_box"]),
        "poste": first_value(stats, ["hit_woodwork"]),
        "ataques": first_value(stats, ["attacks"]),
        "ataques_peligrosos": first_value(stats, ["dangerous_attacks"]),
    }
    conexion.execute(
        """
        INSERT INTO estadisticas_partido (
            id_partido, id_equipo, posesion, tiros, tiros_puerta, corners,
            faltas, fueras_juego, tarjetas_amarillas, tarjetas_rojas, pases,
            pases_correctos, precision_pases, atajadas, xg, tiros_fuera,
            tiros_bloqueados, tiros_area, tiros_fuera_area, poste, ataques,
            ataques_peligrosos, raw_stats_json, actualizado_en
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id_partido, id_equipo) DO UPDATE SET
            posesion = excluded.posesion,
            tiros = excluded.tiros,
            tiros_puerta = excluded.tiros_puerta,
            corners = excluded.corners,
            faltas = excluded.faltas,
            fueras_juego = excluded.fueras_juego,
            tarjetas_amarillas = excluded.tarjetas_amarillas,
            tarjetas_rojas = excluded.tarjetas_rojas,
            pases = excluded.pases,
            pases_correctos = excluded.pases_correctos,
            precision_pases = excluded.precision_pases,
            atajadas = excluded.atajadas,
            xg = excluded.xg,
            tiros_fuera = excluded.tiros_fuera,
            tiros_bloqueados = excluded.tiros_bloqueados,
            tiros_area = excluded.tiros_area,
            tiros_fuera_area = excluded.tiros_fuera_area,
            poste = excluded.poste,
            ataques = excluded.ataques,
            ataques_peligrosos = excluded.ataques_peligrosos,
            raw_stats_json = excluded.raw_stats_json,
            actualizado_en = CURRENT_TIMESTAMP
        """,
        (
            id_partido,
            id_equipo,
            nullable_float(valores["posesion"]),
            nullable_int(valores["tiros"]),
            nullable_int(valores["tiros_puerta"]),
            nullable_int(valores["corners"]),
            nullable_int(valores["faltas"]),
            nullable_int(valores["fueras_juego"]),
            nullable_int(valores["tarjetas_amarillas"]),
            nullable_int(valores["tarjetas_rojas"]),
            nullable_int(valores["pases"]),
            nullable_int(valores["pases_correctos"]),
            nullable_float(valores["precision_pases"]),
            nullable_int(valores["atajadas"]),
            nullable_float(valores["xg"]),
            nullable_int(valores["tiros_fuera"]),
            nullable_int(valores["tiros_bloqueados"]),
            nullable_int(valores["tiros_area"]),
            nullable_int(valores["tiros_fuera_area"]),
            nullable_int(valores["poste"]),
            nullable_int(valores["ataques"]),
            nullable_int(valores["ataques_peligrosos"]),
            json_text(stats),
        ),
    )


def guardar_estadisticas(
    conexion: sqlite3.Connection,
    match: sqlite3.Row,
    stats_payload: dict[str, Any] | None,
    invertido: bool,
) -> None:
    if not stats_payload:
        return
    stats = stats_payload.get("stats") or {}
    home_stats = stats.get("away" if invertido else "home") or {}
    away_stats = stats.get("home" if invertido else "away") or {}
    guardar_metricas_equipo(conexion, match["id_partido"], match["equipo_local_id"], home_stats)
    guardar_metricas_equipo(conexion, match["id_partido"], match["equipo_visitante_id"], away_stats)


def guardar_incidentes(
    conexion: sqlite3.Connection,
    match: sqlite3.Row,
    incidents_payload: dict[str, Any] | None,
    event: dict[str, Any],
    invertido: bool,
) -> None:
    if not incidents_payload:
        return
    incidents = incidents_payload.get("incidents") or []
    conexion.execute(
        "DELETE FROM eventos_partido WHERE id_partido = ? AND api_id LIKE 'bzzoiro:%'",
        (match["id_partido"],),
    )
    home_api = event.get("home_team_id")
    away_api = event.get("away_team_id")
    for idx, item in enumerate(incidents):
        team_api = item.get("team_id")
        id_equipo = None
        if team_api == home_api:
            id_equipo = match["equipo_visitante_id"] if invertido else match["equipo_local_id"]
        elif team_api == away_api:
            id_equipo = match["equipo_local_id"] if invertido else match["equipo_visitante_id"]
        tipo = str(item.get("type") or item.get("incident_type") or "evento")
        detalle = item.get("text") or item.get("detail") or item.get("player_name") or tipo
        minuto = nullable_int(item.get("minute"))
        api_id = f"bzzoiro:{event.get('id')}:{idx}:{tipo}:{minuto}:{normalizar(detalle)[:24]}"
        conexion.execute(
            """
            INSERT INTO eventos_partido (
                api_id, id_partido, id_equipo, tipo, detalle, minuto, periodo
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(api_id) DO UPDATE SET
                id_equipo = excluded.id_equipo,
                tipo = excluded.tipo,
                detalle = excluded.detalle,
                minuto = excluded.minuto,
                periodo = excluded.periodo
            """,
            (api_id, match["id_partido"], id_equipo, tipo, str(detalle), minuto, item.get("period")),
        )


def upsert_bzzoiro_evento(
    conexion: sqlite3.Connection,
    match: sqlite3.Row,
    event: dict[str, Any],
    stats_payload: dict[str, Any] | None,
    incidents_payload: dict[str, Any] | None,
    lineups_payload: dict[str, Any] | None,
) -> None:
    conexion.execute(
        """
        INSERT INTO bzzoiro_eventos (
            id_partido, api_event_id, league_id, season_id, home_team_id,
            away_team_id, status, raw_event_json, stats_json, incidents_json,
            lineups_json, sincronizado_en
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id_partido) DO UPDATE SET
            api_event_id = excluded.api_event_id,
            league_id = excluded.league_id,
            season_id = excluded.season_id,
            home_team_id = excluded.home_team_id,
            away_team_id = excluded.away_team_id,
            status = excluded.status,
            raw_event_json = excluded.raw_event_json,
            stats_json = COALESCE(excluded.stats_json, bzzoiro_eventos.stats_json),
            incidents_json = COALESCE(excluded.incidents_json, bzzoiro_eventos.incidents_json),
            lineups_json = COALESCE(excluded.lineups_json, bzzoiro_eventos.lineups_json),
            sincronizado_en = CURRENT_TIMESTAMP
        """,
        (
            match["id_partido"],
            str(event.get("id")),
            nullable_int(event.get("league_id")),
            nullable_int(event.get("season_id")),
            nullable_int(event.get("home_team_id")),
            nullable_int(event.get("away_team_id")),
            event.get("status"),
            json_text(event),
            json_text(stats_payload) if stats_payload else None,
            json_text(incidents_payload) if incidents_payload else None,
            json_text(lineups_payload) if lineups_payload else None,
        ),
    )


def sincronizar(status: str | None = None, incluir_detalle_programados: bool = False) -> dict[str, int]:
    env = cargar_env()
    token = env.get("BZZOIRO_API_TOKEN")
    if not token:
        raise RuntimeError("Falta BZZOIRO_API_TOKEN en .env")
    base_url = env.get("BZZOIRO_API_BASE", DEFAULT_BASE_URL)
    headers = {"Authorization": f"Token {token}"}
    session = requests.Session()
    session.headers.update(headers)

    inicio = datetime.now(timezone.utc).isoformat(timespec="seconds")
    recibidos = guardados = con_metricas = sin_match = 0

    with abrir_db() as conexion:
        conexion.execute(
            """
            INSERT INTO sincronizaciones_api (
                proveedor, recurso, iniciado_en, estado
            ) VALUES (?, ?, ?, ?)
            """,
            ("Bzzoiro Sports Data", "world_cup_2026", inicio, "en_proceso"),
        )
        sync_id = conexion.execute("SELECT last_insert_rowid()").fetchone()[0]
        exactos, por_par = indexar_partidos(partidos_locales(conexion))

        events = eventos_api(session, env, status)
        live_by_id = {str(event.get("id")): event for event in eventos_live(session, env)}
        for event_id, event in live_by_id.items():
            if not any(str(item.get("id")) == event_id for item in events):
                events.append(event)

        recibidos = len(events)
        vistos: set[str] = set()
        for event in events:
            api_event_id = str(event.get("id"))
            if api_event_id in vistos:
                continue
            vistos.add(api_event_id)
            match, invertido = elegir_match(event, exactos, por_par)
            if match is None:
                sin_match += 1
                continue

            guardar_partido(conexion, match, event, invertido)

            status_norm = str(event.get("status") or "").lower()
            debe_pedir_detalle = (
                incluir_detalle_programados
                or status_norm in LIVE_STATUSES
                or status_norm in FINAL_STATUSES
            )
            stats_payload = incidents_payload = lineups_payload = None
            if debe_pedir_detalle:
                try:
                    stats_payload = api_get(session, base_url, f"events/{api_event_id}/stats")
                    incidents_payload = api_get(session, base_url, f"events/{api_event_id}/incidents")
                    lineups_payload = api_get(session, base_url, f"events/{api_event_id}/lineups")
                    guardar_estadisticas(conexion, match, stats_payload, invertido)
                    guardar_incidentes(conexion, match, incidents_payload, event, invertido)
                    con_metricas += 1
                except requests.HTTPError:
                    stats_payload = incidents_payload = lineups_payload = None

            upsert_bzzoiro_evento(
                conexion,
                match,
                event,
                stats_payload,
                incidents_payload,
                lineups_payload,
            )
            guardados += 1

        final = datetime.now(timezone.utc).isoformat(timespec="seconds")
        conexion.execute(
            """
            UPDATE sincronizaciones_api
            SET finalizado_en = ?, estado = ?, registros_recibidos = ?,
                registros_guardados = ?, mensaje_error = ?
            WHERE id_sincronizacion = ?
            """,
            (
                final,
                "completado",
                recibidos,
                guardados,
                f"sin_match={sin_match}; con_metricas={con_metricas}",
                sync_id,
            ),
        )
        conexion.commit()

    return {
        "eventos_recibidos": recibidos,
        "partidos_actualizados": guardados,
        "partidos_con_metricas": con_metricas,
        "sin_match_local": sin_match,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Sincroniza BSD/Bzzoiro con SQLite.")
    parser.add_argument(
        "--status",
        choices=["notstarted", "inprogress", "finished", "cancelled", "postponed"],
        help="Filtra por estado de la API.",
    )
    parser.add_argument(
        "--detalle-programados",
        action="store_true",
        help="Tambien intenta descargar lineups/metadata para partidos no iniciados.",
    )
    args = parser.parse_args()
    resumen = sincronizar(args.status, args.detalle_programados)
    for key, value in resumen.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
