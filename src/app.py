from __future__ import annotations

import base64
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
sys.path.append(str(CURRENT_DIR))

from data_service import (
    ALIASES_RENDIMIENTO,
    busqueda_global,
    cargar_datos,
    clubes_por_seleccion,
    filtrar_fixture,
    fixture_por_equipo,
    fixture_por_estadio,
    get_match,
    get_stadium,
    get_team,
    grupos_torneo,
    historial_equipo,
    jugadores_por_equipo,
    normalizar_texto,
    opciones_filtros,
    proximos_partidos,
    rendimiento_equipo,
    resumen_torneo,
)
from styles import apply_global_styles
from ui_components import (
    flag_img,
    fmt,
    player_rows,
    render_match_centre,
    render_section_head,
    stadium_data_uri,
)
import viz as viz_helpers


st.set_page_config(page_title="Mundialito UP", layout="wide", initial_sidebar_state="collapsed")


def data_version() -> tuple[tuple[str, int], ...]:
    processed_dir = PROJECT_ROOT / "data" / "mundial_2026" / "processed"
    files = sorted(processed_dir.glob("*.csv"))
    return tuple((path.name, path.stat().st_mtime_ns) for path in files)


@st.cache_data(show_spinner=False)
def load_data(_version: tuple[tuple[str, int], ...]) -> dict[str, pd.DataFrame]:
    return cargar_datos(PROJECT_ROOT)


def init_state(datos: dict[str, pd.DataFrame]) -> None:
    fixture = datos["fact_fixture"].sort_values("match_no")
    teams = datos["dataset_dashboard"].sort_values("seleccion")
    sedes_fixture = datos["fact_fixture"].sort_values("match_no")
    qp_tab = st.query_params.get("tab", "")
    qp_sede = st.query_params.get("sede", "")
    qp_match = st.query_params.get("match", "")
    qp_team = st.query_params.get("team", "")
    if isinstance(qp_tab, list):
        qp_tab = qp_tab[0] if qp_tab else ""
    if isinstance(qp_sede, list):
        qp_sede = qp_sede[0] if qp_sede else ""
    if isinstance(qp_match, list):
        qp_match = qp_match[0] if qp_match else ""
    if isinstance(qp_team, list):
        qp_team = qp_team[0] if qp_team else ""
    tab_map = {"inicio": "Inicio", "partidos": "Partidos", "paises": "Países", "sedes": "Sedes", "tabla": "Tabla", "ranking": "Tabla"}
    if str(qp_tab).lower() in tab_map:
        st.session_state.tab = tab_map[str(qp_tab).lower()]
    if "tab" not in st.session_state:
        st.session_state.tab = "Inicio"
    if "selected_match" not in st.session_state:
        st.session_state.selected_match = int(fixture.iloc[0]["match_no"])
    if "selected_team" not in st.session_state:
        st.session_state.selected_team = str(teams.iloc[0]["seleccion"])
    if "selected_stadium" not in st.session_state:
        selected = str(qp_sede) if qp_sede else str(sedes_fixture.iloc[0]["estadio"])
        st.session_state.selected_stadium = selected
    if qp_sede:
        st.session_state.tab = "Sedes"
        st.session_state.selected_stadium = str(qp_sede)
    if qp_match:
        st.session_state.tab = "Partidos"
        st.session_state.selected_match = int(qp_match)
    if qp_team:
        st.session_state.tab = "Países"
        st.session_state.selected_team = str(qp_team)


