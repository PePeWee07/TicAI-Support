from flask import Flask, request, jsonify
import services.pdf_service as pdf_service
import services.openai_service as openai_service
from config.logging_config import logger
import os
import atexit

app = Flask(__name__)

logger.info("Iniciando Servicio...")

# ==================================================
# Cargar archivo PDF
# ==================================================
pdf_path = os.path.join(os.path.dirname(__file__), 'Docs/UCACUE_TICS.pdf')
if not os.path.exists(pdf_path):
    logger.error(f"El archivo PDF no se encuentra en la ruta especificada: {pdf_path}")
    raise FileNotFoundError(f"El archivo PDF no se encuentra en la ruta especificada: {pdf_path}")

try:
    context = pdf_service.extract_text_from_pdf(pdf_path)
    logger.info("Texto extraído del PDF correctamente.")
except Exception as e:
    logger.error(f"Error inesperado al procesar el PDF: {e}")
    context = None

# ==================================================
# Inicializar el asistente
# ==================================================
assistant = None
try:
    if context:
        assistant = openai_service.verify_or_create_assistant(context)
    else:
        logger.error("No se pudo extraer el contexto del PDF. El asistente no será inicializado.")
except ValueError as e:
    logger.error(f"Advertencia: {e}. El asistente debe ser creado manualmente.")
except Exception as e:
    logger.error(f"Error inesperado al inicializar el asistente: {e}")
    
    
# ==================================================
# Ruta para preguntar al asistente
# ==================================================
@app.route('/ask', methods=['POST'])
def process_user_input():
    if assistant is None:
        return jsonify({"error": "El asistente no está disponible debido a un error."}), 500

    data = request.json
    ask = data.get('ask')
    thread_id = data.get('thread_id')
    name = data.get('name')

    if not ask:
        return jsonify({"error": "Se requiere una pregunta."}), 400
    if not name:
        return jsonify({"error": "Se requiere un nombre."}), 400

    try:
        answer, thread_id = openai_service.get_response(assistant.id, ask, thread_id, name)
        return jsonify({"answer": answer, "thread_id": thread_id}), 200
    except ValueError as e:
        logger.error(f"Error al obtener respuesta: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error inesperado al obtener respuesta: {e}")
        return jsonify({"error": str(e)}), 500


# ==================================================
# Obtener el historial de mensajes de un hilo
# ==================================================
@app.route('/history', methods=['GET'])
def get_history():
    thread_id = request.args.get('thread_id')

    if not thread_id:
        return jsonify({"error": "Se requiere un thread_id."}), 400

    try:
        history = openai_service.view_history(thread_id)
        return jsonify({"history": history}), 200
    except ValueError as e:
        logger.error(f"Error al obtener historial: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error inesperado al obtener historial: {e}")
        return jsonify({"error": str(e)}), 500


# ==================================================
# Eliminar un hilo
# ==================================================
@app.route('/delete-thread-id', methods=['DELETE'])
def delete_thread_endpoint():
    thread_id = request.args.get('thread_id')

    if not thread_id:
        return jsonify({"error": "Se requiere un thread_id."}), 400

    try:
        message = openai_service.delete_thread(thread_id)
        return jsonify({"message": message}), 200
    except ValueError as e:
        logger.error(f"Error al eliminar hilo: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error inesperado al eliminar hilo: {e}")
        return jsonify({"error": str(e)}), 500


# ==================================================
# Eliminar multiples hilos
# ==================================================
@app.route('/delete-threads-ids', methods=['DELETE'])
def delete_threads_endpoint():
    data = request.get_json()
    if not data or 'ids' not in data:
        return jsonify({"error": "Se requiere una lista de IDs de hilos en el campo 'ids'."}), 400

    ids = data['ids']
    if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
        return jsonify({"error": "El campo 'ids' debe ser una lista de strings."}), 400

    try:
        message = openai_service.delete_threads(ids)
        logger.info(f"Hilos eliminados: {message}")
        return jsonify({"message": message}), 200
    except TypeError as e:
        logger.error(f"Error al eliminar hilos: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error inesperado al eliminar hilos: {e}")
        return jsonify({"error": {e}}), 500


# ==================================================
# Cerrar recursos al salir
# ==================================================
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
