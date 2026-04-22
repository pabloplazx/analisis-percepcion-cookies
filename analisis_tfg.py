# =============================================================================
# ANÁLISIS ESTADÍSTICO TFG - Percepción de cookies en internet
# =============================================================================
# Herramientas: pandas, scipy
# Datos: Google Forms -> Excel (180 respuestas, escala Likert 1-5)
#
# ESTRUCTURA:
#   ETAPA 0 - Carga y preparación de datos
#   ETAPA 1 - Análisis descriptivo (Objetivo Secundario 1)
#   ETAPA 2 - Comparación Gen Z vs. Adultos 40+ Mann-Whitney U (OS 2)
#   ETAPA 3 - Correlaciones Spearman e índices compuestos
#   ETAPA 4 - Exportación de resultados a Excel
# =============================================================================

import glob
import sys
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# ETAPA 0 - CARGA Y PREPARACIÓN DE DATOS
# =============================================================================

# Localizar el archivo automáticamente (evita problemas con tildes en la ruta)
files = glob.glob(r'C:\Users\plaza\Desktop\tfg carlota\*.xlsx')
assert files, "No se encontró ningún .xlsx en la carpeta"
path = files[0]

df_raw = pd.read_excel(path)
print(f"Datos cargados: {df_raw.shape[0]} respuestas, {df_raw.shape[1]} columnas\n")

# --- Renombrar columnas con etiquetas cortas para facilitar el análisis ---
COLUMN_MAP = {
    'Marca temporal'                                                                                                                                  : 'timestamp',
    'Creo que estoy bien informado respecto a las cookies.'                                                                                           : 'con_informado',
    'Entiendo lo que son las cookies.'                                                                                                                 : 'con_que_son',
    'Entiendo el funcionamiento general de las cookies.'                                                                                               : 'con_funcionamiento',
    'Soy consciente de los diferentes usos de las cookies.'                                                                                           : 'con_usos',
    'Pienso que las cookies suponen una amenaza para mi persona.'                                                                                     : 'pre_amenaza',
    'Me preocupa activamente cómo se recogen mis datos online.'                                                                                       : 'pre_activa',
    'Creo que las cookies afectan de manera negativa a mi privacidad.'                                                                                : 'pre_privacidad',
    'Creo que puedo hacer frente a consecuencias negativas importantes si acepto las cookies.'                                                        : 'pre_consecuencias',
    'Siento que controlo cómo se recogen mis datos online.'                                                                                           : 'pre_control',
    'Cuando busco por internet me preocupo a menudo por mi privacidad.'                                                                               : 'pre_busqueda',
    'En algún momento he recibido algún tipo de formación sobre las cookies, o aspectos relacionados, en un entorno académico o similar.'             : 'form_recibida',
    'Siento que la información que recibido sobre las cookies ha impactado en mis interacciones online con estas.'                                    : 'form_impacto',
    'Me importan las cookies'                                                                                                                         : 'act_importan',
    'Normalmente acepto las cookies.'                                                                                                                 : 'com_acepto',
    'Normalmente cierro o ignoro el aviso relativo a las cookies que aparece en pantalla.'                                                            : 'com_ignoro',
    'Suelo rechazar las cookies cuando se me da la opción.'                                                                                           : 'com_rechazo',
    'Suelo personalizar las opciones de cookies cuando puedo.'                                                                                        : 'com_personalizo',
    'Cuando ignoro las cookies es porque las veo demasiado a menudo y me cansan.'                                                                    : 'conv_cansan',
    'Pienso que rechazar las cookies lleva más esfuerzo del que estoy dispuesto a hacer.'                                                            : 'conv_esfuerzo_rechazo',
    'Pienso que personalizar las cookies lleva más esfuerzo del que estoy dispuesto a hacer.'                                                        : 'conv_esfuerzo_custom',
    'Es mas probable que personalice las cookies en paginas web en las que no confío.'                                                               : 'com_confianza',
    'Me molestan las notificaciones relativas a las cookies cuando me meto en una página web.'                                                        : 'act_molestia',
    'Me importa más acceder al contenido de forma rápida que las cookies en si.'                                                                     : 'conv_rapidez',
    'Cuando busco en internet, en general, doy más importancia a la comodidad que a la privacidad.'                                                  : 'conv_comodidad',
    'Suelo prestar atención a lo que estoy accediendo cuando acepto las cookies.'                                                                    : 'com_atencion',
    'Siento que el formato en el que aparece la notificación de las cookies me manipula para que las acepte.'                                        : 'act_manipulacion',
    'Alguna vez he aceptado cookies que pretendía rechazar o personalizar por ir con prisa y seleccionar el botón más llamativo dentro de la notificación de cookies.' : 'com_dark_pattern',
    'Género'                                                                                                                                          : 'genero',
    'Edad'                                                                                                                                            : 'edad',
}

