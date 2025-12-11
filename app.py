from flask import Flask, render_template, request, jsonify, send_file
import requests
import json
import pandas as pd
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
BASE_URL = "https://repository.ucatolica.edu.co"

# Traducciones de metadatos
TRADUCCIONES = {
    "dc.title": "Título",
    "dc.title.translated": "Título Traducido",
    "dc.contributor.author": "Autor(es)",
    "dc.contributor.advisor": "Director(es)",
    "dc.description.abstract": "Resumen",
    "dc.identifier.uri": "URI",
    "dc.identifier.url": "URL",
    "dc.identifier.eissn": "EISSN",
    "dc.identifier.issn": "ISSN",
    "dc.date.issued": "Fecha de Publicación",
    "dc.date.accessioned": "Fecha de Acceso",
    "dc.date.available": "Fecha Disponible",
    "dc.publisher": "Editorial",
    "dc.publisher.program": "Programa Académico",
    "dc.publisher.faculty": "Facultad",
    "dc.subject": "Palabras Clave",
    "dc.language.iso": "Idioma",
    "dc.format.mimetype": "Formato",
    "dc.type": "Tipo de Documento",
    "dc.type.coar": "Tipo COAR",
    "dc.type.coarversion": "Versión COAR",
    "dc.type.content": "Tipo de Contenido",
    "dc.type.driver": "Tipo Driver",
    "dc.type.local": "Tipo Local",
    "dc.type.redcol": "Tipo RedCol",
    "dc.type.version": "Versión",
    "dc.rights": "Derechos",
    "dc.rights.accessrights": "Derechos de Acceso",
    "dc.rights.coar": "Derechos COAR",
    "dc.rights.uri": "URI de Derechos",
    "dc.source": "Fuente",
    "dc.relation.bitstream": "Bitstream",
    "dc.relation.citationedition": "Edición",
    "dc.relation.citationendpage": "Página Final",
    "dc.relation.citationissue": "Número",
    "dc.relation.citationstartpage": "Página Inicial",
    "dc.relation.ispartofjournal": "Revista",
    "dc.relation.references": "Referencias",
    "dspace.entity.type": "Tipo de Entidad"
}

# ---------------------------
#  BÚSQUEDA DE ITEMS
# ---------------------------
def buscar_items(query, modo='colecciones'):
    all_results = []
    size = 20
    page = 0
    
    # Construir query según el modo de búsqueda
    if modo == 'titulo':
        search_query = f'dc.title:"{query}"'
    elif modo == 'autor':
        search_query = f'dc.contributor.author:"{query}"'
    elif modo == 'fecha':
        search_query = f'dc.date.issued:{query}'
    elif modo == 'materias':
        search_query = f'dc.subject:"{query}"'
    elif modo == 'tipo':
        search_query = f'dc.type:"{query}"'
    elif modo == 'ods':
        search_query = f'dc.subject.ods:"{query}"'
    else:  # colecciones o búsqueda general
        search_query = query

    while True:
        url = f"{BASE_URL}/server/api/discover/search/objects?query={search_query}&page={page}&size={size}"
        
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en la búsqueda: {e}")
            break

        try:
            items = data["_embedded"]["searchResult"]["_embedded"]["objects"]
        except KeyError:
            break

        if not items:
            break

        for obj in items:
            item = obj["_embedded"]["indexableObject"]
            uuid = item.get("uuid")
            title = item.get("name", "[Sin título]")
            api_url = f"{BASE_URL}/server/api/core/items/{uuid}"

            all_results.append({
                "uuid": uuid,
                "title": title,
                "url_api": api_url
            })

        page += 1

    return all_results

# ---------------------------
#  EXTRAER METADATOS DETALLADOS
# ---------------------------
def extraer_metadatos(uuid):
    url = f"{BASE_URL}/server/api/core/items/{uuid}"
    res = requests.get(url, headers={"Accept": "application/json"})
    if res.status_code != 200:
        return {"UUID": uuid, "Error": "No se pudo acceder a la API"}

    data = res.json()
    metadata = data.get("metadata", {})
    plano = {"UUID": uuid}

    for key, valores in metadata.items():
        etiqueta = TRADUCCIONES.get(key, key)
        plano[etiqueta] = [v["value"] for v in valores]

    return plano

