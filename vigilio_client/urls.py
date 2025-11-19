from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FundTypeViewSet, ShareHolderViewSet

app_name = 'vigilio_client'

router = DefaultRouter()
router.register(r'fund-types', FundTypeViewSet, basename='fund-type')
router.register(r'shareholders', ShareHolderViewSet, basename='shareholder')

urlpatterns = [
    path('', include(router.urls)),
]