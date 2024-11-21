# TicAI Support  
**La herramienta de soporte académico y técnico impulsada por inteligencia artificial para la Universidad Católica de Cuenca.**

---

## Descripción  
**TicAI Support** es una solución innovadora que utiliza tecnología avanzada de inteligencia artificial para mejorar el soporte académico y técnico dentro de la Universidad Católica de Cuenca. Diseñada para estudiantes, docentes y personal administrativo, la plataforma facilita la resolución de consultas relacionadas con servicios TIC, asistencia académica y procesos administrativos, optimizando tiempos y mejorando la experiencia de los usuarios.

**Propósito:** Automatizar y facilitar el acceso a información clave y soporte relacionado con la Dirección de Tecnologías de la Información y Comunicación (TICS), brindando respuestas inmediatas y personalizadas.

---

## Características

### 1. **Soporte técnico automatizado**
- Resolución de preguntas frecuentes sobre plataformas como:
  - ERP University.
  - Office 365.
  - Plataforma EVEA.
- Asistencia técnica para gestión de redes y uso de herramientas digitales.

### 2. **Consultas académicas personalizadas**
- Información sobre el uso de plataformas virtuales de enseñanza-aprendizaje.
- Capacitación virtual sobre tecnologías relacionadas con TIC.

### 3. **Acceso multicanal**
- Disponible 24/7 para consultas a través de un portal centralizado.
- Integración con los servicios actuales del DTIC.

### 4. **Optimización del tiempo**
- Procesamiento inmediato de incidencias comunes:
  - Problemas de acceso a plataformas.
  - Problemas de conectividad o configuración.

### 5. **Eficiencia en el soporte**
- Automatización de respuestas para disminuir la carga del personal técnico humano.
- Soluciones rápidas y preconfiguradas para incidencias frecuentes.

---

## Uso sugerido
Esta herramienta puede ser utilizada por:
- **Estudiantes**: Para obtener soporte técnico o académico relacionado con plataformas virtuales.
- **Docentes**: Para asistencia en el uso de herramientas tecnológicas en su labor educativa.
- **Administrativos**: Para resolver problemas técnicos y gestionar accesos a los sistemas internos.

---

**TicAI Support: Tu aliado en la educación y soporte técnico con inteligencia artificial.**

---

## Instalar  
Para instalar las dependencias necesarias, sigue los pasos a continuación:

```bash
# Paso 1: Instalar OpenAI
pip install openai  

# Paso 2: Instalar PyPDF2 para manipular archivos PDF
pip install PyPDF2

# Paso 3: Instalar Flask para el servidor web
pip install Flask

# Paso 4: Instalar python-dotenv para manejar variables de entorno
pip install python-dotenv

# Paso 5: Instalar tiktoken para tokenización eficiente
pip install tiktoken
```

## Cómo usar:
1. Asegúrate de incluir un archivo `.env` en la raíz de tu proyecto con las siguientes variables de entorno:

```plaintext
OPENAI_API_KEY=tu_clave_api_de_openai
ASSISTANT_ID=tu_id_assistant
```

2. Ejecuta la aplicación con el siguiente comando:

```bash
python app.py
```

## Preguntas frecuentes:
1. ¿Qué servicios ofrece el DTIC?
2. ¿Cómo puedo solicitar soporte técnico?
3. ¿Qué debo hacer si tengo problemas con la red o conectividad?
4. ¿Cómo solicito la recarga de tóner o cartuchos?
5. ¿Cómo actualizo información en el sitio web institucional?


## Estructura de OpenAi
```json
{
  "object": "list",
  "first_id": "msg_xxxxxxxxxxxxxxxxxxxxxxx",
  "last_id": "msg_yyyyyyyyyyyyyyyyyyyyyyyy",
  "has_more": false,
  "data": [
    {
      "id": "msg_xxxxxxxxxxxxxxxxxxxxxxx",
      "assistant_id": "asst_zzzzzzzzzzzzzzzzzz",
      "attachments": [],
      "completed_at": null,
      "content": [
        {
          "type": "text",
          "text": {
            "annotations": [],
            "value": "Para conectarte al WiFi de la Universidad Católica de Cuenca, necesitarás seleccionar la red WiFi disponible en tu dispositivo y luego introducir la contraseña de acceso. Si no dispones de la contraseña, te recomendaría contactar con el personal de la Dirección de Tecnologías de la Información y Comunicación a través de los canales que han facilitado, como la mesa de ayuda en el correo soporte.ucacue.edu.ec, para solicitar la información detallada sobre la conexión al WiFi institucional."
          }
        }
      ],
      "created_at": 1732043753,
      "incomplete_at": null,
      "incomplete_details": null,
      "metadata": {},
      "object": "thread.message",
      "role": "assistant",
      "run_id": "run_iiiiiiiiiiiiiiiiiiiiiiii",
      "status": null,
      "thread_id": "thread_hhhhhhhhhhhhhhhhhhh"
    },
    {
      "id": "msg_yyyyyyyyyyyyyyyyyyyyyyyy",
      "assistant_id": null,
      "attachments": [],
      "completed_at": null,
      "content": [
        {
          "type": "text",
          "text": {
            "annotations": [],
            "value": "Como me conecto al wifi"
          }
        }
      ],
      "created_at": 1732043752,
      "incomplete_at": null,
      "incomplete_details": null,
      "metadata": {},
      "object": "thread.message",
      "role": "user",
      "run_id": null,
      "status": null,
      "thread_id": "thread_hhhhhhhhhhhhhhhhhhh"
    }
  ]
}
```

