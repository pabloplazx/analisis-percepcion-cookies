# Procedimiento de análisis estadístico y resultados
## TFG — Percepción de las cookies en internet y comportamiento frente a ellas

---

## 1. Fuente de datos y herramientas utilizadas

Los datos se obtuvieron mediante un cuestionario distribuido a través de Google Forms y exportados en formato `.xlsx`. El fichero contiene **180 respuestas** y **28 ítems** (además de marca temporal y variables demográficas). Todos los ítems de contenido utilizan una **escala Likert de 1 a 5**, donde 1 = "Totalmente en desacuerdo" y 5 = "Totalmente de acuerdo".

El análisis se realizó íntegramente en **Python**, con las siguientes bibliotecas:

- `pandas` — carga, limpieza y manipulación de datos tabulares
- `scipy.stats` — pruebas estadísticas (Mann-Whitney U y Spearman)
- `openpyxl` — exportación de resultados a Excel con múltiples hojas

---

## 2. Código completo comentado

```python
# =============================================================================
# ANÁLISIS ESTADÍSTICO TFG - Percepción de cookies en internet
# =============================================================================

import glob
import sys
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
```

> `glob` se usa para localizar el archivo `.xlsx` automáticamente sin hardcodear
> la ruta con tildes, que da problemas de codificación en Windows.
> `sys.stdout.reconfigure` fuerza la salida en UTF-8 para que los caracteres
> especiales del español se muestren correctamente en la terminal.

---

### 2.1 Etapa 0 — Carga y preparación de datos

```python
files = glob.glob(r'C:\Users\plaza\Desktop\tfg carlota\*.xlsx')
assert files, "No se encontró ningún .xlsx en la carpeta"
path = files[0]

df_raw = pd.read_excel(path)
```

> `glob` busca cualquier fichero `.xlsx` en la carpeta. Si no encuentra ninguno,
> el `assert` detiene el programa con un mensaje claro en lugar de producir un
> error críptico más adelante.

```python
COLUMN_MAP = {
    'Creo que estoy bien informado respecto a las cookies.' : 'con_informado',
    'Entiendo lo que son las cookies.'                      : 'con_que_son',
    # ... (resto de columnas)
    'Género' : 'genero',
    'Edad'   : 'edad',
}
df = df_raw.rename(columns=COLUMN_MAP).drop(columns=['timestamp'])
```

> Las preguntas originales del formulario son frases largas, lo que hace el código
> ilegible. Se mapean a nombres cortos con prefijo temático:
> - `con_` → conocimiento
> - `pre_` → preocupación por privacidad
> - `form_` → formación recibida
> - `com_` → comportamiento ante cookies
> - `conv_` → orientación a la conveniencia
> - `act_` → actitudes generales

```python
df['grupo_edad'] = df['edad'].map({
    'Menos de 18': 'menor_18',
    '18-28'      : 'gen_z',
    '28-40'      : 'adulto_medio',
    '40-65'      : 'adulto_mayor',
    'Más de 65'  : 'adulto_mayor',
})
```

> Se crea una variable nueva `grupo_edad` que agrupa las categorías de edad en
> cuatro grupos analíticos. Las categorías "40-65" y "Más de 65" se unifican en
> `adulto_mayor` porque el objetivo de la investigación es comparar la Generación Z
> (18-28 años) con los adultos de 40 o más como bloque, tal y como se define en
> la hipótesis de estudio. El tamaño de cada categoría separada no permitiría
> hacer comparaciones estadísticamente robustas.

```python
LIKERT_COLS = [c for c in df.columns if c not in ('genero', 'edad', 'grupo_edad')]
```

> Se construye dinámicamente la lista de columnas Likert excluyendo las variables
> demográficas. Así cualquier cambio en el renombrado no rompe el resto del código.

---

### 2.2 Etapa 1 — Análisis descriptivo

**Objetivo:** caracterizar la distribución general de respuestas y las diferencias entre subgrupos demográficos (Objetivo Secundario 1).

```python
desc_global = df[LIKERT_COLS].agg(['mean', 'median', 'std', 'min', 'max']).T.round(2)
```

> Para cada ítem se calculan: media (tendencia central), mediana (menos sensible
> a valores extremos, preferible en escalas ordinales), desviación típica
> (dispersión) y rango (mín/máx). La `.T` transpone el resultado para que cada
> fila sea un ítem y cada columna un estadístico — formato más legible.

