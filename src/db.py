"""Crea y carga la base de datos SQLite de Mundialito UP.

Uso:
    venv\\Scripts\\python.exe src\\db.py
    venv\\Scripts\\python.exe src\\db.py --recrear

La base se genera en:
    data/mundial_2026/mundialito.db

El script importa los CSV procesados actuales y deja preparadas tablas para
guardar resultados, eventos, alineaciones y estadísticas provenientes de APIs.
"""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "mundial_2026" / "processed"
DB_PATH = PROJECT_ROOT / "data" / "mundial_2026" / "mundialito.db"


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS torneos (
    id_torneo INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    anio INTEGER NOT NULL,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    paises_sede TEXT,
    UNIQUE(nombre, anio)
);

CREATE TABLE IF NOT EXISTS selecciones (
    id_equipo INTEGER PRIMARY KEY,
    api_id TEXT UNIQUE,
    id_torneo INTEGER NOT NULL DEFAULT 1,
    seleccion TEXT NOT NULL,
    seleccion_normalizada TEXT,
    seleccion_original_fifa TEXT,
    codigo_fifa TEXT,
    confederacion TEXT,
    grupo TEXT,
    pais TEXT,
    clasificado TEXT,
    debut_mundial INTEGER,
    escudo_url TEXT,
    ranking_fifa INTEGER,
    fuente TEXT,
    actualizado_en TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_torneo) REFERENCES torneos(id_torneo),
    UNIQUE(id_torneo, codigo_fifa)
);

CREATE TABLE IF NOT EXISTS jugadores (
    id_jugador INTEGER PRIMARY KEY,
    api_id TEXT UNIQUE,
    id_equipo INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    dorsal INTEGER,
    posicion TEXT,
    posicion_nombre TEXT,
    fecha_nacimiento TEXT,
    edad INTEGER,
    altura_cm INTEGER,
    club TEXT,
    pais_club TEXT,
    foto_url TEXT,
    fuente TEXT,
    actualizado_en TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_equipo) REFERENCES selecciones(id_equipo)
);

CREATE TABLE IF NOT EXISTS sedes (
    id_sede INTEGER PRIMARY KEY,
    api_id TEXT UNIQUE,
    estadio TEXT NOT NULL,
    nombre_fifa TEXT,
    ciudad TEXT,
    ciudad_normalizada TEXT,
    pais TEXT,
    capacidad INTEGER,
    cantidad_partidos INTEGER,
    latitud REAL,
    longitud REAL,
    imagen_url TEXT,
    fuente TEXT,
    nota TEXT,
    actualizado_en TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS partidos (
    id_partido INTEGER PRIMARY KEY,
    api_id TEXT UNIQUE,
    id_torneo INTEGER NOT NULL DEFAULT 1,
    match_no INTEGER NOT NULL,
    fase TEXT,
    ronda TEXT,
    grupo TEXT,
    equipo_local_id INTEGER,
    equipo_visitante_id INTEGER,
    local_pendiente TEXT,
    visitante_pendiente TEXT,
    codigo_local TEXT,
    codigo_visitante TEXT,
    id_sede INTEGER,
    fecha_hora_local TEXT,
    fecha_hora_peru TEXT,
    fecha_hora_utc TEXT,
    estado TEXT DEFAULT 'Programado',
    goles_local INTEGER,
    goles_visitante INTEGER,
    goles_local_descanso INTEGER,
    goles_visitante_descanso INTEGER,
    goles_local_penales INTEGER,
    goles_visitante_penales INTEGER,
    minuto_actual INTEGER,
    periodo TEXT,
    arbitro TEXT,
    asistencia INTEGER,
    clima TEXT,
    ganador_id INTEGER,
    fuente TEXT,
    fuente_verificacion TEXT,
    nota TEXT,
    actualizado_en TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_torneo) REFERENCES torneos(id_torneo),
    FOREIGN KEY (equipo_local_id) REFERENCES selecciones(id_equipo),
    FOREIGN KEY (equipo_visitante_id) REFERENCES selecciones(id_equipo),
    FOREIGN KEY (id_sede) REFERENCES sedes(id_sede),
    FOREIGN KEY (ganador_id) REFERENCES selecciones(id_equipo),
    UNIQUE(id_torneo, match_no)
);

