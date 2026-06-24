r"""Descarga las URLs de fotos de jugadores desde TheSportsDB.

Ejemplos:
    venv\Scripts\python.exe API.PY --seleccion Argentina
    venv\Scripts\python.exe API.PY --todos

El resultado se guarda en:
    data/mundial_2026/processed/fotos_jugadores.csv
"""

from __future__ import annotations

import argparse
import time
import unicodedata
from pathlib import Path

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parent
PLAYERS_PATH = PROJECT_ROOT / "data" / "mundial_2026" / "processed" / "fact_jugadores.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "mundial_2026" / "processed" / "fotos_jugadores.csv"
API_URL = "https://www.thesportsdb.com/api/v1/json/123/searchplayers.php"
REQUEST_INTERVAL_SECONDS = 2.1  # El plan gratis permite 30 solicitudes por minuto.
USER_AGENT = "MundialitoUP/1.0 (proyecto educativo)"


def normalizar(valor: object) -> str:
    texto = "" if pd.isna(valor) else str(valor).strip()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(char for char in texto if not unicodedata.combining(char)).casefold()


def nombres_para_busqueda(nombre: str) -> list[str]:
    """Convierte 'APELLIDO Nombre' en alternativas habituales de búsqueda."""
    partes = nombre.strip().split()
    if len(partes) < 2:
        return [nombre.strip()]

    cantidad_apellidos = 0
    for parte in partes:
        if parte.isupper():
            cantidad_apellidos += 1
        else:
            break

    if cantidad_apellidos:
        apellidos = partes[:cantidad_apellidos]
        nombres = partes[cantidad_apellidos:]
        alternativas = [
            " ".join(nombres + apellidos).title(),
            " ".join(nombres[:1] + apellidos).title(),
        ]
    else:
        alternativas = [nombre.strip().title()]

    alternativas.append(nombre.strip().title())
    return list(dict.fromkeys(alternativas))


def elegir_resultado(resultados: list[dict], nombre: str, fecha_nacimiento: str) -> dict | None:
    if not resultados:
        return None

    nombre_objetivo = normalizar(nombre)
    fecha_objetivo = pd.to_datetime(fecha_nacimiento, dayfirst=True, errors="coerce")
    mejor: dict | None = None
    mejor_puntaje = -1

    for jugador in resultados:
        deporte = normalizar(jugador.get("strSport"))
        if deporte and deporte != "soccer":
            continue

        nombres_api = {
            normalizar(jugador.get("strPlayer")),
            normalizar(jugador.get("strPlayerAlternate")),
        }
        puntaje = 0
        identidad_confirmada = False
        if nombre_objetivo in nombres_api:
            puntaje += 4
            identidad_confirmada = True
        elif any(
            set(nombre_objetivo.split()) == set(nombre_api.split())
            for nombre_api in nombres_api
            if nombre_api
        ):
            puntaje += 4
            identidad_confirmada = True
        elif any(
            nombre_objetivo in nombre_api or nombre_api in nombre_objetivo
            for nombre_api in nombres_api
            if nombre_api
        ):
            puntaje += 2
            identidad_confirmada = True

        fecha_api = pd.to_datetime(jugador.get("dateBorn"), errors="coerce")
        if pd.notna(fecha_objetivo) and pd.notna(fecha_api) and fecha_objetivo.date() == fecha_api.date():
            puntaje += 5
            identidad_confirmada = True

        if jugador.get("strThumb") or jugador.get("strCutout"):
            puntaje += 1

        if identidad_confirmada and puntaje > mejor_puntaje:
            mejor = jugador
            mejor_puntaje = puntaje

    return mejor if mejor_puntaje >= 1 else None