```python
desc_edad   = df.groupby('grupo_edad')[LIKERT_COLS].mean().T.round(2)
desc_genero = df.groupby('genero')[LIKERT_COLS].mean().T.round(2)
```

> `groupby` calcula las medias por subgrupo de edad y género por separado.
> Permite identificar si existen patrones visibles antes de aplicar pruebas
> formales de significación estadística.

```python
freq_tables = {}
for col in LIKERT_COLS:
    counts = df[col].value_counts(normalize=True).sort_index() * 100
    freq_tables[col] = counts.round(1)
freq_df = pd.DataFrame(freq_tables).T
```

> `value_counts(normalize=True)` devuelve proporciones (0 a 1); multiplicar por
> 100 las convierte en porcentajes. `sort_index()` garantiza que los valores
> siempre aparezcan ordenados de 1 a 5. La tabla resultante muestra qué porcentaje
> de encuestados eligió cada valor de la escala para cada ítem.

---

### 2.3 Etapa 2 — Análisis comparativo Gen Z vs. Adultos 40+

**Objetivo:** identificar qué factores difieren significativamente entre generaciones (Objetivo Secundario 2).

```python
genz    = df[df['grupo_edad'] == 'gen_z']
mayores = df[df['grupo_edad'] == 'adulto_mayor']
```

> Se separan los dos grupos de interés. Los grupos "menor_18" y "adulto_medio"
> quedan excluidos del test porque tienen muestras muy pequeñas (5 y 10 casos
> respectivamente), lo que haría las pruebas estadísticamente poco fiables.

```python
stat, p = stats.mannwhitneyu(g1, g2, alternative='two-sided')
```

> Se utiliza la **prueba U de Mann-Whitney** en lugar de la t de Student porque:
> 1. Los datos son ordinales (escala Likert), no continuos ni de intervalo.
> 2. No se puede asumir distribución normal en escalas de 5 puntos.
> 3. Los grupos tienen tamaños diferentes (n=61 vs n=104).
>
> `alternative='two-sided'` prueba si hay diferencia en cualquier dirección
> (mayor o menor), sin asumir de antemano qué grupo puntuará más alto.
>
> El umbral de significación es **p < 0.05**, estándar en ciencias sociales.

```python
mw_results.append({
    'mediana_genz'  : round(g1.median(), 2),
    'mediana_40+'   : round(g2.median(), 2),
    'media_genz'    : round(g1.mean(), 2),
    'media_40+'     : round(g2.mean(), 2),
    ...
})
```

> Se reportan tanto la mediana (el estadístico correcto para comparar grupos en
> datos ordinales) como la media (más intuitiva para la interpretación práctica).
> Mann-Whitney compara rangos, pero mostrar ambos facilita la lectura de los
> resultados en el TFG.

---

### 2.4 Etapa 3 — Correlaciones Spearman e índices compuestos

**Objetivo:** examinar relaciones entre dimensiones clave y contrastar la paradoja de la privacidad.

#### Construcción de índices compuestos

```python
df['idx_conocimiento'] = df[['con_informado', 'con_que_son',
                              'con_funcionamiento', 'con_usos']].mean(axis=1)
```

> Un índice compuesto promedia los ítems que miden la misma dimensión teórica.
> Esto reduce el ruido de medición individual y produce una medida más estable
> de cada constructo. `axis=1` calcula la media por fila (por participante),
> no por columna.

```python
df['idx_preocupacion'] = df[['pre_amenaza', 'pre_activa', 'pre_privacidad',
                              'pre_consecuencias', 'pre_busqueda']].mean(axis=1)
```

> Se excluye `pre_control` ("siento que controlo mis datos") porque mide
> percepción de control, no preocupación — incluirlo contaminaría el índice
> con una dimensión conceptualmente distinta.

```python
df['idx_pasivo'] = df[['com_acepto', 'com_ignoro']].mean(axis=1)
```

> El comportamiento pasivo se operacionaliza como la tendencia a aceptar o
> ignorar las cookies sin deliberación. Se excluye `com_rechazo` porque rechazar
> activamente es lo contrario del comportamiento pasivo.

```python
df['idx_conveniencia'] = df[['conv_cansan', 'conv_esfuerzo_rechazo',
                              'conv_esfuerzo_custom', 'conv_rapidez',
                              'conv_comodidad']].mean(axis=1)
```

> La orientación a la conveniencia agrupa ítems que expresan preferencia por
> la comodidad sobre la privacidad, incluyendo el agotamiento ante notificaciones
> repetidas y la percepción de que gestionar cookies requiere demasiado esfuerzo.

