# OEIS Maxima Snippets Collection

Este repositorio contiene una colección organizada de códigos de **Maxima / wxMaxima** extraídos de la **[OEIS (On-Line Encyclopedia of Integer Sequences)](https://oeis.org/)**.

Los snippets han sido procesados y estructurados automáticamente en lotes ejecutables (`.wxm`) con el encabezado y metadatos nativos de wxMaxima.

---

## 🛠️ Proceso de generación

Durante esta sesión se procesó el archivo `maxima_snippets.txt` para extraer exclusivamente los bloques de código de Maxima.

- Se identificaron bloques de sucesiones que comienzan con `Found in oeisdata/seq`.
- Se seleccionaron sólo las líneas `%o ... (Maxima)` que contenían identificadores OEIS como `A000045` y la etiqueta `(Maxima)`.
- Se ignoraron los snippets de otros lenguajes (Python, SageMath, PARI, Magma, GAP, Haskell, Julia, etc.).
- El código se copió tal cual, sin modificaciones, respetando saltos de línea y sangrías.

Se generaron `2818` archivos `.wxm`, organizados en carpetas según los tres primeros dígitos numéricos del identificador OEIS.

## 📁 Estructura del Repositorio

Los archivos están agrupados en carpetas nombradas según los tres primeros dígitos numéricos del identificador A-number de la OEIS. Cada archivo `.wxm` corresponde al código completo de una sucesión en particular:

```text
.
├── A000/
│   ├── A000045.wxm   # Secuencia de Fibonacci
│   ├── A000079.wxm   # Potencias de 2
│   └── ...
├── A001/
│   ├── A001234.wxm
│   └── ...
└── README.md