def nav_tabs() -> str:
    options = ["Inicio", "Partidos", "Países", "Sedes", "Tabla"]
    current = st.session_state.get("tab", "Inicio")
    st.markdown(
        """
        <header class="app-topbar">
            <div>
                <span>Match Centre</span>
                <strong>Mundialito UP 2026</strong>
            </div>
                <em>Inicio | Partidos | Países | Sedes | Tabla</em>
        </header>
        """,
        unsafe_allow_html=True,
    )
    selected = st.radio(
        "Navegación principal",
        options,
        index=options.index(current) if current in options else 0,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.tab = selected
    return selected


def set_match(match_no: int) -> None:
    st.session_state.selected_match = int(match_no)


def set_team(team: str) -> None:
    st.session_state.selected_team = team


def set_stadium(stadium: str) -> None:
    st.session_state.selected_stadium = stadium


def app_url(tab: str, **params: object) -> str:
    query = {"tab": tab}
    query.update({key: value for key, value in params.items() if value not in [None, ""]})
    return "?" + "&".join(f"{key}={quote_plus(str(value))}" for key, value in query.items())


def clean(value: object, fallback: str = "Por definir") -> str:
    if pd.isna(value) or str(value).strip().lower() == "nan":
        return fallback
    return str(value)


def asset_data_uri(relative_path: str) -> str:
    path = PROJECT_ROOT / relative_path
    if not path.exists():
        return ""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def match_card_button(row: pd.Series, key: str, active: bool = False) -> None:
    cls = "match-tile active-card" if active else "match-tile"
    grupo = clean(row.get("grupo"), "Grupo por definir")
    local = clean(row.get("equipo_local"))
    visitante = clean(row.get("equipo_visitante"))
    codigo_local = "" if pd.isna(row.get("codigo_local")) else row.get("codigo_local")
    codigo_visitante = "" if pd.isna(row.get("codigo_visitante")) else row.get("codigo_visitante")
    match_no = int(row["match_no"])
    st.markdown(
        f"""
        <a class="card-link" target="_self" href="{app_url("partidos", match=match_no)}">
        <div class="{cls}">
            <div class="tile-meta">M{int(row["match_no"])} · {grupo} · {clean(row.get("fase"))}</div>
            <div class="tile-team">{flag_img(codigo_local, local, "sm")}<span>{local}</span></div>
            <div class="tile-team">{flag_img(codigo_visitante, visitante, "sm")}<span>{visitante}</span></div>
            <div class="tile-meta">{clean(row.get("fecha_peru"))} · {clean(row.get("hora_peru"))} · {clean(row.get("ciudad"))}</div>
            <div class="tile-venue">{clean(row.get("estadio"))}</div>
        </div>
        </a>
        """,
        unsafe_allow_html=True,
    )


def render_match_preview(datos: dict[str, pd.DataFrame]) -> None:
    fixture = datos["fact_fixture"]
    equipos = datos["dataset_dashboard"]
    jugadores = datos["fact_jugadores"]
    sedes = datos["dim_sedes"]
    match = get_match(fixture, st.session_state.selected_match)
    local = get_team(equipos, str(match["equipo_local"]))
    visitante = get_team(equipos, str(match["equipo_visitante"]))
    sede = get_stadium(sedes, str(match["estadio"]), fixture)
    render_match_centre(
        PROJECT_ROOT,
        match,
        local,
        visitante,
        sede,
        jugadores_por_equipo(jugadores, str(local["seleccion"])),
        jugadores_por_equipo(jugadores, str(visitante["seleccion"])),
        rendimiento_equipo(str(local["seleccion"]), datos["rendimiento_companero"]),
        rendimiento_equipo(str(visitante["seleccion"]), datos["rendimiento_companero"]),
        historial_equipo(str(local["seleccion"]), datos["enfrentamientos_companero"]),
        historial_equipo(str(visitante["seleccion"]), datos["enfrentamientos_companero"]),
    )


def render_inicio(datos: dict[str, pd.DataFrame]) -> None:
    equipos = datos["dataset_dashboard"]
    jugadores = datos["fact_jugadores"]
    fixture = datos["fact_fixture"]
    sedes = datos["dim_sedes"]
    resumen = resumen_torneo(equipos, jugadores, fixture, sedes)
    hero_uri = asset_data_uri("assets/branding/mundialito_hero.png")
    st.markdown(
        f"""
        <section class="home-hero">
            <img class="home-hero-bg" src="{hero_uri}" alt="Portada Mundialito UP 2026" />
            <div>
                <div class="kicker">Portada oficial del torneo</div>
                <h1>
                    <span style="display:block; white-space:nowrap;">Mundialito UP</span>
                    <span style="display:block;">2026</span>
                </h1>
                <p>Fixture, selecciones, sedes y camino al título en una experiencia deportiva interactiva.</p>
            </div>
            <div class="hero-kpis">
                <div><strong>{fmt(resumen["selecciones"])}</strong><span>selecciones</span></div>
                <div><strong>{fmt(resumen["jugadores"])}</strong><span>jugadores</span></div>
                <div><strong>{fmt(resumen["partidos"])}</strong><span>partidos</span></div>
                <div><strong>{fmt(resumen["sedes"])}</strong><span>sedes</span></div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    render_section_head("Panel visual", "metricas del torneo")
    partidos_sede = fixture.groupby("ciudad").size().sort_values(ascending=False).head(10)
    jugadores_conf = jugadores.merge(
        equipos[["seleccion", "confederacion"]], on="seleccion", how="left"
    ).groupby("confederacion").size().sort_values(ascending=False)
    posiciones = jugadores.groupby("posicion_nombre").size().sort_values(ascending=False)
    edad_grupo = equipos.groupby("grupo")["edad_promedio"].mean().sort_index()
    st.markdown(
        '<div class="viz-grid">'
        + viz_helpers.chart_card("Partidos por ciudad", partidos_sede)
        + viz_helpers.chart_card("Jugadores por confederacion", jugadores_conf, "horizontal")
        + '<div style="grid-column:1 / -1;">'
        + viz_helpers.chart_card("Distribucion de posiciones", posiciones, "pie")
        + '</div>'
        + '<div style="grid-column:1 / -1;">'
        + viz_helpers.chart_card("Edad promedio por grupo", edad_grupo, "line")
        + '</div>'
        + '</div>',
        unsafe_allow_html=True,
    )

    render_section_head("Próximos partidos", "primeros cruces del fixture")
    featured = proximos_partidos(fixture, 4)
    cols = st.columns(4)
    for idx, (_, row) in enumerate(featured.iterrows()):
        with cols[idx % 4]:
            match_card_button(row, f"home_match_{int(row['match_no'])}", active=False)
    render_section_head("Camino al título", "estructura desde octavos hasta la final")
    st.markdown(viz_helpers.bracket_html(asset_data_uri("assets/branding/trophy_final.png")), unsafe_allow_html=True)


def render_partidos(datos: dict[str, pd.DataFrame]) -> None:
    fixture = datos["fact_fixture"]
    filtros = opciones_filtros(fixture, datos["dataset_dashboard"])
    render_section_head("Partidos", "fixture filtrable y previa inmediata")
    grupo = st.selectbox("Grupo", filtros["grupos"])
    filtered = filtrar_fixture(
        fixture,
        grupo,
        "Todos",
        "Todas",
        "Todas",
        "Todos",
        "Todas",
    )

    render_section_head("Próximos partidos", "primeros registros cargados")
    recent_cols = st.columns(4)
    for idx, (_, row) in enumerate(proximos_partidos(filtered if not filtered.empty else fixture, 4).iterrows()):
        with recent_cols[idx % 4]:
            match_card_button(
                row,
                f"recent_match_{int(row['match_no'])}",
                active=int(row["match_no"]) == st.session_state.selected_match,
            )

    render_section_head("Previa seleccionada", "se actualiza al elegir un partido")
    render_match_preview(datos)

    render_section_head("Todos los partidos por fecha", f"{len(filtered)} partidos")
    if filtered.empty:
        st.markdown('<div class="empty-state">No hay partidos con estos filtros.</div>', unsafe_allow_html=True)
        return
    for fecha_val, day_df in filtered.groupby("fecha_peru", sort=True):
        st.markdown(
            f'<div class="date-band"><strong>{fecha_val}</strong><span>{len(day_df)} partidos</span></div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(3)
        for idx, (_, row) in enumerate(day_df.iterrows()):
            with cols[idx % 3]:
                match_card_button(
                    row,
                    f"all_match_{int(row['match_no'])}",
                    active=int(row["match_no"]) == st.session_state.selected_match,
                )


def render_paises(datos: dict[str, pd.DataFrame]) -> None:
    equipos = datos["dataset_dashboard"].sort_values(["grupo", "seleccion"])
    jugadores = datos["fact_jugadores"]
    fixture = datos["fact_fixture"]
    selected = st.session_state.selected_team
    team = get_team(equipos, selected)
    team_fixture = fixture_por_equipo(fixture, selected)
    clubs = clubes_por_seleccion(jugadores, selected)
    render_section_head("Países", "perfil y selector lateral")
    side, main_col = st.columns([0.72, 1.9], gap="large")
    with side:
        cards = []
        for _, row in equipos.iterrows():
            active = " active-card" if row["seleccion"] == selected else ""
            cards.append(
                f'<a class="card-link" target="_self" href="{app_url("paises", team=row["seleccion"])}">'
                f'<div class="country-card country-card-compact{active}">'
                f'{flag_img(row["codigo_fifa"], row["seleccion"], "sm")}'
                f'<div><strong>{escape(str(row["seleccion"]))}</strong>'
                f'<span>Grupo {escape(str(row["grupo"]))} | {escape(str(row["confederacion"]))}</span></div>'
                f'</div></a>'
            )
        st.markdown(
            '<aside class="country-rail"><div class="panel-title">Selecciones</div>'
            + "".join(cards)
            + "</aside>",
            unsafe_allow_html=True,
        )

    with main_col:
        render_section_head("Perfil del país", selected)
        c1, c2 = st.columns([0.95, 1.15])
        with c1:
            st.markdown(
                f"""
                <div class="profile-card profile-card-featured">
                    {flag_img(team.get("codigo_fifa", ""), team.get("seleccion", ""), "xl")}
                    <h2>{team.get("seleccion", "")}</h2>
                    <p>Grupo {team.get("grupo", "-")} | {team.get("confederacion", "-")}</p>
                    <div class="mini-kpi"><span>Jugadores</span><strong>{fmt(team.get("cantidad_jugadores", "-"))}</strong></div>
                    <div class="mini-kpi"><span>Edad promedio</span><strong>{fmt(team.get("edad_promedio", "-"))}</strong></div>
                    <div class="mini-kpi"><span>Altura promedio</span><strong>{fmt(team.get("altura_promedio", "-"))}</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown('<div class="panel-title">Partidos que jugará</div>', unsafe_allow_html=True)
            for _, match in team_fixture.iterrows():
                match_card_button(
                    match,
                    f"profile_match_{selected}_{int(match['match_no'])}",
                    active=int(match["match_no"]) == st.session_state.selected_match,
                )

        lower1, lower2 = st.columns([1.2, 0.8])
        with lower1:
            st.markdown('<div class="panel-title">Jugadores</div>', unsafe_allow_html=True)
            st.markdown(player_rows(jugadores_por_equipo(jugadores, selected), 26), unsafe_allow_html=True)
        with lower2:
            st.markdown('<div class="panel-title">Clubes más repetidos</div>', unsafe_allow_html=True)
            for _, club in clubs.iterrows():
                st.markdown(
                    f'<div class="club-row"><strong>{club["club_limpio"]}</strong><span>{int(club["jugadores"])} jugadores</span></div>',
                    unsafe_allow_html=True,
                )


def candidatos_rendimiento(nombre: str) -> set[str]:
    base = normalizar_texto(nombre)
    candidatos = {base}
    alias = ALIASES_RENDIMIENTO.get(base)
    if alias:
        candidatos.add(alias)
    for key, value in ALIASES_RENDIMIENTO.items():
        if value == base:
            candidatos.add(key)
    return {item for item in candidatos if item}


def buscar_rendimiento_equipo(nombre: str, rendimiento: pd.DataFrame) -> pd.Series:
    if rendimiento.empty:
        return pd.Series(dtype=object)
    df = rendimiento.copy()
    for col in ["team_name", "common_name", "country"]:
        if col not in df.columns:
            df[col] = ""
    if "_country_norm" not in df.columns:
        df["_country_norm"] = df["country"].apply(normalizar_texto)
        df["_common_norm"] = df["common_name"].apply(normalizar_texto)
        df["_team_norm"] = df["team_name"].apply(normalizar_texto)
    candidatos = candidatos_rendimiento(nombre)
    exact = df[df["_country_norm"].isin(candidatos) | df["_common_norm"].isin(candidatos)]
    if not exact.empty:
        return exact.iloc[0]
    contains = df[
        df["_team_norm"].apply(lambda value: any(item in value for item in candidatos))
        | df["_common_norm"].apply(lambda value: any(item in value for item in candidatos))
    ]
    if not contains.empty:
        return contains.iloc[0]
    return pd.Series(dtype=object)


def construir_ranking_integral(datos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    equipos = datos["dataset_dashboard"].copy()
    rendimiento = datos["rendimiento_companero"].copy()
    registros = []
    for _, equipo in equipos.iterrows():
        row = buscar_rendimiento_equipo(str(equipo["seleccion"]), rendimiento)
        registros.append(
            {
                "Selección": equipo.get("seleccion", ""),
                "Grupo": equipo.get("grupo", ""),
                "Confederación": equipo.get("confederacion", ""),
                "Jugadores": equipo.get("cantidad_jugadores", 0),
                "Edad prom.": equipo.get("edad_promedio", pd.NA),
                "Altura prom.": equipo.get("altura_promedio", pd.NA),
                "Arqueros": equipo.get("arqueros", 0),
                "Defensas": equipo.get("defensas", 0),
                "Medios": equipo.get("mediocampistas", 0),
                "Delanteros": equipo.get("delanteros", 0),
                "Partidos grupo": equipo.get("partidos_fixture", 0),
                "Rivales": equipo.get("rivales_grupo", ""),
                "PJ rend.": row.get("matches_played", pd.NA),
                "Victorias": row.get("wins", pd.NA),
                "Empates": row.get("draws", pd.NA),
                "Derrotas": row.get("losses", pd.NA),
                "PPG": row.get("points_per_game", pd.NA),
                "GF/P": row.get("goals_scored_per_match", pd.NA),
                "GC/P": row.get("goals_conceded_per_match", pd.NA),
                "Valla invicta %": row.get("clean_sheet_percentage", pd.NA),
                "Posesión %": row.get("average_possession", pd.NA),
                "Tiros al arco": row.get("shots_on_target", pd.NA),
                "Faltas": row.get("fouls", pd.NA),
            }
        )
    ranking = pd.DataFrame(registros)
    metricas = [
        "Jugadores",
        "Edad prom.",
        "Altura prom.",
        "Arqueros",
        "Defensas",
        "Medios",
        "Delanteros",
        "Partidos grupo",
        "PJ rend.",
        "Victorias",
        "Empates",
        "Derrotas",
        "PPG",
        "GF/P",
        "GC/P",
        "Valla invicta %",
        "Posesión %",
        "Tiros al arco",
        "Faltas",
    ]
    for col in metricas:
        ranking[col] = pd.to_numeric(ranking[col], errors="coerce")
    ranking = ranking.sort_values("PPG", ascending=False, na_position="last").reset_index(drop=True)
    ranking.insert(0, "Rank", range(1, len(ranking) + 1))
    return ranking


def render_ranking(datos: dict[str, pd.DataFrame]) -> None:
    render_section_head("Tabla comparativa", "selecciones y rendimiento previo")
    st.markdown(
        """
        <div class="empty-state" style="text-align:left;">
            Esta tabla cruza el perfil del plantel con rendimiento internacional: edad,
            altura, posiciones, puntos por partido, goles, defensa, posesión y rivales.
            No es un ranking oficial: se puede ordenar por la variable que el usuario elija.
        </div>
        """,
        unsafe_allow_html=True,
    )
    ranking = construir_ranking_integral(datos)
    metric_options = [
        "PPG",
        "GF/P",
        "GC/P",
        "Valla invicta %",
        "Posesión %",
        "Tiros al arco",
        "Victorias",
        "Derrotas",
        "Edad prom.",
        "Altura prom.",
    ]
    c1, c2, c3, c4 = st.columns([1.05, 1.05, 1.2, 0.85])
    with c1:
        categoria = st.selectbox("Categoría", ["Todas", "Confederación", "Grupo"])
    if categoria == "Confederación":
        valores = ["Todas"] + sorted(ranking["Confederación"].dropna().unique().tolist())
        campo_categoria = "Confederación"
    elif categoria == "Grupo":
        valores = ["Todos"] + sorted(ranking["Grupo"].dropna().astype(str).unique().tolist())
        campo_categoria = "Grupo"
    else:
        valores = ["Todas"]
        campo_categoria = ""
    with c2:
        valor_categoria = st.selectbox("Valor", valores)
    with c3:
        columna = st.selectbox("Indicador de comparación", metric_options)
    with c4:
        orden = st.selectbox("Orden", ["Mayor a menor", "Menor a mayor"])

    filtrado = ranking.copy()
    if campo_categoria and valor_categoria not in ["Todas", "Todos"]:
        filtrado = filtrado[filtrado[campo_categoria].astype(str) == str(valor_categoria)]

    col_min = float(pd.to_numeric(filtrado[columna], errors="coerce").min()) if not filtrado.empty else 0.0
    col_max = float(pd.to_numeric(filtrado[columna], errors="coerce").max()) if not filtrado.empty else 0.0
    if col_min == col_max:
        rango = (col_min, col_max)
        st.slider("Rango", min_value=col_min, max_value=col_max + 1.0, value=(col_min, col_max + 1.0), disabled=True)
    else:
        rango = st.slider("Rango", min_value=col_min, max_value=col_max, value=(col_min, col_max))
    filtrado = filtrado[
        pd.to_numeric(filtrado[columna], errors="coerce").between(rango[0], rango[1], inclusive="both")
    ]
    filtrado = filtrado.sort_values(columna, ascending=orden == "Menor a mayor").reset_index(drop=True)
    filtrado["Rank"] = range(1, len(filtrado) + 1)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Selecciones", len(filtrado))
    k2.metric("PPG promedio", fmt(filtrado["PPG"].mean() if not filtrado.empty else 0))
    k3.metric("GF/P promedio", fmt(filtrado["GF/P"].mean() if not filtrado.empty else 0))
    k4.metric("Edad promedio", fmt(filtrado["Edad prom."].mean() if not filtrado.empty else 0))

    columnas_tabla = [
        "Rank",
        "Selección",
        "Grupo",
        "Confederación",
        "PPG",
        "GF/P",
        "GC/P",
        "Valla invicta %",
        "Posesión %",
        "Victorias",
        "Edad prom.",
        "Altura prom.",
        "Jugadores",
        "Arqueros",
        "Defensas",
        "Medios",
        "Delanteros",
        "Rivales",
    ]
    st.dataframe(
        filtrado[columnas_tabla],
        use_container_width=True,
        hide_index=True,
        column_config={
            "PPG": st.column_config.NumberColumn("PPG", format="%.2f"),
            "GF/P": st.column_config.NumberColumn("GF/P", format="%.2f"),
            "GC/P": st.column_config.NumberColumn("GC/P", format="%.2f"),
            "Valla invicta %": st.column_config.NumberColumn("Valla invicta %", format="%.0f%%"),
            "Posesión %": st.column_config.NumberColumn("Posesión %", format="%.0f%%"),
            "Edad prom.": st.column_config.NumberColumn("Edad prom.", format="%.1f"),
            "Altura prom.": st.column_config.NumberColumn("Altura prom.", format="%.1f"),
        },
    )


def sede_points(sedes: pd.DataFrame, fixture: pd.DataFrame) -> pd.DataFrame:
    fixture_sedes = fixture[["estadio", "ciudad", "pais_sede"]].drop_duplicates()
    df = fixture_sedes.merge(
        sedes[["estadio", "capacidad_aprox", "latitud", "longitud"]],
        on="estadio",
        how="left",
    )
    manual = {
        "Estadio Azteca": (19.3029, -99.1505, 87523),
        "SoFi Stadium": (33.9535, -118.3392, 70240),
        "Levi's Stadium": (37.4030, -121.9700, 68500),
        "Arrowhead Stadium": (39.0490, -94.4839, 76416),
        "MetLife Stadium": (40.8135, -74.0745, 82500),
    }
    for idx, row in df.iterrows():
        if pd.isna(row.get("latitud")) and row["estadio"] in manual:
            lat, lon, cap = manual[row["estadio"]]
            df.loc[idx, "latitud"] = lat
            df.loc[idx, "longitud"] = lon
            df.loc[idx, "capacidad_aprox"] = cap
    return df


def map_svg(sedes_df: pd.DataFrame, selected: str) -> str:
    def project(lat: float, lon: float) -> tuple[float, float]:
        x = (lon + 128) / 62 * 1000
        y = (54 - lat) / 36 * 520
        return max(20, min(980, x)), max(20, min(500, y))

    points = []
    for _, row in sedes_df.dropna(subset=["latitud", "longitud"]).iterrows():
        x, y = project(float(row["latitud"]), float(row["longitud"]))
        active = row["estadio"] == selected
        cls = "venue-point active" if active else "venue-point"
        label = str(row["estadio"])
        url = f"?tab=sedes&sede={label.replace('&', '%26').replace(' ', '%20')}"
        points.append(
            f'<a target="_self" href="{url}"><circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{12 if active else 8}"></circle>'
            f'<text x="{x + 12:.1f}" y="{y - 8:.1f}">{label}</text></a>'
        )
    return f"""
    <svg class="venue-map" viewBox="0 0 1000 520" role="img" aria-label="Mapa de sedes">
      <rect x="0" y="0" width="1000" height="520" rx="28"></rect>
      <path d="M120 70 C260 20 390 40 470 120 C520 170 520 250 480 310 C430 390 300 430 170 390 C70 360 40 250 80 150 Z" class="land"></path>
      <path d="M500 130 C640 70 850 90 920 190 C980 280 900 410 740 430 C610 450 500 380 500 280 Z" class="land"></path>
      <path d="M360 360 C460 330 560 360 610 440 C520 505 400 500 315 445 Z" class="land mexico"></path>
      <text x="170" y="112" class="map-label">Canadá</text>
      <text x="650" y="176" class="map-label">Estados Unidos</text>
      <text x="405" y="438" class="map-label">México</text>
      {"".join(points)}
    </svg>
    """


def render_sedes(datos: dict[str, pd.DataFrame]) -> None:
    sedes = datos["dim_sedes"]
    fixture = datos["fact_fixture"]
    points = sede_points(sedes, fixture)
    valid_names = set(points["estadio"].dropna())
    if st.session_state.selected_stadium not in valid_names:
        st.session_state.selected_stadium = str(points.iloc[0]["estadio"])
    selected = st.session_state.selected_stadium
    render_section_head("Sedes", "mapa real de Norteamerica")
    components.html(viz_helpers.map_leaflet_html(points, selected), height=540, scrolling=False)
    selected_row = points[points["estadio"] == selected].iloc[0]
    stadium = get_stadium(sedes, selected, fixture)
    stadium_fixture = fixture_por_estadio(fixture, selected)
    data_uri = stadium_data_uri(PROJECT_ROOT, selected)
    media = (
        f'<img src="{data_uri}" alt="{selected}" />'
        if data_uri
        else '<div class="pitch-lines"></div>'
    )
    st.markdown(
        f"""
        <section class="stadium-detail">
            <div class="stadium-media">{media}</div>
            <div>
                <div class="kicker">Sede del torneo</div>
                <h2>{selected}</h2>
                <div class="chip-row">
                    <span class="chip">{selected_row["ciudad"]}</span>
                    <span class="chip">{selected_row["pais_sede"]}</span>
                    <span class="chip">Cap. {fmt(stadium.get("capacidad_aprox", "-"))}</span>
                    <span class="chip">{len(stadium_fixture)} partidos</span>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    render_section_head("Todas las sedes", "tarjetas conectadas al mapa")
    cols = st.columns(3)
    for idx, (_, row) in enumerate(points.sort_values(["pais_sede", "ciudad"]).iterrows()):
        with cols[idx % 3]:
            active = " active-card" if row["estadio"] == selected else ""
            st.markdown(
                f"""
                <a class="card-link" target="_self" href="{app_url("sedes", sede=row["estadio"])}">
                <div class="venue-card{active}">
                    <strong>{row["estadio"]}</strong>
                    <span>{row["ciudad"]} · {row["pais_sede"]}</span>
                </div>
                </a>
                """,
                unsafe_allow_html=True,
            )

    render_section_head("Partidos en la sede", selected)
    cols_matches = st.columns(3)
    for idx, (_, row) in enumerate(stadium_fixture.iterrows()):
        with cols_matches[idx % 3]:
            match_card_button(row, f"stadium_match_{selected}_{int(row['match_no'])}")


def main() -> None:
    apply_global_styles()
    datos = load_data(data_version())
    init_state(datos)
    tab = nav_tabs()
    st.markdown('<div class="app-spacer"></div>', unsafe_allow_html=True)
    if tab == "Inicio":
        render_inicio(datos)
    elif tab == "Partidos":
        render_partidos(datos)
    elif tab == "Países":
        render_paises(datos)
    elif tab == "Sedes":
        render_sedes(datos)
    else:
        render_ranking(datos)


if __name__ == "__main__":
    main()