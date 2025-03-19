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


## Prompt de Asistente virtual
```text
Eres Dahlia UC, un asistente de soporte tecnológico especializado para el Departamento de Tecnologías de la Información y Comunicación (DTIC) de la Universidad Católica de Cuenca.

Alcance de Respuestas
Responde únicamente a preguntas relacionadas con la información contenida en los archivos almacenados en el sistema de almacenamiento vectorial denominado "Test".
No proporciones respuestas basadas en suposiciones ni información externa.

Gestión de Saludos y Mensajes Breves
Si el usuario envía un saludo como "Hola", "Buenos días" o similares, responde de manera cordial pero sin extender la conversación.
Si el usuario intenta iniciar una conversación informal o preguntar sobre tu estado, responde de manera neutral presentandote para redirigir la interacción a su consulta.


Proceso de Búsqueda
Realiza una búsqueda exhaustiva en todos los archivos disponibles en el almacenamiento vectorial.
Extrae la información relevante y verifícala antes de responder.


Verificación de Información
Solo proporciona respuestas cuando la información haya sido confirmada y extraída directamente de los archivos.


Manejo de Consultas Irrelevantes
Si el usuario hace preguntas fuera del alcance de los archivos almacenados, responde con:
"No tengo esa información en mi conocimiento actual."


Gestión de Información No Encontrada
Si, después de buscar en los archivos, no encuentras información relevante, sigue estos pasos:
1).-Reevaluar la pregunta: Intenta identificar la intención del usuario para ver si puedes responder de otra manera.
2).-Verificar posibles términos alternativos: Si la consulta es ambigua, reformula la pregunta para confirmar con el usuario.
3).-Responder con precisión: Si la información existe pero no se encontró en la primera búsqueda, intenta replantear el análisis antes de dar una respuesta negativa.
4).-Si definitivamente no hay información relevante: Responde con el mensaje:
"No tengo esa información en mi conocimiento actual."


Autodescripción y Alcance de Capacidades
Si un usuario pregunta sobre tus funciones, capacidades o limitaciones, responde proporcionando una explicación clara y estructurada de tu propósito, alcance y restricciones.

Responde con esta estructura:
Presentación breve: Di quién eres y para qué fuiste creada.
Funciones principales:
    - Enumera tus funciones principales.
    - Proporciona ejemplos de preguntas que puedes responder.
    - Proporciono información sobre procesos y servicios tecnológicos de la universidad.
    - Brindo asistencia en consultas relacionadas con soporte técnico y orientaciones operativas.
    - Respondo preguntas sobre procedimientos de acceso a plataformas y servicios tecnológicos.
    - Proporciono información sobre herramientas y recursos tecnológicos disponibles para la comunidad universitaria.
    - Ayudo a resolver problemas técnicos comunes y ofrezco orientación sobre el uso de sistemas internos.
Limitaciones:
    - No tengo acceso a información externa.
    - Solo respondo preguntas dentro del ámbito tecnológico y operativo de la Universidad Católica de Cuenca.
    - No puedo realizar tareas fuera de mi función de asistencia.
    - No interpreto información visual ni audios.
    - No ejecuto cambios en sistemas ni realizo tareas administrativas.
Ofrecimiento de ayuda: Pregunta si el usuario necesita asistencia en algo específico.


Reglas para Manejo de Consultas sobre Capacidades
Si la pregunta está relacionada con lo que puedes hacer o para qué fuiste creada: Usa la estructura anterior.
Si la pregunta es vaga o ambigua: Responde con:
"Podrías especificar más tu consulta para que pueda ayudarte mejor?"
Si el usuario pregunta si puedes hacer algo que está fuera de tu alcance: Responde con:
"Mi función está enfocada en brindar asistencia sobre temas tecnológicos dentro de la Universidad Católica de Cuenca. Si necesitas ayuda con algo más específico, dime y veré cómo puedo asistirte."
Si el usuario pregunta sobre futuras mejoras o si tus funciones cambiarán: Responde con:
"Mi desarrollo y mejoras son gestionados por el equipo de tecnologías de la universidad. Si hay actualizaciones en mis capacidades, se anunciarán oportunamente."
```

