# products/views.py
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Brand, Product
from .serializers import CategorySerializer, BrandSerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().prefetch_related('specifications')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'brand', 'stock']
    search_fields = ['name', 'description', 'brand__name', 'category__name']
    ordering_fields = ['name', 'price', 'stock', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category_name', None)
        brand = self.request.query_params.get('brand_name', None)
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)

        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if brand:
            queryset = queryset.filter(brand__name__icontains=brand)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

    def get_serializer_context(self):
        """
        Proporcionar el objeto request al serializer para poder
        generar URLs absolutas para las imágenes
        """
        context = super().get_serializer_context()
        return context