# chatbot/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message
from .serializers import MessageSerializer
from products.models import Product, Category, Brand, ProductSpecification
import openai
from django.conf import settings
import json

openai.api_key = settings.OPENAI_API_KEY


class ChatbotAPIView(APIView):
    def post(self, request):
        message = request.data.get('message', '')
        session_id = request.data.get('session_id', '')

        if not session_id:
            return Response({"error": "Se requiere un session_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener o crear la conversación
        conversation, created = Conversation.objects.get_or_create(session_id=session_id)

        # Guardar mensaje del usuario
        user_message = Message.objects.create(
            conversation=conversation,
            content=message,
            sender='user'
        )

        # Obtener información relevante de la base de datos
        context = self.get_relevant_context(message)

        # Obtener respuesta de OpenAI
        response_text = self.get_openai_response(message, context, conversation)

        # Guardar respuesta del bot
        bot_message = Message.objects.create(
            conversation=conversation,
            content=response_text,
            sender='bot'
        )

        return Response({
            'response': response_text,
            'message_id': bot_message.id
        })

    def get_relevant_context(self, message):
        """Obtener datos relevantes de la base de datos según la consulta"""
        context = {}

        # Resumen de productos para todas las consultas
        total_products = Product.objects.count()
        context['total_products'] = total_products

        # Estadísticas de computadoras si pregunta por ellas
        if any(word in message.lower() for word in ['computadora', 'laptop', 'pc', 'ordenador']):
            computers = Product.objects.filter(category__name__icontains='Computadora')
            brands = {}
            for comp in computers:
                brands[comp.brand.name] = brands.get(comp.brand.name, 0) + 1

            computers_info = []
            for comp in computers:
                specs = {}
                for spec in comp.specifications.all():
                    specs[spec.key] = spec.value

                computers_info.append({
                    'id': comp.id,
                    'name': comp.name,
                    'brand': comp.brand.name,
                    'price': float(comp.price),
                    'stock': comp.stock,
                    'specs': specs
                })

            context['computers'] = {
                'total': computers.count(),
                'by_brand': brands,
                'products': computers_info
            }

        # Información sobre teléfonos si pregunta por ellos
        if any(word in message.lower() for word in ['teléfono', 'celular', 'smartphone', 'móvil']):
            phones = Product.objects.filter(category__name__icontains='Teléfono')
            phones_info = []

            for phone in phones:
                specs = {}
                for spec in phone.specifications.all():
                    specs[spec.key] = spec.value

                phones_info.append({
                    'id': phone.id,
                    'name': phone.name,
                    'brand': phone.brand.name,
                    'price': float(phone.price),
                    'stock': phone.stock,
                    'specs': specs
                })

            context['phones'] = {
                'total': phones.count(),
                'products': phones_info
            }

        # Buscar información sobre una marca específica
        for brand in Brand.objects.all():
            if brand.name.lower() in message.lower():
                products = Product.objects.filter(brand__name=brand.name)
                brand_products = []

                for product in products:
                    specs = {}
                    for spec in product.specifications.all():
                        specs[spec.key] = spec.value

                    brand_products.append({
                        'id': product.id,
                        'name': product.name,
                        'category': product.category.name,
                        'price': float(product.price),
                        'stock': product.stock,
                        'specs': specs
                    })

                context['brand_info'] = {
                    'name': brand.name,
                    'total_products': products.count(),
                    'products': brand_products
                }

        # Buscar información de un producto específico
        for product in Product.objects.all():
            if product.name.lower() in message.lower():
                specs = {}
                for spec in product.specifications.all():
                    specs[spec.key] = spec.value

                context['specific_product'] = {
                    'id': product.id,
                    'name': product.name,
                    'brand': product.brand.name,
                    'category': product.category.name,
                    'price': float(product.price),
                    'stock': product.stock,
                    'description': product.description,
                    'specs': specs
                }

        return context

    def get_openai_response(self, message, context, conversation):
        """Obtener respuesta de OpenAI con el contexto de la conversación"""
        try:
            # Obtener mensajes anteriores para contexto
            previous_messages = conversation.messages.order_by('timestamp')[:8]  # Últimos 8 mensajes

            messages = [
                {"role": "system", "content": """Eres un asistente virtual para la tienda de tecnología Buy n Large. 
                Tu objetivo es proporcionar información precisa sobre los productos, inventario y características. 
                Sé amigable, profesional y conciso. Usa los datos del inventario proporcionados para responder con precisión.
                Si te preguntan sobre un producto específico del que no tienes información en el contexto, indica que buscarás
                la información y pregunta si hay algo más en lo que puedas ayudar mientras tanto.
                Si mencionan una marca o categoría, proporciona detalles sobre los productos disponibles de esa marca.
                Siempre que menciones precios, usa formato de dólares (por ejemplo, $899.99).
                """}
            ]

            # Agregar mensajes previos para mantener contexto conversacional
            for prev_msg in previous_messages:
                role = "assistant" if prev_msg.sender == "bot" else "user"
                messages.append({"role": role, "content": prev_msg.content})

            # Formatear el contexto para que sea legible
            context_str = json.dumps(context, indent=2)

            # Agregar el mensaje actual con el contexto
            prompt = f"""
            Datos del inventario:
            {context_str}

            Pregunta del cliente: {message}

            Responde de manera amigable y profesional basándote en los datos proporcionados.
            """

            messages.append({"role": "user", "content": prompt})

            # Llamar a la API de OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )

            return response.choices[0].message['content']

        except Exception as e:
            # Manejo de errores
            print(f"Error al comunicarse con OpenAI: {str(e)}")
            return "Lo siento, estoy teniendo problemas técnicos para procesar tu consulta en este momento. ¿Puedes intentarlo de nuevo?"