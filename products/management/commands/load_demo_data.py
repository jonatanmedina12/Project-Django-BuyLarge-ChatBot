# products/management/commands/load_demo_data.py
from django.core.management.base import BaseCommand
from products.models import Category, Brand, Product, ProductSpecification
from django.utils import timezone
from django.core.files.base import ContentFile
import random
import requests
import os
import tempfile
from PIL import Image
from io import BytesIO


class Command(BaseCommand):
    help = 'Carga datos de demostración extensos para la tienda incluyendo imágenes'

    # URLs de imágenes de muestra para cada categoría
    SAMPLE_IMAGES = {
        "Computadoras": [
            "https://fakeimg.pl/600x400/007bff/ffffff/?text=Laptop&font=lobster",
            "https://fakeimg.pl/600x400/0044cc/ffffff/?text=Notebook&font=lobster",
            "https://fakeimg.pl/600x400/0066ff/ffffff/?text=Desktop&font=lobster",
        ],
        "Teléfonos": [
            "https://fakeimg.pl/600x400/fd7e14/ffffff/?text=Smartphone&font=lobster",
            "https://fakeimg.pl/600x400/cc5500/ffffff/?text=Celular&font=lobster",
            "https://fakeimg.pl/600x400/ff9900/ffffff/?text=Mobile&font=lobster",
        ],
        "Tablets": [
            "https://fakeimg.pl/600x400/28a745/ffffff/?text=Tablet&font=lobster",
            "https://fakeimg.pl/600x400/198754/ffffff/?text=iPad&font=lobster",
        ],
        "Accesorios": [
            "https://fakeimg.pl/600x400/dc3545/ffffff/?text=Accessory&font=lobster",
            "https://fakeimg.pl/600x400/b02a37/ffffff/?text=Gadget&font=lobster",
        ],
        "Audio": [
            "https://fakeimg.pl/600x400/6610f2/ffffff/?text=Headphones&font=lobster",
            "https://fakeimg.pl/600x400/520dc2/ffffff/?text=Speaker&font=lobster",
        ],
        "Gaming": [
            "https://fakeimg.pl/600x400/d63384/ffffff/?text=Console&font=lobster",
            "https://fakeimg.pl/600x400/ab296a/ffffff/?text=GamePad&font=lobster",
        ],
    }

    def download_image(self, url, category_name):
        """Descarga una imagen desde la URL proporcionada"""
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))

                # Convertir la imagen a JPEG si no lo es
                if img.format != 'JPEG':
                    img = img.convert('RGB')

                # Guardar la imagen en un archivo temporal
                temp_file = BytesIO()
                img.save(temp_file, format='JPEG')
                temp_file.seek(0)

                # Generar un nombre de archivo aleatorio
                filename = f"{category_name.lower().replace(' ', '_')}_{random.randint(1000, 9999)}.jpg"

                return ContentFile(temp_file.read(), name=filename)
            else:
                self.stdout.write(self.style.WARNING(f"No se pudo descargar la imagen. Código: {response.status_code}"))
                return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al descargar imagen: {str(e)}"))
            return None

    def _create_product(self, name, description, price, stock, category, brand, image_url=None):
        """Método auxiliar para crear productos con imagen"""
        try:
            # Crear el producto primero
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category=category,
                brand=brand
            )

            # Si se proporciona URL de imagen, intentar descargarla
            if image_url:
                image_content = self.download_image(image_url, category.name)
                if image_content:
                    product.image = image_content
                    product.save()
                    self.stdout.write(f"Imagen añadida para {name}")
                else:
                    self.stdout.write(self.style.WARNING(f"No se pudo añadir imagen para {name}"))

            return product
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al crear producto {name}: {str(e)}"))
            return None

    def _create_specs(self, product, specs_dict):
        """Método auxiliar para crear especificaciones de producto"""
        if not product:
            self.stdout.write(self.style.WARNING(f"No se pueden crear especificaciones para un producto nulo"))
            return

        try:
            for key, value in specs_dict.items():
                ProductSpecification.objects.create(
                    product=product,
                    key=key,
                    value=value
                )
            self.stdout.write(f"Creadas {len(specs_dict)} especificaciones para {product.name}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al crear especificaciones para {product.name}: {str(e)}"))

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando datos de demostración extensos con imágenes...')

        # Limpiar datos existentes
        self.stdout.write('Eliminando datos anteriores...')
        ProductSpecification.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()

        # Crear categorías
        self.stdout.write('Creando categorías...')
        cat_computers = Category.objects.create(
            name="Computadoras",
            description="Laptops y desktops para todas tus necesidades de computación, desde modelos básicos hasta equipos de alto rendimiento. Incluye ordenadores portátiles, desktops, all-in-one y estaciones de trabajo."
        )
        cat_phones = Category.objects.create(
            name="Teléfonos",
            description="Smartphones y celulares de última generación con las mejores cámaras, procesadores y pantallas. Dispositivos inteligentes que te mantienen conectado y productivo."
        )
        cat_tablets = Category.objects.create(
            name="Tablets",
            description="Tablets y e-readers para productividad y entretenimiento. Perfectos para leer, navegar por internet, ver videos y realizar tareas sencillas en movimiento."
        )
        cat_accessories = Category.objects.create(
            name="Accesorios",
            description="Periféricos, fundas, cargadores y más para tus dispositivos. Encuentra todo lo que necesitas para complementar y proteger tus equipos tecnológicos."
        )
        cat_audio = Category.objects.create(
            name="Audio",
            description="Auriculares, altavoces y equipos de sonido con la mejor calidad de audio y tecnologías inalámbricas. Experimenta un sonido envolvente para tus películas, música y juegos."
        )
        cat_gaming = Category.objects.create(
            name="Gaming",
            description="Consolas, juegos y accesorios para gamers. Todo lo que necesitas para disfrutar de tus videojuegos favoritos con el mejor rendimiento y comodidad."
        )

        # Crear marcas
        self.stdout.write('Creando marcas...')
        brand_hp = Brand.objects.create(
            name="HP",
            description="Hewlett-Packard, empresa multinacional estadounidense fundada en 1939, enfocada en computadoras, impresoras y soluciones tecnológicas para empresas y consumidores."
        )
        brand_dell = Brand.objects.create(
            name="Dell",
            description="Dell Technologies, fundada en 1984, especializada en computadoras personales, servidores, almacenamiento de datos y soluciones empresariales personalizadas."
        )
        brand_apple = Brand.objects.create(
            name="Apple",
            description="Apple Inc., fundada en 1976, creadora del Mac, iPhone, iPad y otros productos premium conocidos por su diseño, innovación y ecosistema integrado."
        )
        brand_samsung = Brand.objects.create(
            name="Samsung",
            description="Samsung Electronics, división de tecnología del grupo surcoreano Samsung, líder mundial en teléfonos móviles, televisores, semiconductores y electrodomésticos."
        )
        brand_lenovo = Brand.objects.create(
            name="Lenovo",
            description="Lenovo Group, multinacional china que desarrolla, fabrica y vende computadoras personales, tablets, smartphones, servidores y soluciones tecnológicas empresariales."
        )
        brand_asus = Brand.objects.create(
            name="Asus",
            description="Asus, empresa taiwanesa fundada en 1989, especializada en computadoras, componentes, periféricos y soluciones para gaming con innovación y calidad."
        )
        brand_acer = Brand.objects.create(
            name="Acer",
            description="Acer Inc., fundada en 1976 en Taiwán, fabricante de computadoras portátiles, de escritorio, tablets, servidores, almacenamiento y dispositivos móviles accesibles."
        )
        brand_xiaomi = Brand.objects.create(
            name="Xiaomi",
            description="Xiaomi, empresa china fundada en 2010, conocida por sus smartphones, dispositivos inteligentes para el hogar y productos electrónicos con buena relación calidad-precio."
        )
        brand_google = Brand.objects.create(
            name="Google",
            description="Google LLC, fundada en 1998, además de su motor de búsqueda, desarrolla productos como Pixel, Nest, Chromebooks y otros dispositivos que integran su ecosistema de servicios."
        )
        brand_sony = Brand.objects.create(
            name="Sony",
            description="Sony Corporation, compañía japonesa fundada en 1946, dedicada a la electrónica de consumo, videojuegos, entretenimiento y servicios financieros con productos premium."
        )
        brand_microsoft = Brand.objects.create(
            name="Microsoft",
            description="Microsoft Corporation, fundada en 1975, empresa de software y hardware conocida por Windows, Office, Surface, Xbox y soluciones empresariales en la nube."
        )
        brand_logitech = Brand.objects.create(
            name="Logitech",
            description="Logitech, empresa suiza especializada en periféricos y accesorios para computadoras como teclados, ratones, webcams, altavoces y productos para videoconferencias."
        )
        brand_jbl = Brand.objects.create(
            name="JBL",
            description="JBL, marca estadounidense de audio fundada en 1946, parte de Harman International (subsidiaria de Samsung), especializada en altavoces, auriculares y sistemas de sonido de alta calidad."
        )

        # Crear productos - HP
        self.stdout.write('Creando productos HP...')
        hp_laptop1 = self._create_product(
            name="HP Pavilion 15",
            description="Laptop potente para trabajo y estudios con procesador i5, ideal para multitarea y aplicaciones de productividad. Diseño elegante con chasis de aluminio, pantalla Full HD IPS de colores vibrantes y audio mejorado por B&O.",
            price=899.99,
            stock=15,
            category=cat_computers,
            brand=brand_hp,
            image_url=random.choice(self.SAMPLE_IMAGES["Computadoras"])
        )

        self._create_specs(hp_laptop1, {
            "Processor": "Intel Core i5-11300H",
            "RAM": "8GB DDR4",
            "Storage": "512GB SSD NVMe",
            "Screen": "15.6 pulgadas FHD IPS",
            "Graphics": "Intel Iris Xe",
            "OS": "Windows 11 Home",
            "Battery": "6 horas",
            "Weight": "1.8 kg",
            "Color": "Plata",
            "Connectivity": "Wi-Fi 6, Bluetooth 5.0",
            "Ports": "2x USB 3.1, 1x USB-C, HDMI, SD Card Reader",
            "Webcam": "HD 720p",
            "Audio": "Bang & Olufsen dual speakers"
        })

        hp_laptop2 = self._create_product(
            name="HP Envy 13",
            description="Laptop premium ultradelgada con pantalla táctil, perfecta para profesionales que necesitan movilidad sin comprometer el rendimiento. Incluye lector de huellas digitales, chasis de aluminio premium, retroiluminación de teclado y cancelación de ruido con IA para videoconferencias.",
            price=1099.99,
            stock=8,
            category=cat_computers,
            brand=brand_hp,
            image_url=random.choice(self.SAMPLE_IMAGES["Computadoras"])
        )

        self._create_specs(hp_laptop2, {
            "Processor": "Intel Core i7-1165G7",
            "RAM": "16GB DDR4",
            "Storage": "1TB SSD NVMe",
            "Screen": "13.3 pulgadas táctil FHD OLED",
            "Graphics": "Intel Iris Xe",
            "OS": "Windows 11 Pro",
            "Battery": "10 horas",
            "Weight": "1.3 kg",
            "Color": "Negro",
            "Connectivity": "Wi-Fi 6, Bluetooth 5.2",
            "Ports": "2x Thunderbolt 4, USB-A, microSD",
            "Security": "Lector de huellas, Cámara IR",
            "Keyboard": "Retroiluminado",
            "Audio": "Bang & Olufsen quad speakers"
        })

        hp_desktop = self._create_product(
            name="HP Pavilion Desktop",
            description="Desktop completo para hogar u oficina con buen rendimiento para tareas cotidianas y espacio de almacenamiento amplio. Diseño compacto que ahorra espacio, excelente para estudios, oficina en casa o entretenimiento multimedia básico.",
            price=649.99,
            stock=10,
            category=cat_computers,
            brand=brand_hp,
            image_url=random.choice(self.SAMPLE_IMAGES["Computadoras"])
        )

        self._create_specs(hp_desktop, {
            "Processor": "Intel Core i5-10400",
            "RAM": "12GB DDR4",
            "Storage": "1TB HDD + 256GB SSD",
            "Graphics": "Intel UHD Graphics 630",
            "OS": "Windows 11 Home",
            "Ports": "USB 3.1, HDMI, DisplayPort",
            "Connectivity": "Wi-Fi 5, Bluetooth 5.0, Ethernet Gigabit",
            "Form Factor": "Tower",
            "Dimensions": "17 x 27.7 x 33.8 cm",
            "Weight": "5.3 kg",
            "Optical Drive": "DVD-RW",
            "Included Accessories": "Teclado y mouse USB"
        })

        # Crear productos - Dell
        self.stdout.write('Creando productos Dell...')
        dell_laptop1 = self._create_product(
            name="Dell Inspiron 15",
            description="Laptop versátil con buen rendimiento y diseño elegante, perfecta para estudiantes y uso cotidiano. Ofrece una experiencia multimedia inmersiva gracias a su pantalla de bordes delgados y audio mejorado, ideal para clases virtuales y entretenimiento.",
            price=749.99,
            stock=12,
            category=cat_computers,
            brand=brand_dell,
            image_url=random.choice(self.SAMPLE_IMAGES["Computadoras"])
        )

        self._create_specs(dell_laptop1, {
            "Processor": "Intel Core i3-1115G4",
            "RAM": "8GB DDR4",
            "Storage": "256GB SSD",
            "Screen": "15.6 pulgadas FHD",
            "Graphics": "Intel UHD Graphics",
            "OS": "Windows 11 Home",
            "Battery": "5 horas",
            "Weight": "1.9 kg",
            "Color": "Plata",
            "Connectivity": "Wi-Fi 5, Bluetooth 4.2",
            "Ports": "2x USB 3.1, 1x USB 2.0, HDMI, SD Card",
            "Webcam": "HD",
            "Audio": "Stereo speakers with Waves MaxxAudio Pro"
        })

        dell_laptop2 = self._create_product(
            name="Dell XPS 13",
            description="Laptop ultradelgada premium con pantalla InfinityEdge. Rendimiento excepcional en un formato compacto. Construida con materiales premium como fibra de carbono y aluminio, con tecnologías avanzadas de refrigeración para mantener alto rendimiento durante periodos prolongados.",
            price=1299.99,
            stock=5,
            category=cat_computers,
            brand=brand_dell,
            image_url=random.choice(self.SAMPLE_IMAGES["Computadoras"])
        )

        self._create_specs(dell_laptop2, {
            "Processor": "Intel Core i7-1185G7",
            "RAM": "16GB LPDDR4x",
            "Storage": "512GB SSD NVMe",
            "Screen": "13.4 pulgadas 4K InfinityEdge",
            "Graphics": "Intel Iris Xe",
            "OS": "Windows 11 Pro",
            "Battery": "12 horas",
            "Weight": "1.2 kg",
            "Color": "Plata y Negro",
            "Connectivity": "Wi-Fi 6, Bluetooth 5.1",
            "Ports": "2x Thunderbolt 4, microSD",
            "Materials": "Aluminio y fibra de carbono",
            "Security": "Lector de huellas en botón de encendido",
            "Webcam": "HD + IR para Windows Hello"
        })

        # Crear productos - Apple
        self.stdout.write('Creando productos Apple...')
        macbook_air = self._create_product(
            name="MacBook Air",
            description="Laptop ultraligera con chip M1 y gran duración de batería. Perfecta para usuarios que valoran la portabilidad y el rendimiento. Diseño icónico en cuña, silenciosa gracias a su diseño sin ventilador y con Magic Keyboard para una experiencia de escritura cómoda y precisa.",
            price=1099.99,
            stock=7,
            category=cat_computers,
            brand=brand_apple,
            image_url=random.choice(self.SAMPLE_IMAGES["Computadoras"])
        )

        self._create_specs(macbook_air, {
            "Processor": "Apple M1",
            "RAM": "8GB unificada",
            "Storage": "256GB SSD",
            "Screen": "13.3 pulgadas Retina",
            "Graphics": "GPU 7 núcleos",
            "OS": "macOS Monterey",
            "Battery": "18 horas",
            "Weight": "1.29 kg",
            "Color": "Space Gray",
            "Connectivity": "Wi-Fi 6, Bluetooth 5.0",
            "Ports": "2x Thunderbolt / USB 4",
            "Keyboard": "Magic Keyboard retroiluminado",
            "Touch ID": "Sí",
            "Camera": "FaceTime HD 720p con ISP"
        })

        macbook_pro = self._create_product(
            name="MacBook Pro 14",
            description="Potente MacBook Pro con chip M1 Pro, pantalla Liquid Retina XDR y MagSafe. Ideal para profesionales creativos. Ofrece un rendimiento excepcional para edición de fotos, videos, desarrollo de software y aplicaciones exigentes con una eficiencia energética superior.",
            price=1999.99,
            stock=4,
            category=cat_computers,
            brand=brand_apple,
            image_url=random.choice(self.SAMPLE_IMAGES["Computadoras"])
        )

        self._create_specs(macbook_pro, {
            "Processor": "Apple M1 Pro",
            "RAM": "16GB unificada",
            "Storage": "512GB SSD",
            "Screen": "14 pulgadas Liquid Retina XDR",
            "Graphics": "GPU 16 núcleos",
            "OS": "macOS Monterey",
            "Battery": "17 horas",
            "Weight": "1.6 kg",
            "Color": "Silver",
            "Connectivity": "Wi-Fi 6, Bluetooth 5.0",
            "Ports": "3x Thunderbolt 4, HDMI, SD card, MagSafe 3",
            "Keyboard": "Magic Keyboard retroiluminado",
            "Audio": "Sistema de 6 altavoces con woofers canceladores de fuerza",
            "Touch ID": "Sí",
            "Display Features": "ProMotion 120Hz, 1000 nits sostenidos"
        })

        # Teléfonos - Samsung
        self.stdout.write('Creando teléfonos Samsung...')
        samsung_phone1 = self._create_product(
            name="Samsung Galaxy S22",
            description="Smartphone de alta gama con excelente cámara y rendimiento. Pantalla AMOLED de alta resolución y fluidez. Construcción en aluminio y vidrio resistente Gorilla Glass Victus+, con certificación IP68 para resistencia al agua y polvo.",
            price=799.99,
            stock=20,
            category=cat_phones,
            brand=brand_samsung,
            image_url=random.choice(self.SAMPLE_IMAGES["Teléfonos"])
        )

        self._create_specs(samsung_phone1, {
            "Processor": "Snapdragon 8 Gen 1",
            "RAM": "8GB",
            "Storage": "128GB",
            "Screen": "6.1 pulgadas AMOLED 120Hz",
            "Camera": "50MP + 12MP + 10MP",
            "Frontal Camera": "10MP",
            "Battery": "3700 mAh",
            "OS": "Android 12",
            "IP Rating": "IP68",
            "Color": "Phantom Black",
            "Charging": "25W wired, 15W wireless",
            "Biometrics": "Ultrasonic fingerprint, Face recognition",
            "Connectivity": "5G, Wi-Fi 6, Bluetooth 5.2, NFC",
            "Water Resistance": "1.5 metros hasta 30 minutos"
        })

        # Agregar otros teléfonos y productos según sea necesario...

        # Tabletas - Apple
        ipad_pro = self._create_product(
            name="iPad Pro 12.9",
            description="iPad de gama alta con chip M2, pantalla Liquid Retina XDR y soporte para Apple Pencil. Ideal para profesionales creativos.",
            price=1099.99,
            stock=6,
            category=cat_tablets,
            brand=brand_apple,
            image_url=random.choice(self.SAMPLE_IMAGES["Tablets"])
        )

        self._create_specs(ipad_pro, {
            "Processor": "Apple M2",
            "RAM": "8GB",
            "Storage": "256GB",
            "Screen": "12.9 pulgadas Liquid Retina XDR",
            "Camera": "12MP + 10MP",
            "Frontal Camera": "12MP Ultra Wide",
            "Battery": "10 horas",
            "OS": "iPadOS 16",
            "Special Feature": "Compatible con Apple Pencil 2",
            "Color": "Space Gray"
        })

        # Accesorios - Apple Pencil
        apple_pencil = self._create_product(
            name="Apple Pencil 2",
            description="Lápiz digital de precisión para iPad. Ideal para notas, dibujo y diseño.",
            price=129.99,
            stock=20,
            category=cat_accessories,
            brand=brand_apple,
            image_url=random.choice(self.SAMPLE_IMAGES["Accesorios"])
        )

        self._create_specs(apple_pencil, {
            "Compatibility": "iPad Pro, iPad Air",
            "Battery": "12 horas",
            "Charging": "Magnético",
            "Pressure Sensitivity": "Sí",
            "Special Feature": "Doble toque para cambiar herramientas",
            "Color": "Blanco"
        })

        self.stdout.write(
            self.style.SUCCESS(f'Datos de demostración completos: {Product.objects.count()} productos creados'))