df = df_raw.rename(columns=COLUMN_MAP).drop(columns=['timestamp'])

# --- Definir grupos de edad para los análisis comparativos ---
# Gen Z: 18-28 años | Adultos 40+: suma de "40-65" y "Más de 65"
df['grupo_edad'] = df['edad'].map({
    'Menos de 18': 'menor_18',
    '18-28'      : 'gen_z',
    '28-40'      : 'adulto_medio',
    '40-65'      : 'adulto_mayor',
    'Más de 65'  : 'adulto_mayor',
})

# Columnas Likert (todas excepto demográficas)
LIKERT_COLS = [c for c in df.columns if c not in ('genero', 'edad', 'grupo_edad')]

print("Distribución por edad:")
print(df['edad'].value_counts(), '\n')
print("Distribución por género:")
print(df['genero'].value_counts(), '\n')
print("Grupos analíticos:")
print(df['grupo_edad'].value_counts(), '\n')

# =============================================================================
# ETAPA 1 - ANÁLISIS DESCRIPTIVO
# Objetivo: documentar patrones de comportamiento generales y por subgrupos.
# =============================================================================

print("=" * 70)
print("ETAPA 1 - ANÁLISIS DESCRIPTIVO")
print("=" * 70)

# --- 1a. Estadísticos globales por ítem ---
desc_global = df[LIKERT_COLS].agg(['mean', 'median', 'std', 'min', 'max']).T.round(2)
desc_global.index.name = 'item'
print("\n--- Estadísticos globales (n=180) ---")
print(desc_global.to_string())

# --- 1b. Medias por grupo de edad ---
desc_edad = df.groupby('grupo_edad')[LIKERT_COLS].mean().T.round(2)
print("\n--- Medias por grupo de edad ---")
print(desc_edad.to_string())

# --- 1c. Medias por género ---
desc_genero = df.groupby('genero')[LIKERT_COLS].mean().T.round(2)
print("\n--- Medias por género ---")
print(desc_genero.to_string())

# --- 1d. Distribución de frecuencias (%) por ítem ---
# Porcentaje de cada valor (1-5) para cada ítem
freq_tables = {}
for col in LIKERT_COLS:
    counts = df[col].value_counts(normalize=True).sort_index() * 100
    freq_tables[col] = counts.round(1)
freq_df = pd.DataFrame(freq_tables).T
freq_df.columns = [f'valor_{int(c)}' for c in freq_df.columns]
print("\n--- Distribución de frecuencias (% por valor 1-5) ---")
print(freq_df.to_string())

# =============================================================================
# ETAPA 2 - ANÁLISIS COMPARATIVO: Gen Z (18-28) vs. Adultos 40+
# Prueba U de Mann-Whitney (no paramétrica, apropiada para datos ordinales Likert).
# Nivel de significación: p < 0.05
# =============================================================================

print("\n" + "=" * 70)
print("ETAPA 2 - MANN-WHITNEY U: Gen Z vs. Adultos 40+")
print("=" * 70)

genz    = df[df['grupo_edad'] == 'gen_z']
mayores = df[df['grupo_edad'] == 'adulto_mayor']
print(f"Gen Z (18-28): n={len(genz)} | Adultos 40+: n={len(mayores)}\n")

