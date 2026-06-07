import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(__file__))
from processing import procesar_todo

st.set_page_config(page_title="Mundialito UP", layout="wide")
st.title("📊 Mundialito UP")

PROCESSED_DIR = "data/processed"
ENF_PATH = os.path.join(PROCESSED_DIR, "enfrentamientos_procesado.csv")
EQUIPOS_PATH = os.path.join(PROCESSED_DIR, "equipos_procesado.csv")

if not os.path.exists(ENF_PATH) or not os.path.exists(EQUIPOS_PATH):
    with st.spinner("Procesando datos por primera vez..."):
        enfrentamientos2, equipos2 = procesar_todo()
else:
    enfrentamientos2 = pd.read_csv(ENF_PATH)
    equipos2 = pd.read_csv(EQUIPOS_PATH)

tab1, tab2, tab3 = st.tabs(["📋 Tablas", " Pestaña 2 ", "pestaña 3 "])

with tab1:
    st.subheader("Tabla de Enfrentamientos")
    st.dataframe(enfrentamientos2, width='stretch', height=400)
    st.markdown("---")
    st.subheader("Tabla de Equipos")
    st.dataframe(equipos2, width='stretch', height=400)

with tab2:
##ejemploooo eliminar
    st.subheader("Goles totales por competición")
    if 'competici_n' in enfrentamientos2.columns:
        goles_por_comp = enfrentamientos2.groupby('competici_n')['home_team_goal_count'].sum()
        st.bar_chart(goles_por_comp)
    else:
        st.info("Columna 'competici_n' no encontrada")

with tab3:
    st.write("")