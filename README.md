# Buy n Large Chatbot

## Descripción del Proyecto
Este proyecto implementa un chatbot inteligente para la tienda virtual de tecnología Buy n Large. El chatbot está diseñado para proporcionar información detallada sobre productos, inventario y asistencia a los clientes utilizando la API de OpenAI (ChatGPT).

## Características Principales
- Integración con OpenAI para generar respuestas naturales y contextualizadas
- Análisis semántico de las consultas de los usuarios
- Búsqueda inteligente de productos por categorías, marcas y especificaciones
- Información detallada sobre precios, stock y características técnicas
- Historial de conversaciones para mantener contexto
- API RESTful para integración con frontend

## Estructura del Proyecto

### Aplicaciones
- **chatbot**: Gestiona la lógica del chatbot y las conversaciones
- **products**: Administra el catálogo de productos, categorías y marcas

### Principales Archivos

#### Chatbot
- `chatbot/views.py`: Contiene la lógica principal del chatbot y el procesamiento de mensajes
- `chatbot/models.py`: Define los modelos para conversaciones y mensajes
- `chatbot/serializers.py`: Serializadores para la API REST
- `chatbot/urls.py`: Define las rutas de la API del chatbot

#### Productos
- `products/models.py`: Define los modelos para productos, categorías, marcas y especificaciones
- `products/views.py`: Vistas API para el catálogo de productos
- `products/serializers.py`: Serializadores para la API de productos

## Instalación

### Requisitos Previos
- Python 3.9+
- Django 5.1+
- Cuenta de OpenAI con API key

### Pasos de Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/jonatanmedina12/Project-Django-BuyLarge-ChatBot.git
cd buynlarge-chatbot
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
# En Windows
set SECRET_KEY=tu_clave_secreta
set OPENAI_API_KEY=tu_clave_api_de_openai
set DEBUG=True
```

5. Realizar migraciones:
```bash
python manage.py migrate
```

6. Cargar datos de ejemplo (opcional):
```bash
python manage.py loaddata sample_data
```

7. Iniciar el servidor:
```bash
python manage.py runserver
```

## Uso de la API

### Endpoint del Chatbot
```
POST /api/chatbot/chat/
```
Parámetros:
```json
{
  "message": "¿Qué laptops tienen en stock?",
  "session_id": "unique_session_identifier"
}
```

### Consultar Historial de Conversación
```
GET /api/chatbot/conversations/{session_id}/
```

## Funcionamiento del Chatbot

El chatbot utiliza un proceso de tres pasos para generar respuestas precisas:

1. **Análisis de Consulta**: Identifica la intención del usuario y extrae palabras clave relacionadas con productos, categorías, marcas, precios, etc.

2. **Recopilación de Contexto**: Obtiene información relevante de la base de datos según la consulta, incluyendo:
   - Productos específicos mencionados
   - Categorías de productos
   - Marcas
   - Estadísticas de precios
   - Información de stock

3. **Generación de Respuesta**: Combina el contexto de la conversación con los datos relevantes y utiliza la API de OpenAI para generar una respuesta natural y precisa.

## Personalización y Extensión

### Añadir Nuevas Categorías
Para añadir nuevas categorías de productos, actualiza el diccionario `category_keywords` en el método `get_relevant_context` del archivo `chatbot/views.py`.

### Modificar el Comportamiento del Chatbot
Las instrucciones específicas para el comportamiento del chatbot se encuentran en el método `get_openai_response`. Puedes ajustar el prompt del sistema para cambiar el estilo y las capacidades del chatbot.