mw_results = []
for col in LIKERT_COLS:
    g1 = genz[col].dropna()
    g2 = mayores[col].dropna()
    stat, p = stats.mannwhitneyu(g1, g2, alternative='two-sided')
    mw_results.append({
        'item'          : col,
        'mediana_genz'  : round(g1.median(), 2),
        'mediana_40+'   : round(g2.median(), 2),
        'media_genz'    : round(g1.mean(), 2),
        'media_40+'     : round(g2.mean(), 2),
        'U'             : round(stat, 1),
        'p_valor'       : round(p, 4),
        'significativo' : 'Sí *' if p < 0.05 else 'No',
    })

mw_df = pd.DataFrame(mw_results).set_index('item')
print(mw_df.to_string())

sig_count = (mw_df['significativo'] == 'Sí *').sum()
print(f"\nÍtems con diferencias significativas (p<0.05): {sig_count} de {len(LIKERT_COLS)}")

# =============================================================================
# ETAPA 3 - CORRELACIONES SPEARMAN E ÍNDICES COMPUESTOS
# Spearman es adecuado para variables ordinales (no asume normalidad).
# Los índices compuestos resumen dimensiones temáticas en una sola métrica.
# =============================================================================

print("\n" + "=" * 70)
print("ETAPA 3 - CORRELACIONES SPEARMAN E ÍNDICES COMPUESTOS")
print("=" * 70)

# --- 3a. Construcción de índices compuestos (media de ítems relacionados) ---
# Cada índice agrupa ítems que miden la misma dimensión conceptual.

df['idx_conocimiento'] = df[['con_informado', 'con_que_son', 'con_funcionamiento', 'con_usos']].mean(axis=1)

df['idx_preocupacion'] = df[['pre_amenaza', 'pre_activa', 'pre_privacidad', 'pre_consecuencias', 'pre_busqueda']].mean(axis=1)
# Nota: pre_control mide percepción de control (no preocupación directa), se excluye del índice.

df['idx_formacion'] = df[['form_recibida', 'form_impacto']].mean(axis=1)

# Comportamiento pasivo: aceptar o ignorar sin reflexión (valores altos = más pasivo)
df['idx_pasivo'] = df[['com_acepto', 'com_ignoro']].mean(axis=1)

# Orientación a la conveniencia sobre privacidad
df['idx_conveniencia'] = df[['conv_cansan', 'conv_esfuerzo_rechazo', 'conv_esfuerzo_custom',
                              'conv_rapidez', 'conv_comodidad']].mean(axis=1)

INDICES = ['idx_conocimiento', 'idx_preocupacion', 'idx_formacion', 'idx_pasivo', 'idx_conveniencia']

print("\n--- Estadísticos de índices compuestos ---")
print(df[INDICES].describe().round(2).to_string())

# --- 3b. Correlaciones Spearman entre índices ---
print("\n--- Correlaciones Spearman entre índices compuestos ---")
corr_matrix, pval_matrix = stats.spearmanr(df[INDICES].dropna(), axis=0)
corr_df = pd.DataFrame(corr_matrix, index=INDICES, columns=INDICES).round(3)
pval_df = pd.DataFrame(pval_matrix, index=INDICES, columns=INDICES).round(4)
print("Coeficientes rho:")
print(corr_df.to_string())
print("\np-valores:")
print(pval_df.to_string())

# --- 3c. Correlación clave 1: Formación formal -> Comportamiento real ---
# ¿Quienes han recibido formación tienen comportamientos menos pasivos?
r1, p1 = stats.spearmanr(df['idx_formacion'], df['idx_pasivo'])
print(f"\n[Paradoja de privacidad - test 1]")
print(f"  Formación vs. Comportamiento pasivo: rho={r1:.3f}, p={p1:.4f}")