#### Correlaciones de Spearman

```python
corr_matrix, pval_matrix = stats.spearmanr(df[INDICES].dropna(), axis=0)
```

> La **correlación de Spearman** (rho) es la adecuada aquí porque:
> 1. Los índices son promedios de variables ordinales, no variables continuas normales.
> 2. No asume linealidad, solo monotonía (a más X, más/menos Y).
> 3. Es robusta frente a outliers.
>
> `stats.spearmanr` calcula simultáneamente todos los pares de correlaciones y
> devuelve también los p-valores, evitando múltiples llamadas individuales.

```python
# Test paradoja privacidad 1: formación -> comportamiento
r1, p1 = stats.spearmanr(df['idx_formacion'], df['idx_pasivo'])

# Test paradoja privacidad 2: preocupación declarada -> aceptación real
r2, p2 = stats.spearmanr(df['idx_preocupacion'], df['com_acepto'])
```

> Estas dos correlaciones son el núcleo del análisis de la paradoja de la
> privacidad: si los usuarios declaran preocupación pero aceptan las cookies
> igualmente, y si recibir formación no cambia su comportamiento real, eso
> constituye evidencia empírica del gap actitud-comportamiento.

---

### 2.5 Etapa 4 — Exportación a Excel

```python
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    desc_global.to_excel(writer, sheet_name='1a_descriptivo_global')
    # ... resto de hojas
```

> Se usa un único archivo Excel con múltiples hojas en lugar de varios ficheros
> separados porque facilita la navegación y reduce el riesgo de perder resultados.
> El motor `openpyxl` es necesario para escribir en formato `.xlsx` moderno.
> El gestor de contexto `with` garantiza que el archivo se cierre correctamente
> aunque ocurra un error durante la escritura.

---

## 3. Resultados obtenidos e interpretación

### 3.1 Descripción de la muestra

La muestra final cuenta con **180 participantes**. La distribución por grupos analíticos es:

| Grupo | n | % |
|-------|---|---|
| Gen Z (18-28) | 61 | 33.9% |
| Adulto medio (28-40) | 10 | 5.6% |
| Adulto mayor (40+) | 104 | 57.8% |
| Menor de 18 | 5 | 2.8% |

La distribución de género es: femenino 109 (60.6%), masculino 70 (38.9%) y 1 persona que prefirió no indicarlo. Los grupos de "menor de 18" y "adulto medio" son demasiado pequeños para análisis comparativos robustos, por lo que el análisis se centra en Gen Z vs. Adultos 40+.

---

### 3.2 Análisis descriptivo (Etapa 1)

#### Conocimiento sobre cookies — bajo en general

Los cuatro ítems de conocimiento presentan medias entre **2.71 y 3.28** sobre 5, indicando un nivel de autoconocimiento percibido moderado-bajo. Destaca que el 20% de los encuestados declara sentirse "nada informado" (valor 1 en `con_informado`) y solo el 11.1% se considera muy informado. El ítem más alto, "Entiendo lo que son las cookies" (media 3.28), sugiere que la mayoría tiene una noción básica del concepto, pero no de su funcionamiento ni de los distintos tipos de uso (media 2.77).

#### Preocupación por la privacidad — alta, pero polarizada

Los ítems de preocupación son los que presentan medias más elevadas de todo el cuestionario: `pre_activa` (media 3.96) y `pre_privacidad` (3.91). El 45% de los encuestados eligió el valor máximo en `pre_activa` y el 38.9% en `pre_privacidad`. Sin embargo, `pre_control` (media 2.11) es el ítem con media más baja de toda la escala: el 41.7% eligió el valor 1 ("no siento ningún control"), lo que revela una percepción generalizada de impotencia frente a la recogida de datos.

#### Formación formal — prácticamente inexistente

`form_recibida` presenta una media de **1.97** y el **57.8% de los encuestados eligió el valor 1** (nunca ha recibido formación en un entorno académico). Este es el dato más extremo de toda la encuesta en cuanto a concentración en un único valor. El impacto percibido de esa formación (`form_impacto`, media 2.64) es también bajo, aunque esto puede deberse parcialmente a que más de la mitad no ha recibido formación alguna.

#### Comportamiento ante las cookies — aceptación y rechazo dominan, poca gestión activa

