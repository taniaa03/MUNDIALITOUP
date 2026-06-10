from __future__ import annotations

import json
from html import escape
from urllib.parse import quote_plus

import pandas as pd

from ui_components import fmt


def chart_card(title: str, series: pd.Series, variant: str = "bar") -> str:
    data = series.dropna()
    if data.empty:
        return f'<div class="viz-card"><h3>{escape(title)}</h3><div class="empty-mini">Sin datos</div></div>'
    if variant != "line":
        data = data.head(8)
    if variant == "pie":
        return _pie_chart(title, data)
    if variant == "line":
        return _line_chart(title, data)
    return _bar_chart(title, data)


def bracket_html(cup_data_uri: str) -> str:
    left = "".join(f'<div class="bracket-slot">Octavos {i}</div>' for i in range(1, 9))
    quarters = "".join(f'<div class="bracket-slot">Cuartos {i}</div>' for i in range(1, 5))
    semis = "".join(f'<div class="bracket-slot">Semifinal {i}</div>' for i in range(1, 3))
    right = "".join(f'<div class="bracket-slot">Octavos {i}</div>' for i in range(9, 17))
    quarters_r = "".join(f'<div class="bracket-slot">Cuartos {i}</div>' for i in range(5, 9))
    semis_r = "".join(f'<div class="bracket-slot">Semifinal {i}</div>' for i in range(3, 5))
    cup = f'<img src="{cup_data_uri}" alt="Copa Mundialito UP" />'
    return f"""
    <section class="bracket">
      <div class="bracket-col">{left}</div>
      <div class="bracket-col tight">{quarters}</div>
      <div class="bracket-col tighter">{semis}</div>
      <div class="cup-core">
        <div class="cup">{cup}</div>
        <div class="final-match-card">
          <span>Final</span>
          <div class="final-teams">
            <strong>Finalista 1</strong>
            <i>vs</i>
            <strong>Finalista 2</strong>
          </div>
          <small>Copa Mundialito UP</small>
        </div>
      </div>
      <div class="bracket-col tighter">{semis_r}</div>
      <div class="bracket-col tight">{quarters_r}</div>
      <div class="bracket-col">{right}</div>
    </section>
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
                "url": f"?tab=sedes&sede={quote_plus(name)}",
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
      <div id="venue-map"><div class="map-caption">Sedes Norteamerica 2026</div></div>
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


def _pie_chart(title: str, data: pd.Series) -> str:
    palette = ["#0057D8", "#00B6D6", "#D6A329", "#08A045", "#0B2454", "#D72638", "#6B5DD3", "#F28C28"]
    total = float(data.sum()) or 1.0
    current = 0.0
    slices = []
    legend = []
    for index, (label, value) in enumerate(data.items()):
        color = palette[index % len(palette)]
        pct = (float(value) / total) * 100
        end = current + pct
        slices.append(f"{color} {current:.2f}% {end:.2f}%")
        legend.append(
            f'<div class="pie-legend-row"><i style="background:{color}"></i>'
            f'<span>{escape(str(label))}</span><strong>{fmt(value)} ({pct:.1f}%)</strong></div>'
        )
        current = end
    return (
        f'<div class="viz-card"><h3>{escape(title)}</h3><div class="pie-layout">'
        f'<div class="pie-chart" style="background:conic-gradient({", ".join(slices)})">'
        f'<div><strong>{fmt(data.sum())}</strong><span>jugadores</span></div></div>'
        f'<div class="pie-legend">{"".join(legend)}</div></div></div>'
    )


def _line_chart(title: str, data: pd.Series) -> str:
    values = [float(v) for v in data.tolist()]
    axis_min = float(int(min(values)))
    axis_max = float(int(max(values)) + 1)
    span = max(axis_max - axis_min, 1.0)
    points = []
    width = max(400, len(values) * 48)
    height = 120
    plot_left = 30
    plot_right = 22
    plot_top = 14
    plot_bottom = 90
    data_left = plot_left + 18
    x_labels = []
    for index, value in enumerate(values):
        x = data_left + (index / max(len(values) - 1, 1)) * (width - data_left - plot_right)
        y = plot_top + (1 - ((value - axis_min) / span)) * (plot_bottom - plot_top)
        points.append(f"{x:.1f},{y:.1f}")
        x_labels.append(
            f'<text class="axis-x-value" x="{x:.1f}" y="112">'
            f'{escape(str(data.index[index]))}</text>'
        )
    y_axis = []
    for tick in range(int(axis_min), int(axis_max) + 1):
        y = plot_top + (1 - ((tick - axis_min) / span)) * (plot_bottom - plot_top)
        y_axis.append(
            f'<line class="axis-grid" x1="{plot_left}" y1="{y:.1f}" x2="{width - plot_right}" y2="{y:.1f}"></line>'
            f'<text class="axis-value" x="{plot_left - 9}" y="{y + 3.5:.1f}">{tick}</text>'
        )
    circles = []
    for point, value in zip(points, values):
        cx, cy = point.split(",")
        label_y = max(13.0, float(cy) - 9)
        circles.append(
            f'<circle cx="{cx}" cy="{cy}" r="4"></circle>'
            f'<text class="line-value" x="{cx}" y="{label_y:.1f}">{fmt(value)}</text>'
        )
    return (
        f'<div class="viz-card"><h3>{escape(title)}</h3>'
        f'<svg class="line-viz" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet">'
        f'{"".join(y_axis)}'
        f'<line class="axis-line" x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" y2="{plot_bottom}"></line>'
        f'<polyline points="{" ".join(points)}"></polyline>'
        f'{"".join(circles)}'
        f'{"".join(x_labels)}'
        f'</svg></div>'
    )


def _bar_chart(title: str, data: pd.Series) -> str:
    max_value = float(data.max()) if float(data.max()) else 1.0
    rows = []
    for label, value in data.items():
        pct = max(5, min(100, (float(value) / max_value) * 100))
        rows.append(
            f'<div class="bar-row"><div class="bar-top"><span>{escape(str(label))}</span>'
            f'<strong>{fmt(value)}</strong></div><div class="bar-track">'
            f'<i style="width:{pct:.1f}%"></i></div></div>'
        )
    return f'<div class="viz-card"><h3>{escape(title)}</h3>{"".join(rows)}</div>'
