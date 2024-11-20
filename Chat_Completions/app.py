from flask import Flask, request, jsonify
from services.pdf_service import extract_text_from_pdf
from services.gpt_service import consultar_con_historial
from services.conversation_service import Conversacion

app = Flask(__name__)

try:
    pdf_content = extract_text_from_pdf("../Docs/UCACUE_TICS.pdf")
    conversacion = Conversacion(contexto=pdf_content)
except RuntimeError as e:
    pdf_content = None
    print(f"Error al cargar el PDF: {e}")

# --- PREGUNTAS CON HISTORIAL DE CONVERSACIÓN ---
@app.route('/preguntar', methods=['POST'])
def preguntar():
    data = request.json
    pregunta = data.get('pregunta')

    if not pregunta:
        return jsonify({"error": "La pregunta es requerida"}), 400

    try:
        conversacion.agregar_mensaje_usuario(pregunta)
        respuesta = consultar_con_historial(conversacion.obtener_historial())
        conversacion.agregar_mensaje_asistente(respuesta)
        return jsonify({"respuesta": respuesta})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503

# --- HISTORIAL DE CONVERSACIÓN ---
@app.route('/historial', methods=['GET'])
def obtener_historial():
    return jsonify({"historial": conversacion.obtener_historial()})

# --- BORRAR HISTORIAL DE CONVERSACIÓN ---
@app.route('/limpiar', methods=['POST'])
def limpiar_historial():
    conversacion.limpiar_historial(pdf_content)
    return jsonify({"mensaje": "Historial limpiado"})

if __name__ == '__main__':
    app.run(debug=True)