# --- 3d. Correlación clave 2: Preocupación declarada -> Comportamiento de aceptación ---
# Paradoja de la privacidad: alta preocupación pero se acepta igual.
r2, p2 = stats.spearmanr(df['idx_preocupacion'], df['com_acepto'])
print(f"\n[Paradoja de privacidad - test 2]")
print(f"  Preocupación vs. Aceptación de cookies: rho={r2:.3f}, p={p2:.4f}")

# --- 3e. Correlación clave 3: Conocimiento -> Comportamiento pasivo ---
r3, p3 = stats.spearmanr(df['idx_conocimiento'], df['idx_pasivo'])
print(f"\n[Conocimiento vs. Pasividad]")
print(f"  Conocimiento vs. Comportamiento pasivo: rho={r3:.3f}, p={p3:.4f}")

# --- 3f. Correlación clave 4: Preocupación -> Conveniencia ---
r4, p4 = stats.spearmanr(df['idx_preocupacion'], df['idx_conveniencia'])
print(f"\n[Preocupación vs. Conveniencia]")
print(f"  Preocupación vs. Conveniencia: rho={r4:.3f}, p={p4:.4f}")

# =============================================================================
# ETAPA 4 - EXPORTACIÓN DE RESULTADOS A EXCEL (un archivo, múltiples hojas)
# =============================================================================

output_path = r'C:\Users\plaza\Desktop\tfg carlota\resultados_analisis.xlsx'

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

    desc_global.to_excel(writer, sheet_name='1a_descriptivo_global')
    desc_edad.to_excel(writer, sheet_name='1b_medias_por_edad')
    desc_genero.to_excel(writer, sheet_name='1c_medias_por_genero')
    freq_df.to_excel(writer, sheet_name='1d_frecuencias_%')
    mw_df.to_excel(writer, sheet_name='2_mann_whitney')

    # Índices: estadísticos descriptivos por grupo de edad
    idx_desc = df.groupby('grupo_edad')[INDICES].mean().T.round(3)
    idx_desc.to_excel(writer, sheet_name='3a_indices_por_edad')

    corr_df.to_excel(writer, sheet_name='3b_corr_spearman')
    pval_df.to_excel(writer, sheet_name='3b_corr_pvalores')

    # Resumen de correlaciones clave
    corr_clave = pd.DataFrame([
        {'Hipótesis': 'Formación -> Comportamiento pasivo',      'rho': round(r1, 3), 'p': round(p1, 4), 'sig': 'Sí' if p1 < 0.05 else 'No'},
        {'Hipótesis': 'Preocupación -> Aceptación (paradoja)',   'rho': round(r2, 3), 'p': round(p2, 4), 'sig': 'Sí' if p2 < 0.05 else 'No'},
        {'Hipótesis': 'Conocimiento -> Comportamiento pasivo',   'rho': round(r3, 3), 'p': round(p3, 4), 'sig': 'Sí' if p3 < 0.05 else 'No'},
        {'Hipótesis': 'Preocupación -> Conveniencia',            'rho': round(r4, 3), 'p': round(p4, 4), 'sig': 'Sí' if p4 < 0.05 else 'No'},
    ])
    corr_clave.to_excel(writer, sheet_name='3c_correlaciones_clave', index=False)

    # Datos completos con índices añadidos (útil para revisión)
    df.to_excel(writer, sheet_name='datos_completos', index=False)

print(f"\n{'=' * 70}")
print(f"Resultados exportados a: {output_path}")
print("Hojas generadas:")
print("  1a_descriptivo_global   - Media, mediana, SD, min, max por ítem")
print("  1b_medias_por_edad      - Medias por grupo de edad")
print("  1c_medias_por_genero    - Medias por género")
print("  1d_frecuencias_%        - Distribución de frecuencias (1-5)")
print("  2_mann_whitney          - U de Mann-Whitney Gen Z vs 40+")
print("  3a_indices_por_edad     - Índices compuestos por grupo de edad")
print("  3b_corr_spearman        - Matriz de correlaciones rho")
print("  3b_corr_pvalores        - p-valores de correlaciones")
print("  3c_correlaciones_clave  - Hipótesis paradoja de privacidad")
print("  datos_completos         - Dataset con índices incluidos")
