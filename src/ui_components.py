from __future__ import annotations

import base64
import re
import unicodedata
from html import escape
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st


FLAG_BY_FIFA = {
    "ALG": "dz",
    "ARG": "ar",
    "AUS": "au",
    "AUT": "at",
    "BEL": "be",
    "BIH": "ba",
    "BRA": "br",
    "CAN": "ca",
    "COL": "co",
    "COD": "cd",
    "CIV": "ci",
    "CPV": "cv",
    "CRO": "hr",
    "CUW": "cw",
    "CZE": "cz",
    "ECU": "ec",
    "EGY": "eg",
    "ENG": "gb-eng",
    "ESP": "es",
    "FRA": "fr",
    "GER": "de",
    "GHA": "gh",
    "HAI": "ht",
    "IRN": "ir",
    "IRQ": "iq",
    "JOR": "jo",
    "JPN": "jp",
    "KOR": "kr",
    "KSA": "sa",
    "MAR": "ma",
    "MEX": "mx",
    "NED": "nl",
    "NOR": "no",
    "NZL": "nz",
    "PAN": "pa",
    "PAR": "py",
    "POR": "pt",
    "QAT": "qa",
    "RSA": "za",
    "SCO": "gb-sct",
    "SEN": "sn",
    "SUI": "ch",
    "SWE": "se",
    "TUN": "tn",
    "TUR": "tr",
    "URU": "uy",
    "USA": "us",
    "UZB": "uz",
}


def link(view: str, **params: object) -> str:
    query = {"view": view}
    query.update({key: value for key, value in params.items() if value not in [None, ""]})
    return "?" + "&".join(f"{key}={quote_plus(str(value))}" for key, value in query.items())


def fmt(value: object) -> str:
    if pd.isna(value) or value == "":
        return "-"
    if isinstance(value, float):
        return f"{value:.1f}" if not value.is_integer() else f"{int(value):,}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def flag_url(code: object) -> str:
    iso = FLAG_BY_FIFA.get(str(code or "").upper(), "")
    return f"https://flagcdn.com/w160/{iso}.png" if iso else ""


def flag_img(code: object, name: object, size: str = "lg") -> str:
    url = flag_url(code)
    label = escape(str(name or "seleccion"))
    if not url:
        return f'<span class="flag flag-{size}">{escape(str(code or ""))}</span>'
    return f'<img class="flag flag-{size}" src="{url}" alt="Bandera de {label}" loading="lazy" />'


def slug_estadio(nombre: object) -> str:
    texto = "" if pd.isna(nombre) else str(nombre)
    texto = texto.replace("&", " t ")
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"[^a-zA-Z0-9]+", "_", texto).strip("_").lower()
    return re.sub(r"_+", "_", texto)


def stadium_data_uri(project_root: Path, estadio: object) -> str:
    path = project_root / "assets" / "estadios" / f"{slug_estadio(estadio)}.png"
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_nav(active: str) -> None:
    labels = [
        ("home", "Home"),
        ("fixture", "Fixture"),
    ]
    tabs = "".join(
        f'<a target="_self" class="{"active" if active == view else ""}" href="{link(view)}">{label}</a>'
        for view, label in labels
    )
    st.markdown(
        f'<nav class="nav-shell"><div class="nav-brand">Mundialito UP 2026</div><div class="nav-tabs">{tabs}</div></nav>',
        unsafe_allow_html=True,
    )


def render_section_head(title: str, meta: str = "") -> None:
    st.markdown(
        f'<div class="section-head"><h2>{escape(title)}</h2><span>{escape(meta)}</span></div>',
        unsafe_allow_html=True,
    )


def render_home(
    resumen: dict[str, int],
    featured: pd.DataFrame,
    grupos: list[tuple[str, pd.DataFrame]],
) -> None:
    metrics = "".join(
        f'<div class="metric-card"><strong>{fmt(value)}</strong><span>{escape(label)}</span></div>'
        for label, value in [
            ("Selecciones", resumen["selecciones"]),
            ("Jugadores", resumen["jugadores"]),
            ("Partidos", resumen["partidos"]),
            ("Sedes", resumen["sedes"]),
        ]
    )
    st.markdown(
        f'<section class="hero"><div class="hero-content"><div class="kicker">Plataforma oficial del torneo</div>'
        f'<h1>Mundialito UP 2026</h1><div class="metric-grid">{metrics}</div>'
        f'<div class="chip-row"><a target="_self" class="action-link primary" href="{link("fixture")}">Explorar fixture</a></div>'
        f'</div></section>',
        unsafe_allow_html=True,
    )


