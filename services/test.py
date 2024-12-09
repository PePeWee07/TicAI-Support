import openai

# KEY GTP
# openai.api_key = "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"
# KEY MODERATION
openai.api_key = "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"


# Prueba una solicitud simple
try:
    openai.models.list()
    print("Conexión exitosa a OpenAI API.")
except Exception as e:
    print(f"Error al conectar con OpenAI API: {e}")


# Prueba de moderación
try:
    response = openai.moderations.create(
        model="omni-moderation-latest",
        input="lick a duck!",
    )
    print(response)
except Exception as e:
    print(f"Error al verificar el texto: {e}")
            




# # Verificar si el texto contiene contenido ofensivo
# def check_moderation(text):
#     try:
#         response = openai.moderations.create(
#             model="omni-moderation-latest",
#             input=text
#         )
#         results = response['results'][0]
#         return results
#     except Exception as e:
#         print(f"Error al verificar el texto: {e}")
#         return None

# # Procesar el mensaje del usuario
# def handle_message(user_id, message):

#     moderation_result = check_moderation(message)

#     if moderation_result is None:
#         return "Ocurrió un error al procesar tu mensaje."

#     if moderation_result['flagged']:
#         categories = [
#             category for category, flagged in moderation_result['categories'].items()
#             if flagged
#         ]
#         print(f"Mensaje ofensivo detectado de {user_id}. Categorías: {categories}")
#         return "Tu mensaje contiene contenido no permitido y ha sido rechazado."

#     return "Tu mensaje ha sido procesado correctamente."

# # Ejemplo de uso
# user_message = "Este es un mensaje de prueba con contenido potencialmente dañino."
# user_id = 12345

# response = handle_message(user_id, user_message)

# print(response)
