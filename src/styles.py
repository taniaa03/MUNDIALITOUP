from __future__ import annotations

import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800;900&family=Barlow:wght@400;500;600;700;800&display=swap');

        :root {
            --ink: #06142E;
            --ink-2: #0B2454;
            --blue: #0057D8;
            --cyan: #00B6D6;
            --gold: #D6A329;
            --green: #08A045;
            --paper: #EEF4FA;
            --line: #C8D4E5;
            --muted: #3F4B5E;
            --danger: #D72638;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 82% 0%, rgba(0,87,216,.13), transparent 32rem),
                linear-gradient(180deg, #FFFFFF 0, var(--paper) 50%, #E5EDF7 100%);
            color: var(--ink);
            font-family: "Barlow", sans-serif;
        }

        [data-testid="stHeader"] {
            background: rgba(248,251,255,.96);
            border-bottom: 1px solid rgba(160,178,205,.82);
            backdrop-filter: blur(18px);
        }

        [data-testid="stToolbar"], [data-testid="stDecoration"], footer {
            visibility: hidden;
            height: 0;
        }

        .block-container {
            max-width: 1240px;
            padding-top: 1.25rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3, .display, .nav-brand, .team-name, .score-title {
            font-family: "Barlow Condensed", sans-serif;
            letter-spacing: 0;
        }

        [data-testid="stWidgetLabel"] p {
            color: var(--ink) !important;
            font-weight: 800 !important;
        }

        div[data-baseweb="select"] > div,
        [data-testid="stTextInput"] input {
            border-radius: 14px !important;
            border-color: var(--line) !important;
            background: #FFFFFF !important;
            box-shadow: 0 12px 30px rgba(6,20,46,.06);
        }

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {
            color: var(--ink) !important;
            font-weight: 700;
        }

        .nav-shell {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 18px;
            padding: 14px 16px;
            border: 1px solid var(--line);
            border-radius: 22px;
            background: rgba(255,255,255,.88);
            box-shadow: 0 18px 42px rgba(6,20,46,.08);
        }

        .nav-brand {
            color: var(--ink);
            font-size: 1.4rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .nav-tabs {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .nav-tabs a,
        .action-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 38px;
            border-radius: 999px;
            padding: 9px 13px;
            color: var(--ink);
            text-decoration: none;
            font-size: .8rem;
            font-weight: 900;
            text-transform: uppercase;
            border: 1px solid var(--line);
            background: #FFFFFF;
            transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
        }

        .nav-tabs a:hover,
        .action-link:hover {
            transform: translateY(-1px);
            box-shadow: 0 12px 28px rgba(0,87,216,.14);
        }

        .nav-tabs a.active,
        .action-link.primary {
            color: #FFFFFF;
            border-color: transparent;
            background: linear-gradient(135deg, var(--blue), var(--ink));
        }

        .hero {
            position: relative;
            min-height: 390px;
            display: grid;
            align-items: end;
            padding: 30px;
            overflow: hidden;
            border-radius: 28px;
            color: #FFFFFF;
            background:
                radial-gradient(circle at 76% 24%, rgba(214,163,41,.44), transparent 30%),
                linear-gradient(135deg, var(--blue), var(--ink) 58%, #087143);
            box-shadow: 0 30px 80px rgba(6,20,46,.18);
        }

        .hero:before {
            content: "";
            position: absolute;
            inset: 0;
            opacity: .14;
            background-image:
                linear-gradient(rgba(255,255,255,.48) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,.48) 1px, transparent 1px);
            background-size: 46px 46px;
        }

        .hero-content {
            position: relative;
            z-index: 1;
        }

        .kicker {
            color: rgba(255,255,255,.72);
            font-size: .78rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .hero h1 {
            max-width: 760px;
            margin: 8px 0 22px;
            color: #FFFFFF;
            font-size: clamp(3rem, 7vw, 6.5rem);
            line-height: .82;
            font-weight: 900;
            text-transform: uppercase;
        }

        .metric-grid,
        .two-grid,
        .three-grid,
        .group-grid,
        .fixture-grid,
        .players-grid,
        .result-grid {
            display: grid;
            gap: 14px;
        }

        .metric-grid {
            grid-template-columns: repeat(4, minmax(0,1fr));
        }

        .metric-card {
            border-radius: 18px;
            padding: 16px;
            background: rgba(255,255,255,.13);
            border: 1px solid rgba(255,255,255,.22);
            backdrop-filter: blur(12px);
        }

        .metric-card strong {
            display: block;
            color: #FFFFFF;
            font-family: "Barlow Condensed", sans-serif;
            font-size: 2.15rem;
            font-weight: 900;
            line-height: .9;
        }

        .metric-card span {
            display: block;
            margin-top: 7px;
            color: rgba(255,255,255,.74);
            font-size: .74rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .section {
            margin-top: 22px;
        }

        .section-head {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 16px;
            margin: 0 0 14px;
        }

        .section-head h2 {
            margin: 0;
            color: var(--ink);
            font-size: 2.05rem;
            line-height: .9;
            font-weight: 900;
            text-transform: uppercase;
        }

        .section-head span {
            color: var(--muted);
            font-size: .75rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .card-link {
            display: block;
            color: inherit !important;
            text-decoration: none !important;
        }

        .card-link:focus-visible {
            outline: 3px solid rgba(214,163,41,.85);
            outline-offset: 4px;
            border-radius: 24px;
        }

        .panel,
        .match-card,
        .group-card,
        .team-card,
        .stadium-panel,
        .comparison-panel,
        .squad-panel,
        .search-card {
            border-radius: 24px;
            background: #FFFFFF;
            border: 1px solid var(--line);
            box-shadow: 0 22px 54px rgba(6,20,46,.09);
            overflow: hidden;
        }

        .panel {
            padding: 20px;
        }

        .two-grid {
            grid-template-columns: 1fr 1fr;
        }

        .three-grid {
            grid-template-columns: repeat(3, minmax(0,1fr));
        }

        .group-grid {
            grid-template-columns: repeat(4, minmax(0,1fr));
        }

        .fixture-grid {
            grid-template-columns: repeat(3, minmax(0,1fr));
        }

        .group-card,
        .match-card,
        .team-card.clickable,
        .stadium-link {
            display: block;
            color: var(--ink) !important;
            text-decoration: none !important;
            cursor: pointer;
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
        }

        .group-card:hover,
        .match-card:hover,
        .team-card.clickable:hover,
        .stadium-link:hover {
            transform: translateY(-3px);
            border-color: rgba(0,87,216,.38);
            box-shadow: 0 28px 64px rgba(0,87,216,.16);
        }

        .group-card.active,
        .match-card.active {
            color: #FFFFFF !important;
            border-color: transparent;
            background: linear-gradient(135deg, var(--blue), var(--ink));
            box-shadow: 0 24px 58px rgba(0,87,216,.22);
        }

        .group-card {
            min-height: 150px;
            padding: 16px;
        }

        .group-title,
        .match-title {
            color: inherit;
            font-family: "Barlow Condensed", sans-serif;
            font-size: 1.55rem;
            font-weight: 900;
            line-height: .95;
            text-transform: uppercase;
        }

        .flag-row {
            display: flex;
            gap: 7px;
            flex-wrap: wrap;
            margin-top: 14px;
        }

        .meta-line {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            color: var(--muted);
            font-size: .72rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .active .meta-line {
            color: rgba(255,255,255,.76);
        }

        .match-card {
            min-height: 198px;
            padding: 16px;
        }

        .match-teams {
            display: grid;
            gap: 10px;
            margin: 14px 0;
        }

        .team-line {
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 0;
            font-size: 1.1rem;
            font-weight: 900;
        }

        .team-line span {
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .flag {
            object-fit: cover;
            border-radius: 999px;
            border: 3px solid #FFFFFF;
            background: #EEF3F8;
            box-shadow: 0 8px 20px rgba(6,20,46,.18);
            vertical-align: middle;
        }

        .flag-sm { width: 32px; height: 32px; }
        .flag-lg { width: 64px; height: 64px; }
        .flag-xl { width: 96px; height: 96px; }

        .match-centre {
            display: grid;
            grid-template-columns: minmax(0,1fr) minmax(350px,.9fr) minmax(0,1fr);
            gap: 16px;
            align-items: stretch;
        }

        .team-card {
            min-height: 440px;
            padding: 26px;
            text-align: center;
            background:
                linear-gradient(180deg, rgba(0,87,216,.10), rgba(255,255,255,0) 42%),
                #FFFFFF;
        }

        .team-card.away {
            background:
                linear-gradient(180deg, rgba(8,160,69,.12), rgba(255,255,255,0) 42%),
                #FFFFFF;
        }

        .team-name {
            margin-top: 18px;
            color: var(--ink);
            font-size: clamp(2.4rem, 5vw, 4.1rem);
            line-height: .82;
            font-weight: 900;
            text-transform: uppercase;
        }

        .team-sub {
            margin-top: 10px;
            color: var(--muted);
            font-size: .82rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .stat-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0,1fr));
            gap: 10px;
            margin-top: 22px;
            text-align: left;
        }

        .stat {
            border-radius: 16px;
            padding: 13px;
            background: #F7FAFE;
            border: 1px solid var(--line);
        }

        .stat span {
            display: block;
            color: var(--muted);
            font-size: .68rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .stat strong {
            display: block;
            margin-top: 4px;
            color: var(--ink);
            font-family: "Barlow Condensed", sans-serif;
            font-size: 1.45rem;
            font-weight: 900;
        }

        .stadium-panel {
            min-height: 440px;
            color: #FFFFFF;
            background: transparent;
            border: 0;
            box-shadow: none;
            overflow: visible;
        }

        .stadium-media {
            position: relative;
            height: 260px;
            overflow: visible;
            background: transparent;
        }

        .stadium-media img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            display: block;
        }

        .pitch-lines {
            position: absolute;
            inset: 20px;
            border: 2px solid rgba(255,255,255,.25);
            border-radius: 20px;
        }

        .stadium-copy {
            padding: 20px;
            background: var(--ink);
            border-radius: 22px;
            box-shadow: 0 18px 42px rgba(6,20,46,.12);
        }

        .stadium-copy h2 {
            margin: 0;
            color: #FFFFFF;
            font-family: "Barlow Condensed", sans-serif;
            font-size: 2.45rem;
            line-height: .86;
            font-weight: 900;
            text-transform: uppercase;
        }

        .chip-row {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 16px;
        }

        .chip {
            border-radius: 999px;
            padding: 8px 10px;
            color: inherit;
            background: rgba(255,255,255,.12);
            border: 1px solid rgba(255,255,255,.18);
            font-size: .74rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .stadium-copy .chip {
            color: #FFFFFF;
        }

        .comparison-panel,
        .squad-panel {
            margin-top: 18px;
            padding: 22px;
        }

        .compare-row {
            display: grid;
            grid-template-columns: minmax(0,1fr) 200px minmax(0,1fr);
            gap: 12px;
            align-items: center;
            padding: 12px 0;
            border-top: 1px solid var(--line);
        }

        .compare-row:first-child {
            border-top: 0;
        }

        .compare-row strong {
            color: var(--ink);
            font-family: "Barlow Condensed", sans-serif;
            font-size: 1.55rem;
            font-weight: 900;
        }

        .compare-row strong:last-child {
            text-align: right;
        }

        .compare-row span {
            color: var(--muted);
            text-align: center;
            font-size: .78rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .players-grid {
            grid-template-columns: 1fr 1fr;
        }

        .player-row {
            display: flex;
            align-items: center;
            gap: 10px;
            min-height: 54px;
            margin-top: 8px;
            padding: 10px;
            border-radius: 14px;
            border: 1px solid var(--line);
            background: #F7FAFE;
        }

        .pos-icon {
            width: 34px;
            height: 34px;
            display: grid;
            place-items: center;
            flex: 0 0 auto;
            border-radius: 12px;
            color: var(--ink);
            background: #E8EEF7;
        }

        .player-row strong {
            display: block;
            color: var(--ink);
            font-size: .92rem;
            font-weight: 900;
            line-height: 1.05;
        }

        .player-row span {
            display: block;
            margin-top: 3px;
            color: var(--muted);
            font-size: .75rem;
            font-weight: 800;
        }

        .search-card {
            padding: 14px;
            color: var(--ink) !important;
            text-decoration: none !important;
        }

        .result-grid {
            grid-template-columns: repeat(4, minmax(0,1fr));
        }

        .status-win,
        .status-loss,
        .status-draw {
            color: #FFFFFF !important;
        }

        .status-win { background: var(--green); }
        .status-loss { background: var(--danger); }
        .status-draw { background: var(--muted); }

        .empty-state {
            border-radius: 20px;
            padding: 22px;
            color: var(--muted);
            background: #FFFFFF;
            border: 1px dashed var(--line);
            font-weight: 800;
        }

        .app-spacer {
            height: 14px;
        }

        .app-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 10px;
            padding: 16px 18px;
            border-radius: 26px;
            color: #FFFFFF;
            background:
                linear-gradient(135deg, rgba(6,20,46,.98), rgba(0,87,216,.92)),
                #06142E;
            border: 1px solid rgba(255,255,255,.16);
            box-shadow: 0 22px 50px rgba(6,20,46,.18);
        }

        .app-topbar span {
            display: block;
            color: var(--gold);
            font-size: .72rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .app-topbar strong {
            display: block;
            margin-top: 2px;
            color: #FFFFFF;
            font-family: "Barlow Condensed", sans-serif;
            font-size: 1.75rem;
            line-height: .9;
            font-weight: 900;
            text-transform: uppercase;
        }

        .app-topbar em {
            color: rgba(255,255,255,.82);
            font-style: normal;
            font-size: .76rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        div[role="radiogroup"] {
            display: flex;
            gap: 10px;
            padding: 10px;
            margin-bottom: 18px;
            border-radius: 24px;
            border: 1px solid #AFC0D8;
            background: linear-gradient(135deg, #FFFFFF, #EEF5FF);
            box-shadow: 0 20px 48px rgba(6,20,46,.12);
        }

        div[role="radiogroup"] label {
            flex: 1;
            border-radius: 999px;
            padding: 10px 12px;
            justify-content: center;
            background: #FFFFFF !important;
            border: 1px solid #B8C8DD;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,.75);
        }

        div[role="radiogroup"] label p {
            color: var(--ink) !important;
            font-weight: 900 !important;
            text-transform: uppercase;
        }

        div[role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(135deg, var(--blue), var(--ink)) !important;
            border-color: transparent;
            box-shadow: 0 14px 30px rgba(0,87,216,.24);
        }

        div[role="radiogroup"] label:has(input:checked) p {
            color: #FFFFFF !important;
        }

        .home-hero {
            min-height: 460px;
            display: grid;
            grid-template-columns: minmax(0,1.2fr) minmax(320px,.8fr);
            gap: 24px;
            align-items: end;
            padding: 34px;
            border-radius: 30px;
            color: #FFFFFF;
            background:
                linear-gradient(90deg, rgba(4,14,34,.92) 0%, rgba(4,14,34,.78) 36%, rgba(4,14,34,.26) 68%, rgba(4,14,34,.1) 100%),
                linear-gradient(135deg, var(--blue), var(--ink));
            box-shadow: 0 30px 80px rgba(6,20,46,.18);
            position: relative;
            overflow: hidden;
        }

        .home-hero > img.home-hero-bg {
            position: absolute !important;
            inset: 0 !important;
            width: 100% !important;
            height: 100% !important;
            max-width: none !important;
            margin: 0 !important;
            object-fit: cover !important;
            object-position: center !important;
            z-index: 0 !important;
        }

        .home-hero:before {
            content: "";
            position: absolute;
            inset: 0;
            opacity: .10;
            z-index: 2;
            background-image:
                linear-gradient(rgba(255,255,255,.46) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,.46) 1px, transparent 1px);
            background-size: 46px 46px;
        }

        .home-hero:after {
            content: "";
            position: absolute;
            inset: 0;
            z-index: 1;
            background: linear-gradient(90deg, rgba(4,14,34,.94) 0%, rgba(4,14,34,.78) 38%, rgba(4,14,34,.28) 72%, rgba(4,14,34,.12) 100%);
        }

        .home-hero > div {
            position: relative;
            z-index: 3;
        }

        .home-hero h1 {
            width: fit-content;
            max-width: 100%;
            margin: 8px 0 12px;
            color: #FFFFFF;
            font-size: clamp(2.8rem, 5vw, 4.5rem);
            line-height: .86;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: -.025em;
        }

        .home-hero h1 span {
            display: block;
        }

        .home-hero p {
            max-width: 640px;
            margin: 0;
            color: rgba(255,255,255,.9);
            font-size: 1.08rem;
            font-weight: 700;
        }

        .hero-kpis {
            display: grid;
            grid-template-columns: repeat(2, minmax(0,1fr));
            gap: 12px;
        }

        .hero-kpis div {
            min-height: 116px;
            border-radius: 20px;
            padding: 16px;
            background: rgba(255,255,255,.13);
            border: 1px solid rgba(255,255,255,.22);
            backdrop-filter: blur(12px);
        }

        .hero-kpis strong {
            display: block;
            color: #FFFFFF;
            font-family: "Barlow Condensed", sans-serif;
            font-size: 2.5rem;
            line-height: .9;
            font-weight: 900;
        }

        .hero-kpis span {
            display: block;
            margin-top: 8px;
            color: rgba(255,255,255,.72);
            font-size: .76rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .chart-title,
        .panel-title {
            margin: 14px 0 8px;
            color: var(--ink);
            font-family: "Barlow Condensed", sans-serif;
            font-size: 1.35rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .viz-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 16px;
            margin-bottom: 22px;
        }

        .viz-grid > div > .viz-card {
            width: 100%;
            box-sizing: border-box;
        }

        .viz-grid > div:last-child .line-viz {
            height: 260px;
        }

        .viz-card {
            min-height: 260px;
            padding: 18px;
            border-radius: 24px;
            background:
                linear-gradient(180deg, rgba(255,255,255,.98), rgba(244,248,253,.98)),
                #FFFFFF;
            border: 1px solid #C6D4E7;
            box-shadow: 0 20px 48px rgba(6,20,46,.09);
        }

        .viz-card h3 {
            margin: 0 0 15px;
            color: var(--ink);
            font-family: "Barlow Condensed", sans-serif;
            font-size: 1.5rem;
            line-height: .95;
            font-weight: 900;
            text-transform: uppercase;
        }

        .bar-row {
            margin-top: 12px;
        }

        .bar-top {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            color: var(--ink);
            font-size: .78rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .bar-top span {
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .bar-track {
            height: 10px;
            margin-top: 6px;
            border-radius: 999px;
            overflow: hidden;
            background: #DDE7F4;
        }

        .bar-track i {
            display: block;
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, var(--blue), var(--gold));
        }

        .pie-layout {
            display: grid;
            grid-template-columns: minmax(150px, .8fr) minmax(180px, 1.2fr);
            gap: 20px;
            align-items: center;
            min-height: 190px;
        }

        .pie-chart {
            width: 170px;
            aspect-ratio: 1;
            display: grid;
            place-items: center;
            margin: auto;
            border-radius: 50%;
            box-shadow: 0 16px 34px rgba(6,20,46,.16);
        }

        .pie-chart > div {
            width: 52%;
            aspect-ratio: 1;
            display: grid;
            place-content: center;
            border-radius: 50%;
            text-align: center;
            background: #FFFFFF;
            box-shadow: inset 0 0 0 1px #D8E3F1;
        }

        .pie-chart strong {
            color: var(--ink);
            font-family: "Barlow Condensed", sans-serif;
            font-size: 1.65rem;
            line-height: .9;
        }

        .pie-chart span {
            color: var(--muted);
            font-size: .62rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .pie-legend {
            display: grid;
            gap: 8px;
        }

        .pie-legend-row {
            display: grid;
            grid-template-columns: 12px minmax(0,1fr) auto;
            gap: 8px;
            align-items: center;
            color: var(--ink);
            font-size: .72rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .pie-legend-row i {
            width: 12px;
            height: 12px;
            border-radius: 4px;
        }

        .pie-legend-row strong {
            color: var(--muted);
            font-size: .68rem;
        }

        .line-viz {
            width: 100%;
            height: 190px;
            display: block;
            border-radius: 18px;
            background:
                linear-gradient(rgba(11,36,84,.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(11,36,84,.08) 1px, transparent 1px),
                #F7FAFE;
            background-size: 100% 25%, 16.66% 100%, auto;
            border: 1px solid #D8E3F1;
        }

        .line-viz polyline {
            fill: none;
            stroke: var(--blue);
            stroke-width: 5;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .line-viz circle {
            fill: var(--gold);
            stroke: #FFFFFF;
            stroke-width: 2;
        }

        .line-viz .line-value {
            fill: var(--ink);
            font-family: "Barlow", sans-serif;
            font-size: 9.5px;
            font-weight: 900;
            text-anchor: middle;
            paint-order: stroke;
            stroke: #FFFFFF;
            stroke-width: 3px;
            stroke-linejoin: round;
        }

        .line-viz .axis-grid {
            stroke: rgba(11,36,84,.13);
            stroke-width: 1;
        }

        .line-viz .axis-line {
            stroke: var(--muted);
            stroke-width: 1.25;
        }

        .line-viz .axis-value {
            fill: var(--ink);
            font-family: "Barlow Condensed", sans-serif;
            font-size: 11px;
            font-weight: 900;
            text-anchor: end;
        }

        .line-viz .axis-x-value {
            fill: var(--ink);
            font-family: "Barlow Condensed", sans-serif;
            font-size: 11px;
            font-weight: 900;
            text-anchor: middle;
        }

        .viz-labels {
            display: flex;
            justify-content: space-between;
            gap: 8px;
            margin-top: 8px;
            color: var(--muted);
            font-size: .7rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .empty-mini {
            color: var(--muted);
            font-weight: 900;
        }

        .match-tile,
        .country-card,
        .venue-card,
        .profile-card,
        .stadium-detail,
        .club-row {
            border-radius: 22px;
            background: #FFFFFF;
            border: 1px solid var(--line);
            box-shadow: 0 18px 42px rgba(6,20,46,.08);
        }

        .match-tile {
            min-height: 200px;
            padding: 15px;
            margin-bottom: 8px;
            transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
        }

        .match-tile:hover,
        .country-card:hover,
        .venue-card:hover {
            transform: translateY(-2px);
            border-color: rgba(0,87,216,.38);
            box-shadow: 0 24px 58px rgba(0,87,216,.14);
        }

        .active-card {
            border-color: rgba(0,87,216,.55) !important;
            background:
                linear-gradient(135deg, rgba(0,87,216,.16), rgba(214,163,41,.16)),
                #FFFFFF !important;
            box-shadow: 0 26px 64px rgba(0,87,216,.24) !important;
        }

        .match-tile.active-card:before,
        .venue-card.active-card:before {
            content: "";
            display: block;
            height: 4px;
            margin: -15px -15px 12px;
            background: linear-gradient(90deg, var(--blue), var(--gold));
        }

        .tile-meta,
        .tile-venue {
            color: var(--muted);
            font-size: .74rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .tile-team {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 11px;
            color: var(--ink);
            font-size: 1.08rem;
            font-weight: 900;
        }

        .tile-team span {
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .tile-venue {
            margin-top: 8px;
            color: #0048B4;
        }

        .date-band {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
            margin: 22px 0 12px;
            padding: 13px 16px;
            border-radius: 18px;
            color: #FFFFFF;
            background: linear-gradient(135deg, var(--ink), var(--blue));
            box-shadow: 0 18px 36px rgba(6,20,46,.14);
        }

        .date-band strong {
            font-family: "Barlow Condensed", sans-serif;
            font-size: 1.6rem;
            line-height: .9;
            font-weight: 900;
            text-transform: uppercase;
        }

        .date-band span {
            color: rgba(255,255,255,.82);
            font-size: .78rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .bracket {
            display: grid;
            grid-template-columns: 1fr .82fr .7fr 1.05fr .7fr .82fr 1fr;
            gap: 10px;
            align-items: center;
            min-height: 480px;
            padding: 22px;
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(0,87,216,.08), rgba(8,160,69,.07)),
                #FFFFFF;
            border: 1px solid var(--line);
            box-shadow: 0 22px 54px rgba(6,20,46,.09);
        }

        .bracket-col {
            display: grid;
            gap: 10px;
        }

        .bracket-col.tight {
            gap: 34px;
        }

        .bracket-col.tighter {
            gap: 88px;
        }

        .bracket-slot {
            min-height: 42px;
            display: grid;
            place-items: center;
            border-radius: 14px;
            color: var(--ink);
            background: #F7FAFE;
            border: 1px solid var(--line);
            font-size: .75rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .cup-core {
            display: grid;
            place-items: center;
            gap: 7px;
            min-height: 280px;
            border-radius: 28px;
            color: #FFFFFF;
            background: linear-gradient(135deg, var(--ink), var(--blue));
            box-shadow: 0 24px 58px rgba(0,87,216,.24);
        }

        .cup img {
            width: min(160px, 70%);
            height: 190px;
            object-fit: contain;
            display: block;
            filter: drop-shadow(0 22px 34px rgba(0,0,0,.35));
        }

        .cup-core strong {
            font-family: "Barlow Condensed", sans-serif;
            font-size: 2rem;
            line-height: .9;
            text-transform: uppercase;
        }

        .cup-core span {
            color: rgba(255,255,255,.72);
            font-size: .75rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .country-card {
            min-height: 168px;
            display: grid;
            place-items: center;
            text-align: center;
            gap: 8px;
            padding: 18px 12px;
            margin-bottom: 8px;
        }

        .country-rail {
            position: sticky;
            top: 82px;
            max-height: calc(100vh - 110px);
            overflow: auto;
            padding: 14px;
            border-radius: 24px;
            background: rgba(255,255,255,.82);
            border: 1px solid #C6D4E7;
            box-shadow: 0 20px 48px rgba(6,20,46,.09);
        }

        .country-card-compact {
            min-height: 64px;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 10px;
            padding: 10px;
            text-align: left;
            border-radius: 18px;
        }

        .country-card-compact strong {
            display: block;
            font-size: 1.08rem;
            line-height: .95;
        }

        .country-card-compact span {
            display: block;
            margin-top: 4px;
            font-size: .66rem;
        }

        .country-card strong {
            color: var(--ink);
            font-family: "Barlow Condensed", sans-serif;
            font-size: 1.55rem;
            line-height: .9;
            text-transform: uppercase;
        }

        .country-card span {
            color: var(--muted);
            font-size: .76rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .profile-card {
            padding: 22px;
            text-align: center;
        }

        .profile-card-featured {
            min-height: 100%;
            background:
                linear-gradient(180deg, rgba(0,87,216,.10), rgba(214,163,41,.10)),
                #FFFFFF;
        }

        .profile-card h2 {
            margin: 14px 0 4px;
            color: var(--ink);
            font-size: 2.6rem;
            line-height: .85;
            font-weight: 900;
            text-transform: uppercase;
        }

        .profile-card p {
            margin: 0 0 12px;
            color: var(--muted);
            font-weight: 900;
            text-transform: uppercase;
        }

        .mini-kpi,
        .club-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            padding: 12px;
            margin-top: 9px;
            border-radius: 15px;
            background: #F7FAFE;
            border: 1px solid var(--line);
        }

        .mini-kpi span,
        .club-row span {
            color: var(--muted);
            font-size: .72rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .mini-kpi strong,
        .club-row strong {
            color: var(--ink);
            font-family: "Barlow Condensed", sans-serif;
            font-size: 1.3rem;
            font-weight: 900;
        }

        .venue-map {
            width: 100%;
            height: auto;
            display: block;
            margin-bottom: 18px;
            filter: drop-shadow(0 24px 56px rgba(6,20,46,.12));
        }

        .venue-map rect {
            fill: #071A3D;
        }

        .venue-map .land {
            fill: #133C78;
            stroke: rgba(255,255,255,.18);
            stroke-width: 2;
        }

        .venue-map .mexico {
            fill: #0D7650;
        }

        .venue-map .map-label {
            fill: rgba(255,255,255,.45);
            font-size: 22px;
            font-weight: 900;
            text-transform: uppercase;
        }

        .venue-map .venue-point {
            fill: var(--gold);
            stroke: #FFFFFF;
            stroke-width: 3;
            cursor: pointer;
        }

        .venue-map .venue-point.active {
            fill: #FFFFFF;
            stroke: var(--gold);
            stroke-width: 5;
        }

        .venue-map text {
            fill: #FFFFFF;
            font-size: 13px;
            font-weight: 900;
            paint-order: stroke;
            stroke: rgba(6,20,46,.65);
            stroke-width: 3px;
        }

        .stadium-detail {
            display: grid;
            grid-template-columns: minmax(280px,.8fr) minmax(0,1.2fr);
            gap: 18px;
            align-items: stretch;
            padding: 18px;
            margin-bottom: 22px;
            background: transparent;
            border: 0;
            box-shadow: none;
        }

        .stadium-detail h2 {
            margin: 8px 0 10px;
            color: var(--ink);
            font-size: clamp(2.5rem, 5vw, 4.2rem);
            line-height: .84;
            font-weight: 900;
            text-transform: uppercase;
        }

        .stadium-detail .kicker,
        .profile-card .kicker {
            color: #0048B4;
        }

        .stadium-detail .chip {
            color: var(--ink);
            background: #EEF5FF;
            border-color: #B8CAE5;
        }

        .venue-card {
            min-height: 112px;
            padding: 16px;
            margin-bottom: 8px;
        }

        .venue-card strong {
            display: block;
            color: var(--ink);
            font-family: "Barlow Condensed", sans-serif;
            font-size: 1.45rem;
            line-height: .9;
            font-weight: 900;
            text-transform: uppercase;
        }

        .venue-card span {
            display: block;
            margin-top: 8px;
            color: var(--muted);
            font-size: .78rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .venue-card.active-card strong,
        .venue-card.active-card span,
        .country-card.active-card strong,
        .country-card.active-card span {
            color: var(--ink);
        }

        div[data-testid="stButton"] > button {
            min-height: 40px;
            border-radius: 999px;
            border: 1px solid var(--line);
            background: #FFFFFF;
            color: var(--ink);
            font-weight: 900;
            text-transform: uppercase;
            box-shadow: 0 10px 24px rgba(6,20,46,.06);
        }

        div[data-testid="stButton"] > button:hover {
            color: #FFFFFF;
            border-color: transparent;
            background: linear-gradient(135deg, var(--blue), var(--ink));
        }

        [data-testid="stMetric"] {
            min-height: 112px;
            padding: 16px 18px;
            border-radius: 16px;
            background: #FFFFFF;
            border: 1px solid rgba(160,178,205,.86);
            box-shadow: 0 16px 34px rgba(6,20,46,.10);
        }

        [data-testid="stMetricLabel"] p {
            color: var(--muted) !important;
            font-weight: 900 !important;
            text-transform: uppercase;
            font-size: .78rem !important;
        }

        [data-testid="stMetricValue"] {
            color: var(--ink) !important;
            font-family: "Barlow Condensed", sans-serif;
            font-weight: 900;
        }

        [data-testid="stMetricValue"] div {
            color: var(--ink) !important;
        }

        @media (max-width: 1050px) {
            .match-centre,
            .three-grid,
            .fixture-grid,
            .result-grid,
            .viz-grid {
                grid-template-columns: 1fr;
            }
            .group-grid,
            .metric-grid {
                grid-template-columns: repeat(2, minmax(0,1fr));
            }
            .home-hero,
            .stadium-detail,
            .bracket {
                grid-template-columns: 1fr;
            }
            .bracket-col.tight,
            .bracket-col.tighter {
                gap: 10px;
            }
            .country-rail {
                position: static;
                max-height: 420px;
            }
        }

        @media (max-width: 640px) {
            .nav-shell {
                align-items: flex-start;
                flex-direction: column;
            }
            .group-grid,
            .metric-grid,
            .two-grid,
            .players-grid,
            .stat-grid {
                grid-template-columns: 1fr;
            }
            .hero {
                min-height: 430px;
                padding: 22px;
            }
            .home-hero h1 {
                font-size: clamp(2.35rem, 10.5vw, 3.6rem);
            }
            .compare-row {
                grid-template-columns: 1fr;
            }
            .compare-row span,
            .compare-row strong:last-child {
                text-align: left;
            }
            .pie-layout {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