CREATE TABLE IF NOT EXISTS eventos_partido (
    id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
    api_id TEXT UNIQUE,
    id_partido INTEGER NOT NULL,
    id_equipo INTEGER,
    id_jugador INTEGER,
    tipo TEXT NOT NULL,
    detalle TEXT,
    minuto INTEGER,
    minuto_extra INTEGER,
    periodo TEXT,
    creado_en TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_partido) REFERENCES partidos(id_partido) ON DELETE CASCADE,
    FOREIGN KEY (id_equipo) REFERENCES selecciones(id_equipo),
    FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
);

CREATE TABLE IF NOT EXISTS alineaciones (
    id_alineacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_partido INTEGER NOT NULL,
    id_equipo INTEGER NOT NULL,
    id_jugador INTEGER NOT NULL,
    titular INTEGER NOT NULL DEFAULT 0 CHECK(titular IN (0, 1)),
    posicion TEXT,
    dorsal INTEGER,
    capitan INTEGER DEFAULT 0 CHECK(capitan IN (0, 1)),
    formacion TEXT,
    FOREIGN KEY (id_partido) REFERENCES partidos(id_partido) ON DELETE CASCADE,
    FOREIGN KEY (id_equipo) REFERENCES selecciones(id_equipo),
    FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador),
    UNIQUE(id_partido, id_jugador)
);

CREATE TABLE IF NOT EXISTS estadisticas_partido (
    id_estadistica INTEGER PRIMARY KEY AUTOINCREMENT,
    id_partido INTEGER NOT NULL,
    id_equipo INTEGER NOT NULL,
    posesion REAL,
    tiros INTEGER,
    tiros_puerta INTEGER,
    corners INTEGER,
    faltas INTEGER,
    fueras_juego INTEGER,
    tarjetas_amarillas INTEGER,
    tarjetas_rojas INTEGER,
    pases INTEGER,
    pases_correctos INTEGER,
    precision_pases REAL,
    atajadas INTEGER,
    actualizado_en TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_partido) REFERENCES partidos(id_partido) ON DELETE CASCADE,
    FOREIGN KEY (id_equipo) REFERENCES selecciones(id_equipo),
    UNIQUE(id_partido, id_equipo)
);

CREATE TABLE IF NOT EXISTS posiciones_grupo (
    id_posicion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_torneo INTEGER NOT NULL,
    id_equipo INTEGER NOT NULL,
    grupo TEXT NOT NULL,
    posicion INTEGER,
    jugados INTEGER DEFAULT 0,
    ganados INTEGER DEFAULT 0,
    empatados INTEGER DEFAULT 0,
    perdidos INTEGER DEFAULT 0,
    goles_favor INTEGER DEFAULT 0,
    goles_contra INTEGER DEFAULT 0,
    diferencia_goles INTEGER DEFAULT 0,
    puntos INTEGER DEFAULT 0,
    actualizado_en TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_torneo) REFERENCES torneos(id_torneo),
    FOREIGN KEY (id_equipo) REFERENCES selecciones(id_equipo),
    UNIQUE(id_torneo, id_equipo)
);

CREATE TABLE IF NOT EXISTS sincronizaciones_api (
    id_sincronizacion INTEGER PRIMARY KEY AUTOINCREMENT,
    proveedor TEXT NOT NULL,
    recurso TEXT NOT NULL,
    iniciado_en TEXT NOT NULL,
    finalizado_en TEXT,
    estado TEXT NOT NULL,
    registros_recibidos INTEGER DEFAULT 0,
    registros_guardados INTEGER DEFAULT 0,
    mensaje_error TEXT
);

