from functools import wraps
from flask import request, jsonify
from services.openAIService import moderation_text
from services.openAIService import num_tokens_from_string

def moderation_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        if data and 'ask' in data:
            texto = data['ask']
            if moderation_text(texto):
                response = {
                    "info": (
                        "Lamento informarte que ese tipo de comentarios no son apropiados. "
                        "Si continúas violando las políticas de la Universidad Católica de Cuenca, serás bloqueado."
                    ),
                    'moderation': True
                }
                return jsonify(response), 400
        return f(*args, **kwargs)
    return decorated_function

def validate_token_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        if data and 'ask' in data:
            texto = data['ask']
            if num_tokens_from_string(answerToToken=texto) > 500:
                response = {
                    "info": "El texto ingresado es demasiado largo. Por favor, resume tu consulta e inténtalo nuevamente."
                }
                return jsonify(response), 400
        return f(*args, **kwargs)
    return decorated_function