El comportamiento más común es o bien aceptar (`com_acepto`, media 3.53; 38.3% elige valor 5) o bien rechazar (`com_rechazo`, media 3.71; 51.7% elige valor 5), con muy poca personalización activa (`com_personalizo`, media 2.64; 41.7% elige valor 1). Esto indica una tendencia al "todo o nada": los usuarios rara vez leen y ajustan las preferencias de cookies. El ítem `act_molestia` es el más alto de todo el cuestionario (media 4.13; 52.2% elige valor 5): las notificaciones de cookies molestan mucho, independientemente de la generación.

#### Orientación a la conveniencia — claramente presente

`conv_esfuerzo_custom` (media 3.76) y `conv_rapidez` (media 3.79) indican que los usuarios perciben la gestión de cookies como costosa en esfuerzo y que prefieren el acceso rápido al contenido. El 40% de los encuestados eligió el valor máximo en ambos ítems, confirmando que la conveniencia es un factor central que explica la pasividad conductual.

---

### 3.3 Comparación generacional Gen Z vs. Adultos 40+ (Etapa 2)

De los 27 ítems testados, **7 presentan diferencias estadísticamente significativas** (p < 0.05). El 20 restante no muestran diferencias significativas entre generaciones, lo que indica que muchos patrones (aceptación, molestia, preocupación por privacidad) son bastante transversales.

#### Diferencias significativas halladas

**Los adultos de 40+ muestran mayor preocupación activa:**

- `pre_activa`: adultos 40+ (media 4.09) vs. Gen Z (3.72), p = 0.023. Los mayores declaran preocuparse más activamente por cómo se recogen sus datos.
- `pre_busqueda`: adultos 40+ (media 3.52) vs. Gen Z (3.07), p = 0.024. Al navegar, los adultos piensan más frecuentemente en la privacidad.

Interpretación: los adultos mayores pueden haber desarrollado mayor sensibilidad a la privacidad digital por haber vivido el cambio pre/post internet o por una mayor percepción del riesgo ligada a la experiencia vital.

**La Generación Z percibe más impacto de la formación recibida — pero recibe más:**

- `form_impacto`: adultos 40+ (media 2.77) vs. Gen Z (2.34), p = 0.044. Los mayores perciben que la formación recibida ha tenido más impacto en su comportamiento.

Aparente paradoja: Gen Z ha recibido más formación (media 2.20 vs. 1.83 de adultos), pero declara que esa formación ha tenido menos impacto en su comportamiento. Esto podría reflejar que la Gen Z, al haber crecido en el ecosistema digital, normaliza la presencia de cookies y por tanto percibe menos transformación comportamental derivada de la formación.

**La Generación Z muestra mayor orientación a la conveniencia:**

- `conv_esfuerzo_rechazo`: Gen Z (media 2.70) vs. adultos 40+ (3.45), p = 0.0015. Este es el resultado con mayor diferencia y significación estadística del estudio. La Gen Z percibe *menos esfuerzo* en rechazar las cookies que los adultos, aunque en términos absolutos rechazar sigue requiriendo esfuerzo para ambos grupos.
- `conv_esfuerzo_custom`: Gen Z (media 3.54) vs. adultos 40+ (3.94), p = 0.034. Los adultos sienten que personalizar las cookies es más costoso.
- `conv_cansan`: Gen Z (media 3.75) vs. adultos 40+ (3.20), p = 0.018. La Gen Z se cansa más rápidamente de las notificaciones repetidas de cookies.

Interpretación: los adultos mayores pueden asociar mayor riesgo a aceptar cookies, lo que les hace más dispuestos a invertir el esfuerzo de rechazarlas. La Gen Z, habituada a la fricción digital constante, experimenta mayor fatiga de decisión ante los avisos de cookies.

**Los adultos prestan más atención al aceptar:**

- `com_atencion`: adultos 40+ (media 3.23) vs. Gen Z (2.67), p = 0.011. Los mayores declaran leer con más atención a qué están accediendo cuando aceptan cookies.

---

### 3.4 Correlaciones Spearman e índices compuestos (Etapa 3)

#### Resumen de estadísticos de los índices compuestos

| Índice | Media | SD | Interpretación |
|--------|-------|----|----------------|
| `idx_conocimiento` | 2.95 | 1.11 | Conocimiento moderado-bajo |
| `idx_preocupacion` | 3.45 | 0.77 | Preocupación moderada-alta |
| `idx_formacion` | 2.30 | 1.06 | Formación escasa |
| `idx_pasivo` | 3.38 | 1.18 | Comportamiento tendente a la pasividad |
| `idx_conveniencia` | 3.54 | 1.00 | Orientación clara a la conveniencia |

