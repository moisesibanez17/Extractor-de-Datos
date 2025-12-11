# Extractor de Documentos - Universidad Católica de Colombia

Aplicación web para buscar y extraer metadatos de documentos del repositorio institucional de la Universidad Católica de Colombia.

## Características

- 🔍 Búsqueda de documentos en el repositorio institucional
- 📊 Visualización de metadatos organizados
- 💾 Exportación de metadatos a JSON
- 📗 Exportación de metadatos a Excel
- 🎨 Interfaz moderna y responsive
- ⚡ Indicador de progreso en tiempo real

## Requisitos

- Python 3.8 o superior
- pip

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/moisesibanez17/Extractor-de-Datos.git
cd app
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Ejecuta la aplicación:
```bash
python app.py
```

2. Abre tu navegador en `http://127.0.0.1:5000`

3. Busca documentos usando palabras clave

4. Selecciona los documentos de interés

5. Exporta los metadatos en el formato deseado (JSON o Excel)

## Estructura del Proyecto

```
.
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias del proyecto
├── static/
│   ├── css/
│   │   └── styles.css    # Estilos CSS
│   └── images/
│       └── logo.png      # Logo institucional
└── templates/
    ├── index.html        # Página principal
    ├── metadatos.html    # Vista de metadatos
    └── ver_json.html     # Vista de detalles
```

## Tecnologías

- **Backend**: Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Exportación**: Pandas, OpenPyXL
- **API**: DSpace REST API

## Licencia

Este proyecto está desarrollado para la Universidad Católica de Colombia.
