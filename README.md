# TicAI Support  
**La herramienta de soporte académico y técnico impulsada por inteligencia artificial para la Universidad Católica de Cuenca.**

## Repositorios Necesarios
#### **Webhook**
Repositorio: [Webhook](https://github.com/PePeWee07/TicAI-Support.git)
#### **WhatsAppApiCloud_ApiRest**
Repositorio: [Back-end](https://github.com/PePeWee07/WhatsAppApiCloud_ApiRest.git)
#### **ERP Simulator**
Repositorio: [ERP-Simulator](https://github.com/PePeWee07/ERP_simulator.git)

## Descripción  
**TicAI Support** es una solución innovadora que utiliza tecnología avanzada de inteligencia artificial para mejorar el soporte académico y técnico dentro de la Universidad Católica de Cuenca. Diseñada para estudiantes, docentes y personal administrativo, la plataforma facilita la resolución de consultas relacionadas con servicios TIC, asistencia académica y procesos administrativos, optimizando tiempos y mejorando la experiencia de los usuarios.

**Propósito:** Automatizar y facilitar el acceso a información clave y soporte relacionado con la Dirección de Tecnologías de la Información y Comunicación (TICS), brindando respuestas inmediatas y personalizadas.

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


## Cómo usar:
1. **Asegúrate de editar el archivo `.env` en la raíz del proyecto:**

```properties
GPT_TICS_KEY="OPENAI_API_KEY_MODEL"
MODERATION_KEY="OPENAI_API_KEY_MODERATION"
ASSISTANT_ID="ASSISTANT_ID"
MODEL_MODERATION="omni-moderation-latest"
ENCODING_BASE="cl100k_base"
API_KEY="MY_API_KEY_AUTH"
```

2. **Construir y ejecutar con Docker Compose:**

```sh
docker-compose up -d
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
            "value": "Texto de respuesta"
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
            "value": "Texto de pregunta"
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

