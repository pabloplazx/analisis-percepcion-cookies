# Análisis estadístico — Percepción de cookies en internet y comportamiento frente a ellas

TFG · Análisis de encuesta (n=180) sobre conocimiento, preocupación por la privacidad y comportamiento ante las cookies de navegación.

---

## Estructura del repositorio

```
.
├── Percepción de la cookies en internet y comportamiento frente a ellas (respuestas).xlsx
│   Datos exportados directamente desde Google Forms. Contiene 180 respuestas
│   y 28 ítems en escala Likert 1–5, más variables demográficas (edad y género).
│
├── analisis_tfg.py
│   Script principal de análisis. Ejecuta las tres etapas del estudio:
│   descriptivo, comparativo (Mann-Whitney U) y correlaciones (Spearman).
│   Genera el archivo de resultados al finalizar.
│
├── resultados_analisis.xlsx
│   Archivo Excel con los resultados organizados en hojas:
│   · 1a_descriptivo_global    — Media, mediana, SD y rango por ítem
│   · 1b_medias_por_edad       — Medias desglosadas por grupo de edad
│   · 1c_medias_por_genero     — Medias desglosadas por género
│   · 1d_frecuencias_%         — Distribución porcentual de valores 1–5
│   · 2_mann_whitney           — Prueba U por ítem (Gen Z vs. Adultos 40+)
│   · 3a_indices_por_edad      — Índices compuestos por grupo de edad
│   · 3b_corr_spearman         — Matriz de correlaciones rho de Spearman
│   · 3b_corr_pvalores         — p-valores de la matriz de correlaciones
│   · 3c_correlaciones_clave   — Hipótesis de la paradoja de privacidad
│   · datos_completos          — Dataset original con índices añadidos
│
└── procedimiento_y_resultados.md
    Documento con el procedimiento completo: código comentado explicando
    el porqué de cada decisión técnica, interpretación de resultados
    y conclusiones del análisis estadístico.
```

---

## Requisitos

Python 3.x con las siguientes bibliotecas:

```bash
pip install pandas scipy openpyxl
```

## Ejecución

```bash
python analisis_tfg.py
```

El script localiza el `.xlsx` automáticamente en la misma carpeta y genera `resultados_analisis.xlsx` al terminar.

---

## Resumen del análisis

El estudio se estructura en tres etapas alineadas con los objetivos de investigación:

**Etapa 1 — Análisis descriptivo**
Medias, medianas, desviaciones típicas y distribuciones de frecuencia para los 27 ítems, desglosadas por grupo de edad y género.

**Etapa 2 — Comparación generacional (Mann-Whitney U)**
Contraste no paramétrico entre la Generación Z (18–28 años, n=61) y los adultos de 40 o más (n=104). Se encontraron diferencias significativas en 7 de 27 ítems, principalmente en preocupación activa por la privacidad y orientación a la conveniencia.

**Etapa 3 — Correlaciones Spearman e índices compuestos**
Se construyeron cinco índices temáticos (conocimiento, preocupación, formación, comportamiento pasivo y conveniencia) y se analizaron sus correlaciones. El resultado más relevante es la confirmación empírica de la paradoja de la privacidad: preocupación declarada alta con correlación débil con el comportamiento real (rho = −0.289), y ausencia de efecto significativo de la formación sobre la conducta (rho = −0.076, n.s.).
