from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, BrandViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'products', ProductViewSet)

# Remove the 'api/' prefix as it's already provided in the main urls.py
urlpatterns = [
    path('', include(router.urls)),
]