def render_group_cards(grupos: list[tuple[str, pd.DataFrame]], active_group: str | None) -> None:
    cards = []
    for grupo, df in grupos:
        active = " active" if active_group == str(grupo) else ""
        flags = "".join(flag_img(row["codigo_fifa"], row["seleccion"], "sm") for _, row in df.iterrows())
        teams = ", ".join(df["seleccion"].tolist())
        cards.append(
            f'<a target="_self" class="group-card{active}" href="{link("fixture", group=grupo)}">'
            f'<div class="group-title">Grupo {escape(str(grupo))}</div>'
            f'<div class="flag-row">{flags}</div>'
            f'<div class="meta-line" style="margin-top:14px;"><span>{escape(teams)}</span></div></a>'
        )
    st.markdown(f'<div class="group-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_fixture_cards(fixture: pd.DataFrame, selected_match: int | None) -> None:
    if fixture.empty:
        st.markdown('<div class="empty-state">No hay partidos con estos filtros.</div>', unsafe_allow_html=True)
        return
    cards = []
    for _, row in fixture.iterrows():
        match_no = int(row["match_no"])
        active = " active" if selected_match == match_no else ""
        cards.append(
            f'<a target="_self" class="match-card{active}" href="{link("match", match_no=match_no)}">'
            f'<div class="meta-line"><span>M{match_no} | Grupo {escape(str(row["grupo"]))}</span><span>{escape(str(row["fase"]))}</span></div>'
            f'<div class="match-teams"><div class="team-line">{flag_img(row["codigo_local"], row["equipo_local"], "sm")}<span>{escape(str(row["equipo_local"]))}</span></div>'
            f'<div class="team-line">{flag_img(row["codigo_visitante"], row["equipo_visitante"], "sm")}<span>{escape(str(row["equipo_visitante"]))}</span></div></div>'
            f'<div class="meta-line"><span>{escape(str(row["ciudad"]))}</span><span>{escape(str(row["fecha_peru"]))} | {escape(str(row["hora_peru"]))}</span></div>'
            f'<div class="meta-line" style="margin-top:8px;"><span>{escape(str(row["estadio"]))}</span><span>Abrir previa</span></div></a>'
        )
    st.markdown(f'<div class="fixture-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_search_results(results: dict[str, list[dict]]) -> None:
    blocks = []
    for item in results.get("partidos", []):
        blocks.append(
            f'<a target="_self" class="search-card" href="{link("match", match_no=int(item["match_no"]))}">'
            f'<div class="meta-line"><span>Partido M{int(item["match_no"])}</span><span>{escape(str(item["ciudad"]))}</span></div>'
            f'<div class="match-title" style="margin-top:8px;">{escape(str(item["equipo_local"]))} vs {escape(str(item["equipo_visitante"]))}</div></a>'
        )
    for item in results.get("equipos", []):
        blocks.append(
            f'<a target="_self" class="search-card" href="{link("team", team=item["seleccion"])}">'
            f'<div class="team-line">{flag_img(item["codigo_fifa"], item["seleccion"], "sm")}<span>{escape(str(item["seleccion"]))}</span></div>'
            f'<div class="meta-line" style="margin-top:8px;"><span>Grupo {escape(str(item["grupo"]))}</span><span>{escape(str(item["confederacion"]))}</span></div></a>'
        )
    for item in results.get("sedes", []):
        blocks.append(
            f'<a target="_self" class="search-card" href="{link("stadium", stadium=item["estadio"])}">'
            f'<div class="meta-line"><span>Sede</span><span>{escape(str(item["ciudad"]))}</span></div>'
            f'<div class="match-title" style="margin-top:8px;">{escape(str(item["estadio"]))}</div></a>'
        )
    if not blocks:
        st.markdown('<div class="empty-state">No se encontraron resultados.</div>', unsafe_allow_html=True)
        return
    st.markdown(f'<div class="result-grid">{"".join(blocks)}</div>', unsafe_allow_html=True)


def render_match_centre(
    project_root: Path,
    match: pd.Series,
    local: pd.Series,
    visitante: pd.Series,
    sede: pd.Series,
    jugadores_local: pd.DataFrame,
    jugadores_visitante: pd.DataFrame,
    rendimiento_local: dict[str, str],
    rendimiento_visitante: dict[str, str],
    historial_local: list[dict[str, str]],
    historial_visitante: list[dict[str, str]],
) -> None:
    st.markdown(
        f'<div class="section-head"><h2>Previa del partido</h2><span>M{int(match["match_no"])} | {escape(str(match["fase"]))}</span></div>'
        f'<section class="match-centre">{team_card(local, "home", rendimiento_local)}'
        f'{stadium_card(project_root, match, sede)}'
        f'{team_card(visitante, "away", rendimiento_visitante)}</section>',
        unsafe_allow_html=True,
    )
    render_comparison(local, visitante)
    render_recent_form(local["seleccion"], visitante["seleccion"], historial_local, historial_visitante)
    render_squads(local, visitante, jugadores_local, jugadores_visitante)


def team_card(team: pd.Series, side: str, rendimiento: dict[str, str]) -> str:
    cls = "team-card away clickable" if side == "away" else "team-card clickable"
    stats = [
        ("Edad", team.get("edad_promedio", "-")),
        ("Altura", team.get("altura_promedio", "-")),
        ("Plantel", team.get("cantidad_jugadores", "-")),
        ("Grupo", team.get("grupo", "-")),
    ]
    stats.extend(rendimiento.items())
    stats_html = "".join(
        f'<div class="stat"><span>{escape(str(label))}</span><strong>{escape(fmt(value))}</strong></div>'
        for label, value in stats[:6]
    )
    return (
        f'<a target="_self" class="{cls}" href="{link("team", team=team.get("seleccion", ""))}">'
        f'{flag_img(team.get("codigo_fifa", ""), team.get("seleccion", ""), "xl")}'
        f'<div class="team-name">{escape(str(team.get("seleccion", "")))}</div>'
        f'<div class="team-sub">Grupo {escape(str(team.get("grupo", "-")))} | {escape(str(team.get("confederacion", "-")))}</div>'
        f'<div class="stat-grid">{stats_html}</div></a>'
    )


def stadium_card(project_root: Path, match: pd.Series, sede: pd.Series) -> str:
    data_uri = stadium_data_uri(project_root, match["estadio"])
    media = (
        f'<img src="{data_uri}" alt="{escape(str(match["estadio"]))}" />'
        if data_uri
        else f'<div class="pitch-lines"></div>'
    )
    capacity = fmt(sede.get("capacidad_aprox", "-"))
    return (
        f'<a target="_self" class="stadium-panel stadium-link" href="{link("stadium", stadium=match["estadio"])}">'
        f'<div class="stadium-media">{media}</div><div class="stadium-copy">'
        f'<div class="kicker">Sede del partido</div><h2>{escape(str(match["estadio"]))}</h2>'
        f'<div class="chip-row"><span class="chip">{escape(str(match["ciudad"]))}</span>'
        f'<span class="chip">{escape(str(match["pais_sede"]))}</span>'
        f'<span class="chip">{escape(str(match["fecha_peru"]))}</span>'
        f'<span class="chip">{escape(str(match["hora_peru"]))} Peru</span>'
        f'<span class="chip">Cap. {capacity}</span></div></div></a>'
    )


def render_comparison(local: pd.Series, visitante: pd.Series) -> None:
    rows = [
        ("Edad promedio", "edad_promedio"),
        ("Altura promedio", "altura_promedio"),
        ("Jugadores", "cantidad_jugadores"),
        ("Arqueros", "arqueros"),
        ("Defensas", "defensas"),
        ("Mediocampistas", "mediocampistas"),
        ("Delanteros", "delanteros"),
        ("Grupo", "grupo"),
        ("Confederacion", "confederacion"),
    ]
    html = "".join(
        f'<div class="compare-row"><strong>{escape(fmt(local.get(key, "-")))}</strong>'
        f'<span>{escape(label)}</span><strong>{escape(fmt(visitante.get(key, "-")))}</strong></div>'
        for label, key in rows
    )
    st.markdown(
        f'<section class="comparison-panel"><div class="section-head"><h2>Comparativa</h2>'
        f'<span>{escape(str(local["seleccion"]))} vs {escape(str(visitante["seleccion"]))}</span></div>{html}</section>',
        unsafe_allow_html=True,
    )


def render_recent_form(
    local_name: str,
    visitante_name: str,
    historial_local: list[dict[str, str]],
    historial_visitante: list[dict[str, str]],
) -> None:
    def side(name: str, items: list[dict[str, str]]) -> str:
        if not items:
            return '<div class="empty-state">Sin historial reciente disponible.</div>'
        rows = "".join(
            f'<div class="player-row"><span class="chip status-{escape(item["clase"])}">{escape(item["estado"])}</span>'
            f'<div><strong>{escape(item["marcador"])} vs {escape(item["rival"])}</strong>'
            f'<span>{escape(item["competencia"])}</span></div></div>'
            for item in items
        )
        return f'<div class="panel"><div class="match-title">{escape(name)}</div>{rows}</div>'

    st.markdown(
        f'<section class="section"><div class="section-head"><h2>Camino reciente</h2><span>solo dentro de la previa</span></div>'
        f'<div class="two-grid">{side(local_name, historial_local)}{side(visitante_name, historial_visitante)}</div></section>',
        unsafe_allow_html=True,
    )


def render_squads(
    local: pd.Series,
    visitante: pd.Series,
    jugadores_local: pd.DataFrame,
    jugadores_visitante: pd.DataFrame,
) -> None:
    st.markdown(
        f'<section class="squad-panel"><div class="section-head"><h2>Planteles del partido</h2>'
        f'<span>solo para el cruce seleccionado</span></div><div class="players-grid">'
        f'<div><div class="team-line">{flag_img(local.get("codigo_fifa", ""), local.get("seleccion", ""), "sm")}<span>{escape(str(local["seleccion"]))}</span></div>'
        f'{player_rows(jugadores_local)}</div>'
        f'<div><div class="team-line">{flag_img(visitante.get("codigo_fifa", ""), visitante.get("seleccion", ""), "sm")}<span>{escape(str(visitante["seleccion"]))}</span></div>'
        f'{player_rows(jugadores_visitante)}</div></div></section>',
        unsafe_allow_html=True,
    )


def player_rows(jugadores: pd.DataFrame, limit: int = 12) -> str:
    if jugadores.empty:
        return '<div class="empty-state">No hay jugadores para este filtro.</div>'
    rows = []
    for _, row in jugadores.head(limit).iterrows():
        foto_url = str(row.get("foto_url", "")).strip()
        if foto_url and foto_url.lower() != "nan":
            foto = (
                f'<img class="player-photo" src="{escape(foto_url, quote=True)}" '
                f'alt="Foto de {escape(str(row["jugador_nombre_limpio"]), quote=True)}" '
                f'loading="lazy" referrerpolicy="no-referrer">'
            )
        else:
            foto = f'<div class="player-photo player-photo-empty">{position_icon(str(row.get("posicion", "")))}</div>'
        rows.append(
            f'<div class="player-row">{foto}'
            f'<div><strong>{escape(str(row["jugador_nombre_limpio"]))}</strong>'
            f'<span>{escape(str(row["posicion_nombre"]))} | {escape(str(row["club_limpio"]))}</span></div></div>'
        )
    return "".join(rows)


def position_icon(pos: str) -> str:
    pos = pos.upper()
    if pos == "GK":
        return '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M4 5h16v14H4z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="10" r="2" fill="currentColor"/></svg>'
    if pos == "DF":
        return '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M12 3 19 6v5c0 5-3 8-7 10-4-2-7-5-7-10V6l7-3Z" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
    if pos == "MF":
        return '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2"/><path d="M4 12h16M12 4v16" stroke="currentColor" stroke-width="2"/></svg>'
    return '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M4 20 20 4" stroke="currentColor" stroke-width="2"/><path d="M14 4h6v6" fill="none" stroke="currentColor" stroke-width="2"/></svg>'


def render_team_profile(team: pd.Series, team_fixture: pd.DataFrame, players: pd.DataFrame, clubs: pd.DataFrame) -> None:
    fixtures = "".join(
        f'<a target="_self" class="match-card" href="{link("match", match_no=int(row["match_no"]))}">'
        f'<div class="meta-line"><span>M{int(row["match_no"])}</span><span>{escape(str(row["ciudad"]))}</span></div>'
        f'<div class="match-title" style="margin-top:10px;">{escape(str(row["equipo_local"]))} vs {escape(str(row["equipo_visitante"]))}</div></a>'
        for _, row in team_fixture.iterrows()
    )
    club_rows = "".join(
        f'<div class="player-row"><strong>{escape(str(row["jugadores"]))}</strong><div><strong>{escape(str(row["club_limpio"]))}</strong><span>jugadores</span></div></div>'
        for _, row in clubs.iterrows()
    )
    st.markdown(
        f'<section class="section"><div class="section-head"><h2>Perfil de seleccion</h2><span>{escape(str(team["seleccion"]))}</span></div>'
        f'<div class="match-centre" style="grid-template-columns: .85fr 1.15fr .85fr;">'
        f'{team_card(team, "home", {})}<div class="panel"><div class="section-head"><h2>Partidos</h2><span>{len(team_fixture)} cargados</span></div><div class="fixture-grid" style="grid-template-columns:1fr;">{fixtures}</div></div>'
        f'<div class="panel"><div class="section-head"><h2>Clubes</h2><span>mas repetidos</span></div>{club_rows}</div></div>'
        f'<div class="squad-panel"><div class="section-head"><h2>Jugadores</h2><span>contexto seleccion</span></div>{player_rows(players, 18)}</div></section>',
        unsafe_allow_html=True,
    )


def render_stadium_profile(
    project_root: Path,
    stadium: pd.Series,
    stadium_fixture: pd.DataFrame,
) -> None:
    data_uri = stadium_data_uri(project_root, stadium["estadio"])
    media = (
        f'<img src="{data_uri}" alt="{escape(str(stadium["estadio"]))}" />'
        if data_uri
        else '<div class="pitch-lines"></div>'
    )
    matches = "".join(
        f'<a target="_self" class="match-card" href="{link("match", match_no=int(row["match_no"]))}">'
        f'<div class="meta-line"><span>M{int(row["match_no"])}</span><span>{escape(str(row["fecha_peru"]))}</span></div>'
        f'<div class="match-title" style="margin-top:10px;">{escape(str(row["equipo_local"]))} vs {escape(str(row["equipo_visitante"]))}</div></a>'
        for _, row in stadium_fixture.iterrows()
    )
    st.markdown(
        f'<section class="section"><div class="section-head"><h2>Ficha de estadio</h2><span>{escape(str(stadium["ciudad"]))}</span></div>'
        f'<div class="two-grid"><article class="stadium-panel"><div class="stadium-media">{media}</div>'
        f'<div class="stadium-copy"><div class="kicker">Sede oficial</div><h2>{escape(str(stadium["estadio"]))}</h2>'
        f'<div class="chip-row"><span class="chip">{escape(str(stadium["ciudad"]))}</span><span class="chip">{escape(str(stadium["pais"]))}</span>'
        f'<span class="chip">Cap. {fmt(stadium.get("capacidad_aprox", "-"))}</span><span class="chip">{len(stadium_fixture)} partidos</span></div></div></article>'
        f'<div class="panel"><div class="section-head"><h2>Partidos en sede</h2><span>{len(stadium_fixture)} programados</span></div><div class="fixture-grid" style="grid-template-columns:1fr;">{matches}</div></div></div></section>',
        unsafe_allow_html=True,
    )
