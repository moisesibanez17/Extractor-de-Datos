import requests
import re
from flask import Flask, request, render_template

app = Flask(__name__)

# Diccionario para traducir claves técnicas a nombres legibles
TRADUCCIONES = {
    "dc.title": "Título",
    "dc.contributor.author": "Autor(es)",
    "dc.contributor.advisor": "Director(es)",
    "dc.description.abstract": "Resumen",
    "dc.description": "Descripción",
    "dc.date.issued": "Fecha de Publicación",
    "dc.identifier.uri": "Enlace",
    "dc.description.tableofcontents": "Tabla de Contenidos",
    "dc.publisher": "Editorial",
    "dc.language.iso": "Idioma",
    "dc.subject": "Temas",
    "dc.rights": "Derechos",
    "dc.format.extent": "Extensión",
    "dc.format.mimetype": "Formato",
    "dc.description.degreelevel": "Nivel del Título",
    "dc.description.degreename": "Nombre del Título",
    "dc.publisher.program": "Programa Académico",
    "dc.publisher.faculty": "Facultad",
    "dc.publisher.place": "Lugar de publicación",
    "dc.relation.references": "Referencias",
    "dc.rights.accessrights": "Derechos de Acceso",
    "dc.rights.coar": "Derechos coar",
    "dc.rights.license": "Derechos de licencia",
    "dc.rights.uri": "Licencia",
    "dc.subject.armarc": "Temas ArmARC",
    "dc.subject.ddc": "Clasificación DDC",
    "dc.subject.ods": "Objetivos de Desarrollo Sostenible (ODS)",
    "dc.subject.proposal": "Temas de Propuesta",
    "dc.type": "Tipo de Documento",
    "dc.type.coar": "Tipo COAR",
    "dc.type.coarversion": "Versión COAR",
    "dc.type.content": "Tipo de Contenido",
    "dc.type.driver": "Tipo (Driver)",
    "dc.type.version": "Versión del Documento",
    "dspace.entity.type": "Entidad DSpace",
    "dc.identifier.citation": "Citacion"
}

def extraer_uuid(desde_url):
    match = re.search(r'([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})', desde_url)
    return match.group(1) if match else None

def extraer_metadatos(uuid):
    api_url = f"https://repository.ucatolica.edu.co/server/api/core/items/{uuid}"
    response = requests.get(api_url, headers={"Accept": "application/json"})
    if response.status_code != 200:
        return None

    json_data = response.json()
    try:
        metadata = json_data["metadata"]
    except KeyError:
        return {}

    plano = {}
    for key, valores in metadata.items():
        etiqueta = TRADUCCIONES.get(key, key)  # Usa la traducción si existe
        plano[etiqueta] = [entry["value"] for entry in valores]

    return plano

@app.route('/', methods=['GET', 'POST'])
def index():
    metadatos = {}
    error = None
    if request.method == 'POST':
        url = request.form['url']
        uuid = extraer_uuid(url)
        if uuid:
            metadatos = extraer_metadatos(uuid)
            if metadatos is None:
                error = "❌ No se pudo acceder a la API."
            elif not metadatos:
                error = "⚠️ No se encontraron metadatos."
        else:
            error = "❌ URL inválida."

    return render_template('index.html', metadatos=metadatos, error=error)

if __name__ == '__main__':
    app.run(debug=True)
