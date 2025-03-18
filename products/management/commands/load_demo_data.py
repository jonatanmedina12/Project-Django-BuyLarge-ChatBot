# products/management/commands/load_demo_data.py
from django.core.management.base import BaseCommand
from products.models import Category, Brand, Product, ProductSpecification


class Command(BaseCommand):
    help = 'Carga datos de demostración para la tienda'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando datos de demostración...')

        # Limpiar datos existentes
        ProductSpecification.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()

        # Crear categorías
        cat_computers = Category.objects.create(name="Computadoras", description="Laptops y desktops")
        cat_phones = Category.objects.create(name="Teléfonos", description="Smartphones y celulares")
        cat_tablets = Category.objects.create(name="Tablets", description="Tablets y e-readers")

        # Crear marcas
        brand_hp = Brand.objects.create(name="HP", description="Hewlett-Packard")
        brand_dell = Brand.objects.create(name="Dell", description="Dell Technologies")
        brand_apple = Brand.objects.create(name="Apple", description="Apple Inc.")
        brand_samsung = Brand.objects.create(name="Samsung", description="Samsung Electronics")

        # Crear productos - HP
        hp_laptop = Product.objects.create(
            name="HP Pavilion 15",
            description="Laptop potente para trabajo y estudios con procesador i5",
            price=899.99,
            stock=15,
            category=cat_computers,
            brand=brand_hp
        )

        ProductSpecification.objects.create(product=hp_laptop, key="Processor", value="Intel Core i5")
        ProductSpecification.objects.create(product=hp_laptop, key="RAM", value="8GB")
        ProductSpecification.objects.create(product=hp_laptop, key="Storage", value="512GB SSD")
        ProductSpecification.objects.create(product=hp_laptop, key="Screen", value="15.6 pulgadas")

        hp_laptop2 = Product.objects.create(
            name="HP Envy 13",
            description="Laptop premium ultradelgada con pantalla táctil",
            price=1099.99,
            stock=8,
            category=cat_computers,
            brand=brand_hp
        )

        ProductSpecification.objects.create(product=hp_laptop2, key="Processor", value="Intel Core i7")
        ProductSpecification.objects.create(product=hp_laptop2, key="RAM", value="16GB")
        ProductSpecification.objects.create(product=hp_laptop2, key="Storage", value="1TB SSD")
        ProductSpecification.objects.create(product=hp_laptop2, key="Screen", value="13.3 pulgadas táctil")

        # Crear productos - Dell
        dell_laptop = Product.objects.create(
            name="Dell Inspiron 15",
            description="Laptop versátil con buen rendimiento y diseño elegante",
            price=749.99,
            stock=8,
            category=cat_computers,
            brand=brand_dell
        )

        ProductSpecification.objects.create(product=dell_laptop, key="Processor", value="Intel Core i3")
        ProductSpecification.objects.create(product=dell_laptop, key="RAM", value="8GB")
        ProductSpecification.objects.create(product=dell_laptop, key="Storage", value="256GB SSD")
        ProductSpecification.objects.create(product=dell_laptop, key="Screen", value="15.6 pulgadas")

        # Crear productos - Apple
        macbook = Product.objects.create(
            name="MacBook Air",
            description="Laptop ultraligera con chip M1 y gran duración de batería",
            price=1099.99,
            stock=5,
            category=cat_computers,
            brand=brand_apple
        )

        ProductSpecification.objects.create(product=macbook, key="Processor", value="Apple M1")
        ProductSpecification.objects.create(product=macbook, key="RAM", value="8GB")
        ProductSpecification.objects.create(product=macbook, key="Storage", value="256GB SSD")
        ProductSpecification.objects.create(product=macbook, key="Screen", value="13.3 pulgadas")

        # Teléfonos - Samsung
        samsung_phone = Product.objects.create(
            name="Samsung Galaxy S22",
            description="Smartphone de alta gama con excelente cámara",
            price=799.99,
            stock=20,
            category=cat_phones,
            brand=brand_samsung
        )

        ProductSpecification.objects.create(product=samsung_phone, key="Processor", value="Snapdragon 8 Gen 1")
        ProductSpecification.objects.create(product=samsung_phone, key="RAM", value="8GB")
        ProductSpecification.objects.create(product=samsung_phone, key="Storage", value="128GB")
        ProductSpecification.objects.create(product=samsung_phone, key="Screen", value="6.1 pulgadas AMOLED")
        ProductSpecification.objects.create(product=samsung_phone, key="Camera", value="50MP + 12MP + 10MP")

        # Teléfonos - Apple
        iphone = Product.objects.create(
            name="iPhone 14",
            description="El último iPhone con chip A16 Bionic",
            price=899.99,
            stock=12,
            category=cat_phones,
            brand=brand_apple
        )

        ProductSpecification.objects.create(product=iphone, key="Processor", value="A16 Bionic")
        ProductSpecification.objects.create(product=iphone, key="RAM", value="6GB")
        ProductSpecification.objects.create(product=iphone, key="Storage", value="128GB")
        ProductSpecification.objects.create(product=iphone, key="Screen", value="6.1 pulgadas Super Retina XDR")
        ProductSpecification.objects.create(product=iphone, key="Camera", value="48MP + 12MP")

        # Tablets - Samsung
        samsung_tablet = Product.objects.create(
            name="Samsung Galaxy Tab S8",
            description="Tablet potente con S Pen incluido",
            price=649.99,
            stock=7,
            category=cat_tablets,
            brand=brand_samsung
        )

        ProductSpecification.objects.create(product=samsung_tablet, key="Processor", value="Snapdragon 8 Gen 1")
        ProductSpecification.objects.create(product=samsung_tablet, key="RAM", value="8GB")
        ProductSpecification.objects.create(product=samsung_tablet, key="Storage", value="128GB")
        ProductSpecification.objects.create(product=samsung_tablet, key="Screen", value="11 pulgadas AMOLED")

        self.stdout.write(self.style.SUCCESS('Datos de demostración cargados con éxito'))