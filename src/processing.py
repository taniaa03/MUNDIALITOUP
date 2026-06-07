import pandas as pd
import os
import re

def limpiar_enfrentamientos(df):
    print("--- Limpiando enfrentamientos ---")
    # Eliminar columnas que contengan 'attendance' (insensible a mayúsculas)
    attendance_cols = [col for col in df.columns if 'attendance' in col.lower()]
    if attendance_cols:
        df.drop(columns=attendance_cols, inplace=True)
        print(f"  ✅ Eliminadas: {attendance_cols}")
    else:
        print("  ⚠️ No se encontró ninguna columna con 'attendance'")

    # Eliminar columnas específicas
    eliminar = [
        'Home Team Pre-Match xG',
        'Away Team Pre-Match xG',
        'team_a_xg',
        'team_b_xg'
    ]
    for col in eliminar:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
            print(f"  ✅ Eliminada: {col}")

    # Eliminar columnas que empiecen con 'odds_'
    odds_cols = [col for col in df.columns if col.lower().startswith('odds_')]
    if odds_cols:
        df.drop(columns=odds_cols, inplace=True)
        print(f"  ✅ Eliminadas columnas odds: {len(odds_cols)} columnas")

    # Reemplazar nulos en referee y stadium_name
    for col in df.columns:
        if col.lower() in ['referee', 'referi']:
            df[col] = df[col].fillna('desconocido').replace(['N/A', '', ' '], 'desconocido')
            print(f"  ✅ Nulos en '{col}' → 'desconocido'")
    if 'stadium_name' in df.columns:
        df['stadium_name'] = df['stadium_name'].fillna('desconocido').replace(['N/A', '', ' '], 'desconocido')
        print(f"  ✅ Nulos en 'stadium_name' → 'desconocido'")

    return df

def limpiar_equipos(df):
    print("--- Limpiando equipos ---")
    eliminar = ['league_position_home', 'league_position_away', 'suspended_matches']
    for col in eliminar:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
            print(f"  ✅ Eliminada: {col}")
    return df

def reemplazar_nulos_numericos_por_cero(df):
    for col in df.select_dtypes(include=['number']).columns:
        if df[col].isnull().any():
            df[col] = df[col].fillna(0)
            print(f"  🔢 Nulos en columna numérica '{col}' → 0")
    return df

def reemplazar_nulos_texto_por_desconocido(df):
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].isnull().any():
            df[col] = df[col].fillna('desconocido')
            print(f"  📝 Nulos en columna de texto '{col}' → 'desconocido'")
    return df

def limpiar_goal_timings_vacio(df):
    """Deja vacías (cadena '') las celdas en columnas de tiempos de goles que no tengan datos"""
    for col in df.columns:
        if 'goal_timings' in col:
            # Reemplazar 'desconocido', N/A, espacios, nulos por cadena vacía
            df[col] = df[col].replace(['desconocido', 'N/A', '', ' '], '')
            df[col] = df[col].fillna('')
            print(f"  ⚽ Columna '{col}': valores vacíos o nulos → celda vacía ('' )")
    return df

def estandarizar_nombres_columnas(df):
    nuevos = {}
    for col in df.columns:
        nuevo = col.lower().strip()
        nuevo = re.sub(r'[^a-z0-9_]', '_', nuevo)
        nuevo = re.sub(r'_+', '_', nuevo)
        nuevos[col] = nuevo
    df.rename(columns=nuevos, inplace=True)
    return df

def procesar_todo(ruta_data='data', ruta_salida='data/processed'):
    os.makedirs(ruta_salida, exist_ok=True)

    # Buscar archivos originales
    archivos = os.listdir(ruta_data)
    enf_path = None
    eq_path = None
    for f in archivos:
        if 'enfrentamientos' in f.lower() and f.endswith(('.xlsx', '.xls', '.csv')):
            enf_path = os.path.join(ruta_data, f)
        elif 'equipos' in f.lower() and f.endswith(('.xlsx', '.xls', '.csv')):
            eq_path = os.path.join(ruta_data, f)

    if not enf_path or not eq_path:
        raise FileNotFoundError("No se encontraron enfrentamientos.xlsx o equipos.xlsx en la carpeta data/")

    print(f"📂 Leyendo {enf_path} ...")
    df_enf = pd.read_excel(enf_path)
    print(f"📂 Leyendo {eq_path} ...")
    df_eq = pd.read_excel(eq_path)

    print(f"Original: enfrentamientos {df_enf.shape}, equipos {df_eq.shape}")

    # ---- LIMPIEZA ----
    # 1. Reemplazar nulos numéricos por 0
    df_enf = reemplazar_nulos_numericos_por_cero(df_enf)
    df_eq = reemplazar_nulos_numericos_por_cero(df_eq)

    # 2. Limpiezas específicas
    df_enf = limpiar_enfrentamientos(df_enf)
    df_eq = limpiar_equipos(df_eq)

    # 3. Estandarizar nombres
    df_enf = estandarizar_nombres_columnas(df_enf)
    df_eq = estandarizar_nombres_columnas(df_eq)

    # 4. Reemplazar nulos de texto restantes por "desconocido"
    df_enf = reemplazar_nulos_texto_por_desconocido(df_enf)
    df_eq = reemplazar_nulos_texto_por_desconocido(df_eq)

    # 5. Dejar vacías las columnas de tiempos de goles (home_team_goal_timings, away_team_goal_timings)
    df_enf = limpiar_goal_timings_vacio(df_enf)

    print(f"Final: enfrentamientos {df_enf.shape}, equipos {df_eq.shape}")

    # Guardar archivos
    enf_csv = os.path.join(ruta_salida, 'enfrentamientos_procesado.csv')
    eq_csv = os.path.join(ruta_salida, 'equipos_procesado.csv')
    df_enf.to_csv(enf_csv, index=False)
    df_eq.to_csv(eq_csv, index=False)

    enfrentamientos2 = df_enf
    equipos2 = df_eq

    print(f"✅ Datos guardados en {ruta_salida}")
    return enfrentamientos2, equipos2

if __name__ == "__main__":
    procesar_todo()