# ---------------------------
#  RUTA PRINCIPAL
# ---------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = []
    if request.method == 'POST':
        query = request.form['query']
        modo = request.form.get('modo', 'colecciones')
        resultados = buscar_items(query, modo)

    return render_template('index.html', resultados=resultados)

# ---------------------------
#  EXTRAER SELECCIONADOS
# ---------------------------
@app.route('/extraer', methods=['POST'])
def extraer():
    uuids = request.form.getlist('seleccionados')
    
    if not uuids:
        return render_template('metadatos.html', metadatos=[], mensaje="No se seleccionó ningún documento")
    
    metadatos = []
    for uuid in uuids:
        try:
            meta = extraer_metadatos(uuid)
            metadatos.append(meta)
        except Exception as e:
            metadatos.append({"UUID": uuid, "Error": str(e)})
    
    return render_template('metadatos.html', metadatos=metadatos, mensaje=None)

# ---------------------------
#  VER JSON RAW INDIVIDUAL
# ---------------------------
@app.route('/ver_json')
def ver_json():
    uuid = request.args.get('uuid')
    if not uuid:
        return "No se especificó el UUID", 400

    try:
        api_url = f"{BASE_URL}/server/api/core/items/{uuid}"
        res = requests.get(api_url)
        res.raise_for_status()
        json_data = res.json()
        
        # Procesar metadatos con traducciones
        metadata_traducido = {}
        if 'metadata' in json_data:
            for key, valores in json_data['metadata'].items():
                etiqueta = TRADUCCIONES.get(key, key)
                metadata_traducido[etiqueta] = valores

        return render_template('ver_json.html', json_data=json_data, metadata_traducido=metadata_traducido, api_url=api_url)

    except Exception as e:
        return f"Error al consultar la API: {e}", 500

# ---------------------------
#  EXPORTAR A JSON
# ---------------------------
@app.route('/exportar/json', methods=['POST'])
def exportar_json():
    uuids = request.form.getlist('seleccionados')
    
    if not uuids:
        return jsonify({"error": "No se seleccionó ningún documento"}), 400
    
    metadatos = []
    for uuid in uuids:
        try:
            meta = extraer_metadatos(uuid)
            metadatos.append(meta)
        except Exception as e:
            metadatos.append({"UUID": uuid, "Error": str(e)})
    
    # Crear archivo JSON
    json_data = json.dumps(metadatos, ensure_ascii=False, indent=2)
    buffer = BytesIO()
    buffer.write(json_data.encode('utf-8'))
    buffer.seek(0)
    
    filename = f"metadatos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return send_file(buffer, mimetype='application/json', as_attachment=True, download_name=filename)

# ---------------------------
#  EXPORTAR A EXCEL
# ---------------------------
@app.route('/exportar/excel', methods=['POST'])
def exportar_excel():
    uuids = request.form.getlist('seleccionados')
    
    if not uuids:
        return jsonify({"error": "No se seleccionó ningún documento"}), 400
    
    metadatos = []
    for uuid in uuids:
        try:
            meta = extraer_metadatos(uuid)
            metadatos.append(meta)
        except Exception as e:
            metadatos.append({"UUID": uuid, "Error": str(e)})
    
    # Preparar datos para Excel
    data_for_excel = []
    for doc in metadatos:
        row = {}
        for key, values in doc.items():
            if isinstance(values, list):
                row[key] = ", ".join(str(v) for v in values)
            else:
                row[key] = values
        data_for_excel.append(row)
    
    # Crear archivo Excel
    df = pd.DataFrame(data_for_excel)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Metadatos')
    buffer.seek(0)
    
    filename = f"metadatos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                     as_attachment=True, download_name=filename)

# ---------------------------
#  INICIO
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
