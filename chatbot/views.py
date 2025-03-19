# chatbot/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message
from products.models import Product, Category, Brand, ProductSpecification
import json
import logging
from django.conf import settings
from openai import OpenAI
from rest_framework import status, generics

from .serializers import ConversationSerializer

# Configurar logging
logger = logging.getLogger(__name__)

# Inicializar el cliente de OpenAI con la clave API configurada
client = OpenAI(api_key=settings.OPENAI_API_KEY)


class ChatbotAPIView(APIView):
    """
    API View para el chatbot que procesa mensajes a través de OpenAI ChatGPT
    """

    def post(self, request):
        """
        Procesa los mensajes del usuario y devuelve respuestas generadas por ChatGPT
        """
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

        try:
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
                'message_id': bot_message.id,
                'conversation_id': conversation.id
            })
        except Exception as e:
            logger.error(f"Error al procesar la consulta del chatbot: {str(e)}")
            return Response({
                'response': "Lo siento, estoy teniendo problemas técnicos para procesar tu consulta en este momento. ¿Puedes intentarlo de nuevo?",
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_relevant_context(self, message):
        """
        Obtiene datos relevantes de la base de datos según la consulta del usuario
        con información detallada sobre productos, categorías y marcas
        """
        context = {}
        message_lower = message.lower()

        # Obtener resumen general de inventario
        context['general_stats'] = {
            'total_products': Product.objects.count(),
            'total_categories': Category.objects.count(),
            'total_brands': Brand.objects.count()
        }

        # Detección específica de consulta sobre categorías disponibles
        category_query_keywords = ['categorías', 'categorias', 'tipos de productos', 'qué venden', 'que venden',
                                   'qué productos', 'que productos', 'secciones', 'departamentos']

        if any(keyword in message_lower for keyword in category_query_keywords):
            # Marcar específicamente que el usuario está consultando sobre categorías
            context['query_type'] = 'categories_list'
            # Asegurarnos de incluir información detallada de categorías
            context['categories_detailed'] = [
                {
                    'name': category.name,
                    'description': category.description,
                    'product_count': Product.objects.filter(category=category).count(),
                    'brands': list(set(Product.objects.filter(category=category).values_list('brand__name', flat=True)))
                }
                for category in Category.objects.all()
            ]

        # Obtener todas las categorías disponibles
        categories = Category.objects.all()
        categories_info = []
        for category in categories:
            product_count = Product.objects.filter(category=category).count()
            categories_info.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'product_count': product_count
            })
        context['categories'] = categories_info

        # Obtener todas las marcas disponibles
        brands = Brand.objects.all()
        brands_info = []
        for brand in brands:
            product_count = Product.objects.filter(brand=brand).count()
            brands_info.append({
                'id': brand.id,
                'name': brand.name,
                'description': brand.description,
                'product_count': product_count
            })
        context['brands'] = brands_info

        # Procesamiento semántico del mensaje para determinar intenciones

        # Detección de intención de búsqueda por categoría
        category_keywords = {
            'computadora': ['computadora', 'laptop', 'pc', 'ordenador', 'notebook', 'desktop', 'computadoras',
                            'laptops', 'pcs', 'ordenadores'],
            'teléfono': ['teléfono', 'celular', 'smartphone', 'móvil', 'telefono', 'movil', 'telefonos', 'celulares',
                         'smartphones'],
            'tablet': ['tablet', 'tableta', 'ipad', 'tablets', 'tabletas'],
            'accesorio': ['accesorio', 'periférico', 'periferico', 'accesorios', 'periféricos', 'perifericos', 'gadget',
                          'gadgets'],
            'audio': ['audio', 'auricular', 'altavoz', 'audifono', 'parlante', 'auriculares', 'altavoces', 'audifonos',
                      'parlantes', 'bocina', 'bocinas'],
            'gaming': ['gaming', 'juego', 'consola', 'gamer', 'videojuego', 'juegos', 'consolas', 'videojuegos']
        }

        detected_categories = []
        for category_name, keywords in category_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_categories.append(category_name)

        # Si se detecta una categoría, obtener productos relacionados
        if detected_categories:
            for category_name in detected_categories:
                category_products = Product.objects.filter(category__name__icontains=category_name)
                products_info = []

                for product in category_products:
                    # Recopilar especificaciones del producto
                    specs = {}
                    for spec in product.specifications.all():
                        specs[spec.key] = spec.value

                    # Agregar información completa del producto
                    product_info = {
                        'id': product.id,
                        'name': product.name,
                        'description': product.description,
                        'price': float(product.price),
                        'stock': product.stock,
                        'brand': product.brand.name,
                        'category': product.category.name,
                        'image_url': product.image.url if product.image and hasattr(product.image, 'url') else None,
                        'created_at': product.created_at.strftime('%Y-%m-%d'),
                        'specs': specs
                    }
                    products_info.append(product_info)

                # Agrupar por marca para análisis estadístico
                brands_in_category = {}
                for product in category_products:
                    brand_name = product.brand.name
                    if brand_name not in brands_in_category:
                        brands_in_category[brand_name] = {
                            'count': 0,
                            'min_price': float('inf'),
                            'max_price': 0,
                            'avg_price': 0,
                            'total_price': 0
                        }

                    brands_in_category[brand_name]['count'] += 1
                    brands_in_category[brand_name]['total_price'] += float(product.price)
                    brands_in_category[brand_name]['min_price'] = min(brands_in_category[brand_name]['min_price'],
                                                                      float(product.price))
                    brands_in_category[brand_name]['max_price'] = max(brands_in_category[brand_name]['max_price'],
                                                                      float(product.price))

                # Calcular precios promedio
                for brand in brands_in_category:
                    if brands_in_category[brand]['count'] > 0:
                        brands_in_category[brand]['avg_price'] = brands_in_category[brand]['total_price'] / \
                                                                 brands_in_category[brand]['count']

                # Agregar al contexto
                context[f'{category_name}_products'] = {
                    'total': category_products.count(),
                    'by_brand': brands_in_category,
                    'products': products_info
                }

        # Detección de intención de búsqueda por marca
        for brand in Brand.objects.all():
            brand_lower = brand.name.lower()
            if brand_lower in message_lower:
                brand_products = Product.objects.filter(brand__name=brand.name)
                brand_products_info = []

                for product in brand_products:
                    # Obtener todas las especificaciones
                    specs = {}
                    for spec in product.specifications.all():
                        specs[spec.key] = spec.value

                    # Agregar información completa del producto
                    product_info = {
                        'id': product.id,
                        'name': product.name,
                        'description': product.description,
                        'price': float(product.price),
                        'stock': product.stock,
                        'category': product.category.name,
                        'image_url': product.image.url if product.image and hasattr(product.image, 'url') else None,
                        'created_at': product.created_at.strftime('%Y-%m-%d'),
                        'specs': specs
                    }
                    brand_products_info.append(product_info)

                # Agrupar por categoría para análisis
                categories_in_brand = {}
                for product in brand_products:
                    category_name = product.category.name
                    if category_name not in categories_in_brand:
                        categories_in_brand[category_name] = 0
                    categories_in_brand[category_name] += 1

                # Agregar al contexto
                context['brand_info'] = {
                    'id': brand.id,
                    'name': brand.name,
                    'description': brand.description,
                    'total_products': brand_products.count(),
                    'by_category': categories_in_brand,
                    'products': brand_products_info
                }

        # Búsqueda de producto específico por nombre
        products = Product.objects.all()
        for product in products:
            product_name_lower = product.name.lower()
            # Verificar si el nombre del producto está en el mensaje
            if product_name_lower in message_lower:
                # Obtener todas las especificaciones
                specs = {}
                for spec in product.specifications.all():
                    specs[spec.key] = spec.value

                # Crear contexto detallado del producto específico
                context['specific_product'] = {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': float(product.price),
                    'stock': product.stock,
                    'brand': {
                        'id': product.brand.id,
                        'name': product.brand.name,
                        'description': product.brand.description
                    },
                    'category': {
                        'id': product.category.id,
                        'name': product.category.name,
                        'description': product.category.description
                    },
                    'image_url': product.image.url if product.image and hasattr(product.image, 'url') else None,
                    'created_at': product.created_at.strftime('%Y-%m-%d'),
                    'updated_at': product.updated_at.strftime('%Y-%m-%d'),
                    'specs': specs
                }

                # Productos similares (misma categoría)
                similar_products = Product.objects.filter(
                    category=product.category
                ).exclude(id=product.id)[:5]

                similar_products_info = []
                for similar in similar_products:
                    similar_products_info.append({
                        'id': similar.id,
                        'name': similar.name,
                        'price': float(similar.price),
                        'brand': similar.brand.name,
                    })

                context['specific_product']['similar_products'] = similar_products_info
                break  # Solo procesamos el primer producto encontrado para evitar contextos demasiado grandes

        # Búsqueda por rango de precios
        price_keywords = ['precio', 'costo', 'valor', 'cuánto cuesta', 'cuanto cuesta', 'precios', 'costos']
        if any(keyword in message_lower for keyword in price_keywords):
            # Obtener estadísticas de precios por categoría
            price_stats = {}
            for category in Category.objects.all():
                category_products = Product.objects.filter(category=category)
                if category_products.exists():
                    products_info = []
                    for product in category_products:
                        products_info.append({
                            'name': product.name,
                            'price': float(product.price),
                            'brand': product.brand.name
                        })

                    # Calcular precios min, max y promedio
                    prices = [float(p.price) for p in category_products]
                    price_stats[category.name] = {
                        'min_price': min(prices) if prices else 0,
                        'max_price': max(prices) if prices else 0,
                        'avg_price': sum(prices) / len(prices) if prices else 0,
                        'count': len(prices),
                        'products': products_info[:10]  # Limitamos a 10 productos para no sobrecargar el contexto
                    }

            context['price_info'] = price_stats

        # Búsqueda por disponibilidad o stock
        stock_keywords = ['disponible', 'stock', 'hay', 'disponibilidad', 'existencia', 'existencias', 'inventario']
        if any(keyword in message_lower for keyword in stock_keywords):
            # Obtener productos con poco stock (menos de 5 unidades)
            low_stock = Product.objects.filter(stock__lt=5)
            low_stock_info = []
            for product in low_stock:
                low_stock_info.append({
                    'id': product.id,
                    'name': product.name,
                    'stock': product.stock,
                    'price': float(product.price),
                    'brand': product.brand.name,
                    'category': product.category.name
                })

            # Obtener productos sin stock
            out_of_stock = Product.objects.filter(stock=0)
            out_of_stock_info = []
            for product in out_of_stock:
                out_of_stock_info.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'brand': product.brand.name,
                    'category': product.category.name
                })

            # Obtener productos con mayor stock
            high_stock = Product.objects.order_by('-stock')[:10]
            high_stock_info = []
            for product in high_stock:
                high_stock_info.append({
                    'id': product.id,
                    'name': product.name,
                    'stock': product.stock,
                    'price': float(product.price),
                    'brand': product.brand.name,
                    'category': product.category.name
                })

            context['stock_info'] = {
                'low_stock': low_stock_info,
                'out_of_stock': out_of_stock_info,
                'high_stock': high_stock_info
            }

        return context

    def get_openai_response(self, message, context, conversation):
        """
        Obtiene respuesta de OpenAI (ChatGPT) con el contexto de la conversación
        y datos relevantes sobre productos
        """
        try:
            # Obtener mensajes anteriores para contexto (máximo 8 mensajes para mantener el contexto limitado)
            previous_messages = conversation.messages.order_by('timestamp')[:8]

            # Configurar el sistema con instrucciones específicas para el asistente
            messages = [
                {"role": "system", "content": """Eres un asistente virtual especializado para la tienda de tecnología Buy n Large. 
                Tu objetivo es proporcionar información precisa y detallada sobre los productos, inventario y características técnicas.

                Directrices importantes:
                1. Sé amigable, profesional y conciso pero completo en tus respuestas.
                2. Usa SIEMPRE los datos del inventario proporcionados para responder con precisión.
                3. Cuando hables de precios, usa el formato de dólares (por ejemplo, $899.99).
                4. Si no tienes información sobre un producto específico, indícalo claramente.
                5. Cuando menciones especificaciones técnicas, estructúralas de manera clara y legible.
                6. Si el cliente pregunta por comparaciones entre productos, destaca diferencias clave.
                7. Personaliza tus recomendaciones basándote en las necesidades expresadas por el cliente.
                8. Responde en español, de manera profesional pero conversacional.
                9. Cuando menciones características técnicas importantes (como procesador, memoria, etc.), resáltalas.
                10. Si el cliente menciona un rango de precio, recomienda productos dentro de ese rango.

                Buy n Large es una tienda que se especializa en productos electrónicos de alta calidad, incluyendo computadoras,
                teléfonos, tablets, accesorios, equipos de audio y productos para gaming.
                """}
            ]

            # Agregar mensajes previos para mantener contexto conversacional
            for prev_msg in previous_messages:
                role = "assistant" if prev_msg.sender == "bot" else "user"
                messages.append({"role": role, "content": prev_msg.content})

            # Formatear el contexto para que sea legible para el modelo
            context_str = json.dumps(context, indent=2)

            # Agregar el mensaje actual con el contexto
            prompt = f"""
            Datos del inventario y productos de Buy n Large:
            {context_str}

            Consulta del cliente: {message}

            Proporciona una respuesta detallada y útil basándote en la información del inventario proporcionada,
            teniendo en cuenta la conversación previa con el cliente.
            """

            messages.append({"role": "user", "content": prompt})

            # Llamar a la API de OpenAI con el cliente
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # También puedes usar gpt-4 para respuestas más avanzadas
                messages=messages,
                max_tokens=500,  # Aumentado para permitir respuestas más completas
                temperature=0.7,  # Balance entre creatividad y precisión
                top_p=0.9,
                presence_penalty=0.2,  # Leve penalización para evitar repeticiones
                frequency_penalty=0.4  # Penalización para evitar repetición de frases
            )

            return response.choices[0].message.content

        except Exception as e:
            # Manejo de errores detallado
            logger.error(f"Error al comunicarse con OpenAI: {str(e)}")
            # Propagamos la excepción para manejarla en el método post
            raise


class ConversationHistoryView(generics.RetrieveAPIView):
    """
    Endpoint para obtener el historial de mensajes de una conversación
    """
    serializer_class = ConversationSerializer
    lookup_field = 'session_id'

    def get_queryset(self):
        return Conversation.objects.all().prefetch_related('messages')

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response(
                {"error": "No se encontró una conversación con este ID de sesión"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error al recuperar el historial: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )