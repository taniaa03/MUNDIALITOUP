from __future__ import annotations

import base64
import json
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
    tab_map = {"inicio": "Inicio", "partidos": "Partidos", "paises": "Países", "sedes": "Sedes"}
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
    options = ["Inicio", "Partidos", "Países", "Sedes"]
    current = st.session_state.get("tab", "Inicio")
    st.markdown(
        """
        <header class="app-topbar">
            <div>
                <span>Match Centre</span>
                <strong>Mundialito UP 2026</strong>
            </div>
            <em>Inicio | Partidos | Países | Sedes</em>
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


def chart_card(title: str, series: pd.Series, variant: str = "bar") -> str:
    data = series.dropna()
    if data.empty:
        return f'<div class="viz-card"><h3>{escape(title)}</h3><div class="empty-mini">Sin datos</div></div>'
    data = data.head(8)
    max_value = float(data.max()) if float(data.max()) else 1.0
    if variant == "line":
        values = [float(v) for v in data.tolist()]
        max_v = max(values) or 1.0
        min_v = min(values)
        span = max(max_v - min_v, 1.0)
        points = []
        width = 320
        height = 120
        for index, value in enumerate(values):
            x = 18 + (index / max(len(values) - 1, 1)) * (width - 36)
            y = 16 + (1 - ((value - min_v) / span)) * (height - 32)
            points.append(f"{x:.1f},{y:.1f}")
        labels = "".join(
            f'<span>{escape(str(label))}</span>' for label in data.index.astype(str).tolist()
        )
        circles = []
        for point in points:
            cx, cy = point.split(",")
            circles.append(f'<circle cx="{cx}" cy="{cy}" r="4"></circle>')
        return (
            f'<div class="viz-card"><h3>{escape(title)}</h3>'
            f'<svg class="line-viz" viewBox="0 0 {width} {height}" preserveAspectRatio="none">'
            f'<polyline points="{" ".join(points)}"></polyline>'
            f'{"".join(circles)}'
            f'</svg><div class="viz-labels">{labels}</div></div>'
        )
    rows = []
    for label, value in data.items():
        pct = max(5, min(100, (float(value) / max_value) * 100))
        rows.append(
            f'<div class="bar-row"><div class="bar-top"><span>{escape(str(label))}</span>'
            f'<strong>{fmt(value)}</strong></div><div class="bar-track">'
            f'<i style="width:{pct:.1f}%"></i></div></div>'
        )
    return f'<div class="viz-card"><h3>{escape(title)}</h3>{"".join(rows)}</div>'


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
        <section class="home-hero" style="--hero-image: url('{hero_uri}')">
            <div>
                <div class="kicker">Portada oficial del torneo</div>
                <h1>Mundialito UP 2026</h1>
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
        + chart_card("Partidos por ciudad", partidos_sede)
        + chart_card("Jugadores por confederacion", jugadores_conf)
        + chart_card("Distribucion de posiciones", posiciones)
        + chart_card("Edad promedio por grupo", edad_grupo, "line")
        + '</div>',
        unsafe_allow_html=True,
    )

    render_section_head("Partidos destacados", "primeros cruces del fixture")
    featured = proximos_partidos(fixture, 4)
    cols = st.columns(4)
    for idx, (_, row) in enumerate(featured.iterrows()):
        with cols[idx % 4]:
            match_card_button(row, f"home_match_{int(row['match_no'])}", active=False)
    render_section_head("Camino al título", "estructura desde octavos hasta la final")
    st.markdown(bracket_html(), unsafe_allow_html=True)


def bracket_html() -> str:
    left = "".join(f'<div class="bracket-slot">Octavos {i}</div>' for i in range(1, 9))
    quarters = "".join(f'<div class="bracket-slot">Cuartos {i}</div>' for i in range(1, 5))
    semis = "".join(f'<div class="bracket-slot">Semifinal {i}</div>' for i in range(1, 3))
    right = "".join(f'<div class="bracket-slot">Octavos {i}</div>' for i in range(9, 17))
    quarters_r = "".join(f'<div class="bracket-slot">Cuartos {i}</div>' for i in range(5, 9))
    semis_r = "".join(f'<div class="bracket-slot">Semifinal {i}</div>' for i in range(3, 5))
    cup = f'<img src="{asset_data_uri("assets/branding/trophy_final.png")}" alt="Copa Mundialito UP" />'
    return f"""
    <section class="bracket">
      <div class="bracket-col">{left}</div>
      <div class="bracket-col tight">{quarters}</div>
      <div class="bracket-col tighter">{semis}</div>
      <div class="cup-core"><div class="cup">{cup}</div><strong>Final</strong><span>Copa Mundialito UP</span></div>
      <div class="bracket-col tighter">{semis_r}</div>
      <div class="bracket-col tight">{quarters_r}</div>
      <div class="bracket-col">{right}</div>
    </section>
    """


def render_partidos(datos: dict[str, pd.DataFrame]) -> None:
    fixture = datos["fact_fixture"]
    filtros = opciones_filtros(fixture, datos["dataset_dashboard"])
    render_section_head("Partidos", "fixture filtrable y previa inmediata")
    f1, f2, f3 = st.columns(3)
    f4, f5, f6 = st.columns(3)
    grupo = f1.selectbox("Grupo", filtros["grupos"])
    pais = f2.selectbox("País", filtros["paises"])
    fecha = f3.selectbox("Fecha", filtros["fechas"])
    ciudad = f4.selectbox("Ciudad", filtros["ciudades"])
    estadio = f5.selectbox("Estadio", filtros["estadios"])
    fase = f6.selectbox("Fase", filtros["fases"])
    filtered = filtrar_fixture(fixture, grupo, pais, fecha, ciudad, estadio, fase)

    render_section_head("Partidos recientes", "primeros registros cargados")
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


def map_leaflet_html(sedes_df: pd.DataFrame, selected: str) -> str:
    venues = []
    for _, row in sedes_df.dropna(subset=["latitud", "longitud"]).iterrows():
        name = str(row["estadio"])
        venues.append(
            {
                "name": name,
                "city": str(row["ciudad"]),
                "country": str(row["pais_sede"]),
                "lat": float(row["latitud"]),
                "lon": float(row["longitud"]),
                "active": name == selected,
                "url": app_url("sedes", sede=name),
            }
        )
    payload = json.dumps(venues, ensure_ascii=False)
    return f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      <style>
        html, body {{ margin: 0; padding: 0; background: transparent; }}
        #venue-map {{
          height: 520px;
          width: 100%;
          border-radius: 28px;
          overflow: hidden;
          background: #0A1D3E;
          box-shadow: 0 24px 56px rgba(6,20,46,.16);
          border: 1px solid rgba(13,38,77,.18);
        }}
        .leaflet-container {{
          font-family: Barlow, Arial, sans-serif;
        }}
        .leaflet-tooltip {{
          border: 0;
          border-radius: 12px;
          padding: 8px 10px;
          color: #06142E;
          box-shadow: 0 12px 26px rgba(6,20,46,.18);
          font-weight: 800;
        }}
        .map-caption {{
          position: absolute;
          left: 18px;
          top: 18px;
          z-index: 600;
          padding: 10px 12px;
          border-radius: 16px;
          color: #FFFFFF;
          background: rgba(6,20,46,.86);
          border: 1px solid rgba(255,255,255,.16);
          font-weight: 900;
          text-transform: uppercase;
          letter-spacing: 0;
          pointer-events: none;
        }}
      </style>
    </head>
    <body>
      <div id="venue-map"><div class="map-caption">Sedes Norteamérica 2026</div></div>
      <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
      <script>
        const venues = {payload};
        const map = L.map('venue-map', {{
          scrollWheelZoom: false,
          zoomControl: true,
          attributionControl: false
        }});
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
          maxZoom: 18
        }}).addTo(map);
        const bounds = [];
        venues.forEach((venue) => {{
          bounds.push([venue.lat, venue.lon]);
          const marker = L.circleMarker([venue.lat, venue.lon], {{
            radius: venue.active ? 13 : 9,
            color: venue.active ? '#06142E' : '#FFFFFF',
            weight: venue.active ? 4 : 3,
            fillColor: venue.active ? '#D6A329' : '#0057D8',
            fillOpacity: venue.active ? 1 : .88
          }}).addTo(map);
          marker.bindTooltip(`<strong>${{venue.name}}</strong><br>${{venue.city}}, ${{venue.country}}`, {{
            direction: 'top',
            offset: [0, -8]
          }});
          marker.on('click', () => {{
            window.open(venue.url, '_top');
          }});
        }});
        if (bounds.length) {{
          map.fitBounds(bounds, {{ padding: [44, 44] }});
        }} else {{
          map.setView([39, -98], 3);
        }}
      </script>
    </body>
    </html>
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
    components.html(map_leaflet_html(points, selected), height=540, scrolling=False)
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
    else:
        render_sedes(datos)


if __name__ == "__main__":
    main()
