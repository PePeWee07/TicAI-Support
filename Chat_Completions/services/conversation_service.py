class Conversacion:
    def __init__(self, contexto: str):
        self._inicializar_historial(contexto)

    def _inicializar_historial(self, contexto: str):
        self.historial = [
            {"role": "system", "content": "Eres un asistente diseñado para proporcionar soporte tecnológico en el área de TIC de la Universidad Católica de Cuenca."},
            {"role": "system", "content": "Responde siempre de forma clara y directa basándote únicamente en el contenido proporcionado. No menciones ni hagas referencia al documento en tus respuestas."},
            {"role": "system", "content": "Si no puedes encontrar la información en el contenido proporcionado, indica que no tienes suficiente información para responder esa pregunta específicamente, pero no menciones el documento."},
            {"role": "system", "content": "Nunca te limites a mencionar que existen canales de atención sin incluir sus detalles completos como numeros o correos electronicos o direciones si lo tienen. Responde de forma que el usuario pueda actuar directamente con la información dada."},
            {"role": "system", "content": f"Contenido del documento: {contexto}"}
        ]

    def agregar_mensaje_usuario(self, mensaje: str):
        self.historial.append({"role": "user", "content": mensaje})

    def agregar_mensaje_asistente(self, mensaje: str):
        self.historial.append({"role": "assistant", "content": mensaje})

    def obtener_historial(self) -> list:
        return self.historial

    def limpiar_historial(self, contexto: str):
        self._inicializar_historial(contexto)