CREATE INDEX IF NOT EXISTS idx_partidos_fecha ON partidos(fecha_hora_peru);
CREATE INDEX IF NOT EXISTS idx_partidos_estado ON partidos(estado);
CREATE INDEX IF NOT EXISTS idx_partidos_equipos
    ON partidos(equipo_local_id, equipo_visitante_id);
CREATE INDEX IF NOT EXISTS idx_eventos_partido ON eventos_partido(id_partido);
CREATE INDEX IF NOT EXISTS idx_jugadores_equipo ON jugadores(id_equipo);
"""


def valor(valor_original: object) -> object | None:
    """Convierte valores vacíos/NaN de pandas a NULL de SQLite."""
    if pd.isna(valor_original):
        return None
    if hasattr(valor_original, "item"):
        return valor_original.item()
    return valor_original


def entero(valor_original: object) -> int | None:
    limpio = valor(valor_original)
    return None if limpio in (None, "") else int(float(limpio))


def real(valor_original: object) -> float | None:
    limpio = valor(valor_original)
    return None if limpio in (None, "") else float(limpio)


def fecha_iso(valor_original: object) -> str | None:
    limpio = valor(valor_original)
    if limpio in (None, ""):
        return None
    fecha = pd.to_datetime(limpio, dayfirst=True, errors="coerce")
    return None if pd.isna(fecha) else fecha.strftime("%Y-%m-%d")


def fecha_hora(fecha: object, hora: object) -> str | None:
    fecha_limpia = valor(fecha)
    hora_limpia = valor(hora)
    if fecha_limpia in (None, ""):
        return None
    texto = str(fecha_limpia)
    if hora_limpia not in (None, ""):
        texto += f" {hora_limpia}"
    momento = pd.to_datetime(texto, errors="coerce")
    return None if pd.isna(momento) else momento.strftime("%Y-%m-%d %H:%M:%S")


def leer_csv(nombre: str) -> pd.DataFrame:
    ruta = PROCESSED_DIR / nombre
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo requerido: {ruta}")
    return pd.read_csv(ruta)


def crear_esquema(conexion: sqlite3.Connection) -> None:
    conexion.executescript(SCHEMA_SQL)
    conexion.execute(
        """
        INSERT INTO torneos (
            id_torneo, nombre, anio, fecha_inicio, fecha_fin, paises_sede
        ) VALUES (1, ?, ?, ?, ?, ?)
        ON CONFLICT(id_torneo) DO UPDATE SET
            nombre = excluded.nombre,
            anio = excluded.anio,
            fecha_inicio = excluded.fecha_inicio,
            fecha_fin = excluded.fecha_fin,
            paises_sede = excluded.paises_sede
        """,
        (
            "Copa Mundial de la FIFA 2026",
            2026,
            "2026-06-11",
            "2026-07-19",
            "Canadá, Estados Unidos y México",
        ),
    )


def cargar_selecciones(conexion: sqlite3.Connection) -> int:
    df = leer_csv("dim_selecciones.csv")
    filas = [
        (
            entero(row.id_equipo),
            str(row.seleccion),
            valor(row.seleccion_normalizada),
            valor(row.seleccion_original_fifa),
            valor(row.codigo_fifa),
            valor(row.confederacion),
            valor(row.grupo),
            valor(row.pais),
            valor(row.clasificado),
            entero(row.debut_mundial),
            valor(row.fuente_equipos),
        )
        for row in df.itertuples(index=False)
    ]
    conexion.executemany(
        """
        INSERT INTO selecciones (
            id_equipo, id_torneo, seleccion, seleccion_normalizada,
            seleccion_original_fifa, codigo_fifa, confederacion, grupo, pais,
            clasificado, debut_mundial, fuente
        ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id_equipo) DO UPDATE SET
            seleccion = excluded.seleccion,
            seleccion_normalizada = excluded.seleccion_normalizada,
            seleccion_original_fifa = excluded.seleccion_original_fifa,
            codigo_fifa = excluded.codigo_fifa,
            confederacion = excluded.confederacion,
            grupo = excluded.grupo,
            pais = excluded.pais,
            clasificado = excluded.clasificado,
            debut_mundial = excluded.debut_mundial,
            fuente = excluded.fuente,
            actualizado_en = CURRENT_TIMESTAMP
        """,
        filas,
    )
    return len(filas)


def cargar_sedes(conexion: sqlite3.Connection) -> int:
    df = leer_csv("dim_sedes.csv")
    filas = [
        (
            entero(row.id_sede),
            str(row.estadio),
            valor(row.nombre_fifa_estadio),
            valor(row.ciudad),
            valor(row.ciudad_normalizada),
            valor(row.pais),
            entero(row.capacidad_aprox),
            entero(row.cantidad_partidos),
            real(row.latitud),
            real(row.longitud),
            valor(row.fuente_sedes),
            valor(row.nota),
        )
        for row in df.itertuples(index=False)
    ]
    conexion.executemany(
        """
        INSERT INTO sedes (
            id_sede, estadio, nombre_fifa, ciudad, ciudad_normalizada, pais,
            capacidad, cantidad_partidos, latitud, longitud, fuente, nota
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id_sede) DO UPDATE SET
            estadio = excluded.estadio,
            nombre_fifa = excluded.nombre_fifa,
            ciudad = excluded.ciudad,
            ciudad_normalizada = excluded.ciudad_normalizada,
            pais = excluded.pais,
            capacidad = excluded.capacidad,
            cantidad_partidos = excluded.cantidad_partidos,
            latitud = excluded.latitud,
            longitud = excluded.longitud,
            fuente = excluded.fuente,
            nota = excluded.nota,
            actualizado_en = CURRENT_TIMESTAMP
        """,
        filas,
    )
    return len(filas)


def cargar_jugadores(conexion: sqlite3.Connection) -> int:
    jugadores = leer_csv("fact_jugadores.csv")
    fotos_path = PROCESSED_DIR / "fotos_jugadores.csv"
    if fotos_path.exists():
        fotos = pd.read_csv(fotos_path, usecols=["id_jugador", "foto_url", "thesportsdb_id"])
        jugadores = jugadores.merge(fotos, on="id_jugador", how="left")
    else:
        jugadores["foto_url"] = None
        jugadores["thesportsdb_id"] = None

    filas = [
        (
            entero(row.id_jugador),
            valor(row.thesportsdb_id),
            entero(row.id_equipo),
            str(row.jugador_nombre_limpio),
            valor(row.posicion),
            valor(row.posicion_nombre),
            fecha_iso(row.fecha_nacimiento),
            entero(row.edad),
            entero(row.altura_cm),
            valor(row.club_limpio),
            valor(row.pais_club),
            valor(row.foto_url),
            valor(row.fuente_jugadores),
        )
        for row in jugadores.itertuples(index=False)
    ]
    conexion.executemany(
        """
        INSERT INTO jugadores (
            id_jugador, api_id, id_equipo, nombre, posicion, posicion_nombre,
            fecha_nacimiento, edad, altura_cm, club, pais_club, foto_url, fuente
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id_jugador) DO UPDATE SET
            api_id = excluded.api_id,
            id_equipo = excluded.id_equipo,
            nombre = excluded.nombre,
            posicion = excluded.posicion,
            posicion_nombre = excluded.posicion_nombre,
            fecha_nacimiento = excluded.fecha_nacimiento,
            edad = excluded.edad,
            altura_cm = excluded.altura_cm,
            club = excluded.club,
            pais_club = excluded.pais_club,
            foto_url = excluded.foto_url,
            fuente = excluded.fuente,
            actualizado_en = CURRENT_TIMESTAMP
        """,
        filas,
    )
    return len(filas)


def cargar_partidos(conexion: sqlite3.Connection) -> int:
    df = leer_csv("fact_fixture.csv")
    filas = []
    for row in df.itertuples(index=False):
        local_id = entero(row.id_equipo_local)
        visitante_id = entero(row.id_equipo_visitante)
        filas.append(
            (
                entero(row.id_partido),
                entero(row.match_no),
                valor(row.fase),
                valor(row.ronda),
                valor(row.grupo),
                local_id,
                visitante_id,
                None if local_id else valor(row.equipo_local),
                None if visitante_id else valor(row.equipo_visitante),
                valor(row.codigo_local),
                valor(row.codigo_visitante),
                entero(row.id_sede),
                fecha_hora(row.fecha_local, row.hora_local_24h),
                fecha_hora(row.fecha_peru, row.hora_peru),
                valor(row.estado),
                entero(row.goles_local),
                entero(row.goles_visitante),
                valor(row.fuente_fixture),
                valor(row.fuente_verificacion_fifa),
                valor(row.nota),
            )
        )

    conexion.executemany(
        """
        INSERT INTO partidos (
            id_partido, id_torneo, match_no, fase, ronda, grupo,
            equipo_local_id, equipo_visitante_id, local_pendiente,
            visitante_pendiente, codigo_local, codigo_visitante, id_sede,
            fecha_hora_local, fecha_hora_peru, estado, goles_local,
            goles_visitante, fuente, fuente_verificacion, nota
        ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id_partido) DO UPDATE SET
            match_no = excluded.match_no,
            fase = excluded.fase,
            ronda = excluded.ronda,
            grupo = excluded.grupo,
            equipo_local_id = excluded.equipo_local_id,
            equipo_visitante_id = excluded.equipo_visitante_id,
            local_pendiente = excluded.local_pendiente,
            visitante_pendiente = excluded.visitante_pendiente,
            codigo_local = excluded.codigo_local,
            codigo_visitante = excluded.codigo_visitante,
            id_sede = excluded.id_sede,
            fecha_hora_local = excluded.fecha_hora_local,
            fecha_hora_peru = excluded.fecha_hora_peru,
            estado = excluded.estado,
            goles_local = excluded.goles_local,
            goles_visitante = excluded.goles_visitante,
            fuente = excluded.fuente,
            fuente_verificacion = excluded.fuente_verificacion,
            nota = excluded.nota,
            actualizado_en = CURRENT_TIMESTAMP
        """,
        filas,
    )
    return len(filas)


def crear_base_datos(recrear: bool = False) -> dict[str, int]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if recrear and DB_PATH.exists():
        DB_PATH.unlink()

    with sqlite3.connect(DB_PATH) as conexion:
        conexion.execute("PRAGMA foreign_keys = ON")
        crear_esquema(conexion)
        conteos = {
            "selecciones": cargar_selecciones(conexion),
            "sedes": cargar_sedes(conexion),
            "jugadores": cargar_jugadores(conexion),
            "partidos": cargar_partidos(conexion),
        }
        conexion.execute(
            """
            INSERT INTO sincronizaciones_api (
                proveedor, recurso, iniciado_en, finalizado_en, estado,
                registros_recibidos, registros_guardados
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "CSV procesados del proyecto",
                "carga_inicial",
                datetime.now().isoformat(timespec="seconds"),
                datetime.now().isoformat(timespec="seconds"),
                "completado",
                sum(conteos.values()),
                sum(conteos.values()),
            ),
        )
        conexion.commit()
        errores_fk = conexion.execute("PRAGMA foreign_key_check").fetchall()
        if errores_fk:
            raise RuntimeError(f"Se encontraron relaciones inválidas: {errores_fk}")
    return conteos


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crea y carga la base SQLite de Mundialito UP."
    )
    parser.add_argument(
        "--recrear",
        action="store_true",
        help="Elimina la base existente antes de crearla nuevamente.",
    )
    args = parser.parse_args()

    conteos = crear_base_datos(recrear=args.recrear)
    print(f"Base SQLite creada correctamente: {DB_PATH}")
    for tabla, cantidad in conteos.items():
        print(f"  {tabla}: {cantidad}")


if __name__ == "__main__":
    main()
