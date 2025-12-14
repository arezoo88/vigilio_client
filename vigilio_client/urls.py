from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FundTypeViewSet,
    ShareHolderViewSet,
    CashFlowViewSet,
    TotalReturnViewSet,
    EtfReturnViewSet,
    FundDetailViewSet
)

app_name = 'vigilio_client'

router = DefaultRouter()
router.register(r'fund-types', FundTypeViewSet, basename='fund-type')
router.register(r'shareholders', ShareHolderViewSet, basename='shareholder')
router.register(r'cashflow', CashFlowViewSet, basename='cash-flow')
router.register(r'total_return', TotalReturnViewSet, basename='total-return')
router.register(r'etf_return', EtfReturnViewSet, basename='etf-return')
router.register(r'watchlist', FundDetailViewSet, basename='watchlist')

urlpatterns = [
    path('', include(router.urls)),
]