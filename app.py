from flask import Flask, request, jsonify
from services.pdf_service import extract_text_from_pdf
from services.openai_service import obtener_respuesta, ver_historial, eliminar_hilo, eliminar_hilos, verificar_o_crear_asistente
from config.logging_config import logger
import os
import atexit

app = Flask(__name__)

logger.info("Iniciando aplicación...")

# Ruta al archivo PDF
pdf_path = os.path.join(os.path.dirname(__file__), 'Docs/UCACUE_TICS.pdf')
if not os.path.exists(pdf_path):
    logger.error(f"El archivo PDF no se encuentra en la ruta especificada: {pdf_path}")
    raise FileNotFoundError(f"El archivo PDF no se encuentra en la ruta especificada: {pdf_path}")


# Extraer texto del PDF al iniciar la aplicación
try:
    contexto = extract_text_from_pdf(pdf_path)
    logger.info("Texto extraído del PDF correctamente.")
except Exception as e:
    logger.error(f"Error inesperado al procesar el PDF: {e}")
    contexto = None


# Inicializar el asistente
assistant = None
try:
    if contexto:
        assistant = verificar_o_crear_asistente(contexto)
    else:
        logger.error("No se pudo extraer el contexto del PDF. El asistente no será inicializado.")
except ValueError as e:
    logger.error(f"Advertencia: {e}. El asistente debe ser creado manualmente.")
except Exception as e:
    logger.error(f"Error inesperado al inicializar el asistente: {e}")
    
    
# Ruta para preguntar al asistente
@app.route('/preguntar', methods=['POST'])
def preguntar():
    if contexto is None:
        return jsonify({"error": "El contexto no está disponible debido a un error al procesar el PDF."}), 500

    if assistant is None:
        return jsonify({"error": "El asistente no está disponible debido a un error."}), 500

    data = request.json
    pregunta = data.get('pregunta')
    thread_id = data.get('thread_id')
    nombre = data.get('nombre')

    if not pregunta:
        return jsonify({"error": "Se requiere una pregunta."}), 400
    if not nombre:
        return jsonify({"error": "Se requiere un nombre."}), 400

    try:
        respuesta, thread_id = obtener_respuesta(assistant.id, pregunta, thread_id, nombre)
        return jsonify({"respuesta": respuesta, "thread_id": thread_id}), 200
    except ValueError as e:
        logger.error(f"Error al obtener respuesta: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error inesperado al obtener respuesta: {e}")
        return jsonify({"error": str(e)}), 500

# Ruta para obtener el historial de mensajes de un hilo
@app.route('/historial', methods=['GET'])
def obtener_historial():
    thread_id = request.args.get('thread_id')

    if not thread_id:
        return jsonify({"error": "Se requiere un thread_id."}), 400

    try:
        historial = ver_historial(thread_id)
        return jsonify({"historial": historial}), 200
    except ValueError as e:
        logger.error(f"Error al obtener historial: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error inesperado al obtener historial: {e}")
        return jsonify({"error": str(e)}), 500

# Ruta para eliminar un hilo
@app.route('/eliminar-hilo', methods=['DELETE'])
def eliminar_hilo_endpoint():
    thread_id = request.args.get('thread_id')

    if not thread_id:
        return jsonify({"error": "Se requiere un thread_id."}), 400

    try:
        mensaje = eliminar_hilo(thread_id)
        return jsonify({"mensaje": mensaje}), 200
    except ValueError as e:
        logger.error(f"Error al eliminar hilo: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error inesperado al eliminar hilo: {e}")
        return jsonify({"error": str(e)}), 500

# Ruta para eliminar hilos
@app.route('/eliminar-hilos', methods=['DELETE'])
def eliminar_hilos_endpoint():
    data = request.get_json()
    if not data or 'ids' not in data:
        return jsonify({"error": "Se requiere una lista de IDs de hilos en el campo 'ids'."}), 400

    ids = data['ids']
    if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
        return jsonify({"error": "El campo 'ids' debe ser una lista de strings."}), 400

    try:
        mensajes = eliminar_hilos(ids)
        logger.info(f"Hilos eliminados: {mensajes}")
        return jsonify({"mensajes": mensajes}), 200
    except TypeError as e:
        logger.error(f"Error al eliminar hilos: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error inesperado al eliminar hilos: {e}")
        return jsonify({"error": {e}}), 500

# Cerrar recursos al salir
def clean_up():
    logger.info("Cerrando aplicación y limpiando recursos.")
    
atexit.register(clean_up)

if __name__ == '__main__':
    app.run(
    host="0.0.0.0", 
    port=5000, 
    debug=False, 
    threaded=True, 
    #ssl_context=('cert.pem', 'key.pem')
)

