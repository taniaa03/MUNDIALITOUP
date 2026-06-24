"""Consultas SQL del Mundial 2026 mostradas directamente en la consola."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "mundial_2026" / "mundialito.db"


CONSULTA_EQUIPOS_MAS_GOLEADORES = """
WITH goles_por_equipo AS (
    SELECT equipo_local_id AS id_equipo, goles_local AS goles
    FROM partidos
    WHERE goles_local IS NOT NULL

    UNION ALL

    SELECT equipo_visitante_id AS id_equipo, goles_visitante AS goles
    FROM partidos
    WHERE goles_visitante IS NOT NULL
)
SELECT
    s.seleccion AS equipo,
    s.grupo,
    COUNT(*) AS partidos_con_resultado,
    SUM(g.goles) AS goles_totales
FROM goles_por_equipo AS g
JOIN selecciones AS s
    ON s.id_equipo = g.id_equipo
GROUP BY s.id_equipo, s.seleccion, s.grupo
ORDER BY goles_totales DESC, partidos_con_resultado ASC, equipo ASC
LIMIT 10;
"""


CONSULTA_TOP_GOLEADORES = """
WITH goles AS (
    SELECT
        CAST(json_extract(incidente.value, '$.player_id') AS TEXT) AS jugador_id,
        json_extract(incidente.value, '$.player') AS jugador,
        CASE
            WHEN json_extract(incidente.value, '$.is_home') = 1
                THEN json_extract(evento.raw_event_json, '$.home_team')
            ELSE json_extract(evento.raw_event_json, '$.away_team')
        END AS equipo
    FROM bzzoiro_eventos AS evento
    JOIN json_each(
        evento.incidents_json,
        '$.incidents'
    ) AS incidente
    WHERE json_valid(evento.incidents_json)
      AND json_extract(incidente.value, '$.type') = 'goal'
      AND json_extract(incidente.value, '$.player') IS NOT NULL
)
SELECT
    jugador,
    equipo,
    COUNT(*) AS goles
FROM goles
GROUP BY jugador_id, jugador, equipo
ORDER BY goles DESC, jugador ASC
LIMIT 10;
"""


CONSULTA_TOP_PUNTAJE_FASE_GRUPOS = """
WITH resultados_por_equipo AS (
    SELECT
        p.grupo,
        p.equipo_local_id AS id_equipo,
        p.goles_local AS goles_favor,
        p.goles_visitante AS goles_contra
    FROM partidos AS p
    WHERE p.grupo IS NOT NULL
      AND TRIM(p.grupo) <> ''
      AND p.goles_local IS NOT NULL
      AND p.goles_visitante IS NOT NULL

    UNION ALL

    SELECT
        p.grupo,
        p.equipo_visitante_id AS id_equipo,
        p.goles_visitante AS goles_favor,
        p.goles_local AS goles_contra
    FROM partidos AS p
    WHERE p.grupo IS NOT NULL
      AND TRIM(p.grupo) <> ''
      AND p.goles_local IS NOT NULL
      AND p.goles_visitante IS NOT NULL
),
tabla AS (
    SELECT
        grupo,
        id_equipo,
        COUNT(*) AS partidos_jugados,
        SUM(CASE WHEN goles_favor > goles_contra THEN 1 ELSE 0 END) AS ganados,
        SUM(CASE WHEN goles_favor = goles_contra THEN 1 ELSE 0 END) AS empatados,
        SUM(CASE WHEN goles_favor < goles_contra THEN 1 ELSE 0 END) AS perdidos,
        SUM(goles_favor) AS goles_favor,
        SUM(goles_contra) AS goles_contra,
        SUM(goles_favor - goles_contra) AS diferencia_goles,
        SUM(
            CASE
                WHEN goles_favor > goles_contra THEN 3
                WHEN goles_favor = goles_contra THEN 1
                ELSE 0
            END
        ) AS puntos
    FROM resultados_por_equipo
    GROUP BY grupo, id_equipo
)
SELECT
    tabla.grupo,
    seleccion.seleccion AS equipo,
    tabla.partidos_jugados,
    tabla.ganados,
    tabla.empatados,
    tabla.perdidos,
    tabla.goles_favor,
    tabla.goles_contra,
    tabla.diferencia_goles,
    tabla.puntos
FROM tabla
JOIN selecciones AS seleccion
    ON seleccion.id_equipo = tabla.id_equipo
ORDER BY
    tabla.puntos DESC,
    tabla.diferencia_goles DESC,
    tabla.goles_favor DESC,
    equipo ASC
LIMIT 10;
"""


def ejecutar_consulta(
    conexion: sqlite3.Connection,
    consulta: str,
) -> tuple[list[str], list[sqlite3.Row]]:
    cursor = conexion.execute(consulta)
    columnas = [descripcion[0] for descripcion in cursor.description]
    return columnas, cursor.fetchall()


def imprimir_tabla(
    titulo: str,
    columnas: Sequence[str],
    filas: Sequence[sqlite3.Row],
) -> None:
    print(f"\n{titulo}")
    print("=" * len(titulo))

    if not filas:
        print("No se encontraron resultados.")
        return

    valores = [
        ["" if valor is None else str(valor) for valor in fila]
        for fila in filas
    ]
    anchos = [
        max(len(str(columna)), *(len(fila[indice]) for fila in valores))
        for indice, columna in enumerate(columnas)
    ]

    formato = " | ".join(f"{{:<{ancho}}}" for ancho in anchos)
    separador = "-+-".join("-" * ancho for ancho in anchos)

    print(formato.format(*columnas))
    print(separador)
    for fila in valores:
        print(formato.format(*fila))


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"No se encontró la base de datos: {DATABASE_PATH}")

    consultas = [
        ("TOP 10 EQUIPOS CON MÁS GOLES", CONSULTA_EQUIPOS_MAS_GOLEADORES),
        ("TOP 10 GOLEADORES DEL MUNDIAL", CONSULTA_TOP_GOLEADORES),
        (
            "TOP 10 EQUIPOS POR PUNTAJE EN FASE DE GRUPOS",
            CONSULTA_TOP_PUNTAJE_FASE_GRUPOS,
        ),
    ]

    with sqlite3.connect(DATABASE_PATH) as conexion:
        conexion.row_factory = sqlite3.Row

        for titulo, consulta in consultas:
            columnas, filas = ejecutar_consulta(conexion, consulta)
            imprimir_tabla(titulo, columnas, filas)


if __name__ == "__main__":
    main()