def buscar_jugador(session: requests.Session, row: pd.Series) -> dict[str, object]:
    nombre_original = str(row["jugador_nombre_limpio"]).strip()
    consultas = nombres_para_busqueda(nombre_original)
    resultados: list[dict] = []
    error = ""

    for consulta in dict.fromkeys(consultas):
        try:
            respuesta = session.get(API_URL, params={"p": consulta}, timeout=20)
            respuesta.raise_for_status()
            resultados = respuesta.json().get("player") or []
            if resultados:
                break
        except (requests.RequestException, ValueError) as exc:
            error = str(exc)
            break

    elegido = elegir_resultado(resultados, nombre_original, str(row.get("fecha_nacimiento", "")))
    return {
        "id_jugador": row["id_jugador"],
        "jugador_nombre_limpio": nombre_original,
        "seleccion": row.get("seleccion", ""),
        "foto_url": (elegido or {}).get("strCutout") or (elegido or {}).get("strThumb") or "",
        "thesportsdb_id": (elegido or {}).get("idPlayer", ""),
        "nombre_api": (elegido or {}).get("strPlayer", ""),
        "estado_foto": "encontrada" if elegido and ((elegido.get("strCutout") or elegido.get("strThumb"))) else "no_encontrada",
        "error_api": error,
    }


def cargar_existentes() -> pd.DataFrame:
    if OUTPUT_PATH.exists():
        return pd.read_csv(OUTPUT_PATH, dtype={"thesportsdb_id": "string"})
    return pd.DataFrame()


def guardar_resultados(resultados: list[dict[str, object]], existentes: pd.DataFrame) -> None:
    nuevos = pd.DataFrame(resultados)
    combinado = pd.concat([existentes, nuevos], ignore_index=True)
    combinado = combinado.drop_duplicates(subset=["id_jugador"], keep="last")
    combinado = combinado.sort_values("id_jugador")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combinado.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser(description="Busca fotos de jugadores en TheSportsDB.")
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--seleccion", help='Procesa un país, por ejemplo: --seleccion "Argentina"')
    grupo.add_argument("--todos", action="store_true", help="Procesa todos los jugadores.")
    parser.add_argument(
        "--reintentar",
        action="store_true",
        help="Vuelve a consultar jugadores ya guardados, incluso si no tenían foto.",
    )
    args = parser.parse_args()

    if not PLAYERS_PATH.exists():
        raise FileNotFoundError(f"No se encontró {PLAYERS_PATH}")

    jugadores = pd.read_csv(PLAYERS_PATH)
    existentes = cargar_existentes()

    if args.seleccion:
        seleccion_normalizada = normalizar(args.seleccion)
        jugadores = jugadores[
            jugadores["seleccion"].map(normalizar) == seleccion_normalizada
        ]
        if jugadores.empty:
            opciones = ", ".join(sorted(pd.read_csv(PLAYERS_PATH)["seleccion"].dropna().unique()))
            raise SystemExit(f"No se encontró esa selección. Opciones: {opciones}")

    if not args.reintentar and not existentes.empty:
        ids_guardados = set(existentes["id_jugador"].astype(str))
        jugadores = jugadores[~jugadores["id_jugador"].astype(str).isin(ids_guardados)]

    if jugadores.empty:
        print("No hay jugadores pendientes. Usa --reintentar para consultarlos nuevamente.")
        return

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    resultados: list[dict[str, object]] = []
    total = len(jugadores)

    for indice, (_, jugador) in enumerate(jugadores.iterrows(), start=1):
        resultado = buscar_jugador(session, jugador)
        resultados.append(resultado)
        marca = "OK" if resultado["estado_foto"] == "encontrada" else "--"
        print(f"[{indice}/{total}] {marca} {resultado['jugador_nombre_limpio']}")

        if indice % 25 == 0:
            guardar_resultados(resultados, existentes)
        if indice < total:
            time.sleep(REQUEST_INTERVAL_SECONDS)

    guardar_resultados(resultados, existentes)
    encontradas = sum(item["estado_foto"] == "encontrada" for item in resultados)
    print(f"\nListo: {encontradas}/{total} fotos encontradas.")
    print(f"Archivo generado: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
