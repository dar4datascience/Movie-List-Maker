# Biblioteca de Películas y Series - Sitio Web Quarto

Este sitio web muestra una colección de 257 títulos de películas y series de TV extraídos de transcripciones de audio.

## Características

- **🔍 Búsqueda Interactiva**: Tabla interactiva con Observable JS para buscar y filtrar títulos en tiempo real
- **📊 Estadísticas**: Resumen de la colección con contadores
- **🎬 Enlaces IMDB**: Enlaces directos a IMDB cuando los IDs están disponibles
- **🎨 Tema Materia**: Diseño limpio y profesional orientado a biblioteca
- **🌐 En Español**: Toda la interfaz está en español

## Estructura del Sitio

1. **Buscar y Filtrar** (Primera sección)
   - Tabla interactiva con Observable JS
   - Búsqueda en tiempo real
   - Enlaces a IMDB

2. **Resumen de la Biblioteca**
   - Estadísticas de la colección
   - Total de títulos
   - Títulos con datos de IMDB

3. **Explorar por Título**
   - Tarjetas organizadas alfabéticamente (A-Z)
   - Diseño de cuadrícula responsivo
   - Efectos hover

## Cómo Renderizar el Sitio

### Opción 1: Renderizar una vez
```bash
source venv/bin/activate
quarto render index.qmd
```

El HTML se generará en `docs/index.html`

### Opción 2: Vista previa con auto-recarga
```bash
source venv/bin/activate
quarto preview index.qmd --no-browser --port 8080
```

Luego abre http://localhost:8080 en tu navegador.

## Archivos Principales

- `index.qmd` - Documento principal de Quarto
- `styles.css` - Estilos personalizados para el tema de biblioteca
- `_quarto.yml` - Configuración de Quarto
- `unified_movie_list.json` - Datos de las películas (fuente de datos)

## Tecnologías Utilizadas

- **Quarto**: Framework de publicación científica y técnica
- **Observable JS**: Para la tabla interactiva y búsqueda
- **Python**: Para procesamiento de datos y generación de contenido
- **Materia Theme**: Tema Bootstrap Material Design
- **CSS personalizado**: Para el diseño orientado a biblioteca

## Despliegue

El sitio se genera como HTML estático en la carpeta `docs/`, lo que lo hace fácil de desplegar en:

- GitHub Pages
- Netlify
- Vercel
- Cualquier servidor de archivos estáticos

## Próximos Pasos

Para enriquecer el sitio con datos de IMDB:

1. Obtén una clave API gratuita de OMDB: http://www.omdbapi.com/apikey.aspx
2. Ejecuta el script de enriquecimiento:
   ```bash
   python enrich_with_imdb.py
   ```
3. Re-renderiza el sitio para ver los enlaces de IMDB actualizados