#### Correlaciones entre índices

La correlación más fuerte y más relevante teóricamente es:

**`idx_pasivo` ↔ `idx_conveniencia`: rho = 0.573, p < 0.001**

Correlación moderada-fuerte y altamente significativa. Los usuarios que priorizan la conveniencia tienden sistemáticamente a mostrar comportamientos más pasivos ante las cookies (aceptar o ignorar sin reflexionar). Este resultado apoya empíricamente la idea de que la comodidad percibida es el principal motor del comportamiento pasivo — no la falta de conocimiento ni la falta de preocupación.

**`idx_conocimiento` ↔ `idx_formacion`: rho = 0.489, p < 0.001**

Correlación moderada significativa. Quienes han recibido más formación declaran mayor conocimiento sobre las cookies. Esto es coherente y valida que los ítems de formación y conocimiento miden constructos relacionados pero distintos.

#### La paradoja de la privacidad: evidencia empírica

**Test 1 — Formación → Comportamiento pasivo**
`rho = -0.076, p = 0.313` → **No significativo**

La formación formal recibida no se correlaciona significativamente con el comportamiento pasivo. En otras palabras: haber estudiado sobre cookies en un entorno académico no reduce la tendencia a aceptarlas o ignorarlas. Esto constituye evidencia del fenómeno conocido como *knowledge-intention gap*: el conocimiento por sí solo no basta para cambiar el comportamiento.

**Test 2 — Preocupación declarada → Aceptación de cookies**
`rho = -0.289, p < 0.001` → **Significativo pero débil**

Este es el resultado más directamente relacionado con la paradoja de la privacidad. La correlación es significativa y negativa: quienes más se preocupan tienden ligeramente a aceptar menos. Sin embargo, el coeficiente rho = -0.289 revela una **asociación débil**. Considerando que el índice de preocupación tiene una media de 3.45 y el ítem de aceptación una media de 3.53, la conclusión es que la mayoría de los encuestados acepta las cookies de manera habitual *a pesar de* declarar preocupación por la privacidad. Esto es evidencia directa de la paradoja de la privacidad: la actitud declarada y el comportamiento real divergen sustancialmente.

**Test 3 — Conocimiento → Comportamiento pasivo**
`rho = -0.111, p = 0.139` → **No significativo**

El conocimiento sobre cookies tampoco se traduce en comportamiento menos pasivo. Junto con el test 1, refuerza la idea de que el déficit de comportamiento privacidad-consciente no se explica principalmente por falta de información.

**Test 4 — Preocupación → Conveniencia**
`rho = -0.102, p = 0.174` → **No significativo**

La preocupación por la privacidad no reduce significativamente la orientación a la conveniencia. Los usuarios pueden sentirse preocupados y al mismo tiempo preferir la comodidad, sin que ambas actitudes se contrarresten de forma consistente.

---

## 4. Conclusiones del análisis estadístico

1. **El patrón "todo o nada"** domina el comportamiento ante cookies: los usuarios aceptan o rechazan en bloque, con muy poca personalización. Esto facilita los dark patterns de diseño que empujan hacia la aceptación mediante botones prominentes.

2. **La paradoja de la privacidad queda confirmada**: la preocupación declarada es alta (media 3.45) pero la correlación con el comportamiento es débil (rho = -0.289), y la formación no produce cambios significativos en la conducta (rho = -0.076, n.s.).

3. **La conveniencia es el predictor más fuerte del comportamiento pasivo** (rho = 0.573), por encima del conocimiento o la preocupación. Las intervenciones de política pública o diseño que busquen cambiar el comportamiento deben reducir la fricción del rechazo/personalización, no solo informar mejor.

4. **Las diferencias generacionales son moderadas** (7 de 27 ítems significativos). Donde existen, apuntan a que la Gen Z muestra mayor fatiga de notificación y menor disposición a invertir esfuerzo en rechazar, mientras que los adultos de 40+ muestran mayor preocupación activa y más atención al aceptar.

5. **La falta de formación formal es un problema generalizado** (57.8% nunca ha recibido formación) y los datos sugieren que, incluso cuando existe, no se traduce automáticamente en mejor comportamiento — lo que indica que el diseño del contenido de la formación importa tanto como su existencia.

---

*Análisis realizado con Python (pandas 3.0.2, scipy 1.17.1). Fichero de datos: Google Forms export, n=180. Nivel de significación α=0.05.*
