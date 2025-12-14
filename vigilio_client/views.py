from pickle import FALSE

from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings
import grpc

from .client import VigilioClient
from .serializers import (
    FundTypeSerializer,
    ShareHolderListSerializer,
    ShareHolderSummarySerializer,
    ShareHolderForDateSerializer,
    ShareHolderDetailSerializer,
    CashFlowSerializer,
    CashFlowDetailSerializer,
    TotalReturnSerializer,
    EtfReturnSerializer,
    NavTrendSerializer,
    SplitSerializer,
    ProfitSerializer,
    PriceSerializer
)


def get_grpc_client():
    """Helper function to get gRPC client from settings"""
    grpc_host = getattr(settings, 'VIGILIO_GRPC_HOST', '127.0.0.1:50051')
    secure = getattr(settings, 'VIGILIO_GRPC_SECURE', False)
    credentials_path = getattr(settings, 'VIGILIO_GRPC_CREDENTIALS_PATH', None)

    return VigilioClient(host=grpc_host, secure=secure, credentials_path=credentials_path)


class FundTypeViewSet(viewsets.ViewSet):
    """
    ViewSet for Fund Types

    list: GET /vigilio/fund-types/
    """
    http_method_names = ['get']
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        """Get all fund types"""
        try:
            with get_grpc_client() as client:
                fund_types = client.get_fund_types()
                serializer = FundTypeSerializer(fund_types, many=True)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ShareHolderViewSet(viewsets.ViewSet):
    """
    ViewSet for ShareHolders

    list: GET /vigilio/shareholders/?fund_type=<fund_type>
    retrieve: GET /vigilio/shareholders/<id>/?fund=<fund>
    summary: GET /vigilio/shareholders/summary/?date=<date>&fund_type=<fund_type>&search=<search>&ordering=<ordering>
    summary_excel: GET /vigilio/shareholders/summary_excel/?fund_type=<fund_type>&date=<date>
    for_date: GET /vigilio/shareholders/<id>/for_date/?date=<date>&fund_type=<fund_type>
    excel: GET /vigilio/shareholders/<id>/excel/?fund=<fund>
    """
    http_method_names = ['get']
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        """
        List all shareholders
        Query params: fund_type (optional)
        """
        fund_type = request.query_params.get('fund_type', None)

        try:
            with get_grpc_client() as client:
                shareholders = client.list_shareholders(fund_type=fund_type)
                serializer = ShareHolderListSerializer(shareholders, many=True)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """
        Get detailed shareholder information with chart data
        Query params: fund (optional)
        """
        fund = request.query_params.get('fund', None)

        try:
            with get_grpc_client() as client:
                detail = client.get_shareholder_detail(
                    shareholder_id=int(pk),
                    fund=fund
                )
                serializer = ShareHolderDetailSerializer(detail)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get shareholders summary with aggregated data
        Query params: date, fund_type, search, ordering (all optional)
        """
        date = request.query_params.get('date', None)
        fund_type = request.query_params.get('fund_type', None)
        search = request.query_params.get('search', None)
        ordering = request.query_params.get('ordering', None)

        try:
            with get_grpc_client() as client:
                summary = client.get_shareholders_summary(
                    date=date,
                    fund_type=fund_type,
                    search=search,
                    ordering=ordering
                )
                serializer = ShareHolderSummarySerializer(summary, many=True)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='summary_excel')
    def summary_excel(self, request):
        """
        Export shareholders summary to Excel
        Query params: fund_type (required), date (optional)
        """
        fund_type = request.query_params.get('fund_type')
        date = request.query_params.get('date', None)

        if not fund_type:
            return Response(
                {'error': 'fund_type query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with get_grpc_client() as client:
                excel_data = client.export_shareholders_summary_excel(
                    fund_type=fund_type,
                    date=date
                )

                response = HttpResponse(
                    excel_data,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="shareholders_summary_{fund_type}.xlsx"'
                return response
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='for_date')
    def for_date(self, request, pk=None):
        """
        Get shareholder details for a specific date
        Query params: date, fund_type (both optional)
        """
        date = request.query_params.get('date', None)
        fund_type = request.query_params.get('fund_type', None)

        try:
            with get_grpc_client() as client:
                shareholder = client.get_shareholder_for_date(
                    shareholder_id=int(pk),
                    date=date,
                    fund_type=fund_type
                )
                serializer = ShareHolderForDateSerializer(shareholder)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def excel(self, request, pk=None):
        """
        Export specific shareholder data to Excel
        Query params: fund (optional)
        """
        fund = request.query_params.get('fund', None)

        try:
            with get_grpc_client() as client:
                excel_data = client.export_shareholder_excel(
                    shareholder_id=int(pk),
                    fund=fund
                )

                response = HttpResponse(
                    excel_data,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="shareholder_{pk}.xlsx"'
                return response
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CashFlowViewSet(generics.ListAPIView ,generics.RetrieveAPIView ,viewsets.GenericViewSet):
    """
    ViewSet for Cash Flows

    list: GET /vigilio/cash-flows/?start_date=<start_date>&end_date=<end_date>&institute_kind=<institute_kind>
    detail: GET /vigilio/cash-flows/<fund_id>/detail/?start_date=<start_date>&end_date=<end_date>&fund_type=<fund_type>&institute_kind=<institute_kind>
    """
    http_method_names = ['get']
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        """
        List cash flows summary for all funds
        Query params: start_date (required), end_date (required), institute_kind (optional)
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        institute_kind = request.query_params.get('institute_kind', None)

        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date query parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with get_grpc_client() as client:
                cash_flows = client.list_cash_flows(
                    start_date=start_date,
                    end_date=end_date,
                    institute_kind=institute_kind
                )
                serializer = CashFlowSerializer(cash_flows, many=True)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """
        Get detailed cash flow for a specific fund
        Query params: start_date (required), end_date (required), fund_type (required), institute_kind (optional)
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        fund_type = request.query_params.get('fund_type')
        institute_kind = request.query_params.get('institute_kind', None)

        if not start_date or not end_date or not fund_type:
            return Response(
                {'error': 'start_date, end_date, and fund_type query parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with get_grpc_client() as client:
                cash_flow_detail = client.get_cash_flow_detail(
                    fund_id=int(pk),
                    start_date=start_date,
                    end_date=end_date,
                    fund_type=fund_type,
                    institute_kind=institute_kind
                )
                serializer = CashFlowDetailSerializer(cash_flow_detail, many=True)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TotalReturnViewSet(generics.ListAPIView,viewsets.GenericViewSet):
    """
    ViewSet for Total Returns

    list: GET /vigilio/total-returns/?fund_type=<fund_type>&fund_id=<fund_id>&institute_kind=<institute_kind>&date=<date>
    """
    http_method_names = ['get']
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        """
        List total returns for all funds
        Query params: fund_type, fund_id, institute_kind, date (all optional)
        """
        fund_type = request.query_params.get('fund_type', None)
        fund_id = request.query_params.get('fund_id', None)
        institute_kind = request.query_params.get('institute_kind', None)
        date = request.query_params.get('date', None)

        try:
            with get_grpc_client() as client:
                returns = client.list_total_returns(
                    fund_type=fund_type,
                    fund_id=int(fund_id) if fund_id else None,
                    institute_kind=institute_kind,
                    date=date
                )
                serializer = TotalReturnSerializer(returns, many=True)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EtfReturnViewSet(generics.ListAPIView,viewsets.GenericViewSet):
    """
    ViewSet for ETF Returns

    list: GET /vigilio/etf-returns/?fund_id=<fund_id>&institute_kind=<institute_kind>&date=<date>
    """
    http_method_names = ['get']
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        """
        List ETF returns
        Query params: fund_id, institute_kind, date (all optional)
        """
        fund_id = request.query_params.get('fund_id', None)
        institute_kind = request.query_params.get('institute_kind', None)
        date = request.query_params.get('date', None)

        try:
            with get_grpc_client() as client:
                returns = client.list_etf_returns(
                    fund_id=int(fund_id) if fund_id else None,
                    institute_kind=institute_kind,
                    date=date
                )
                serializer = EtfReturnSerializer(returns, many=True)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FundDetailViewSet(viewsets.GenericViewSet):
    """
    ViewSet for Fund Detail (NAV trends, splits, profits, prices)

    nav_trend: GET /vigilio/funds/<fund_id>/nav_trend/
    splits: GET /vigilio/funds/<fund_id>/splits/
    profits: GET /vigilio/funds/<fund_id>/profits/
    prices: GET /vigilio/funds/<fund_id>/prices/
    """
    http_method_names = ['get']
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=False, methods=['get'], url_path='nav_trend')
    def nav_trend(self, request):
        """
        Get NAV trend data for a specific fund
        """
        fund_id = request.query_params.get('fund_id', None)
        if not fund_id:
            Response(
                {'error': 'fund_id query parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            with get_grpc_client() as client:
                nav_trend = client.get_nav_trend(fund_id=int(fund_id))
                serializer = NavTrendSerializer(nav_trend)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def splits(self, request):
        """
        Get fund splits for a specific fund
        """
        fund_id = request.query_params.get('fund_id', None)
        if not fund_id:
            Response(
                {'error': 'fund_id query parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            with get_grpc_client() as client:
                splits = client.get_splits(fund_id=int(fund_id))
                serializer = SplitSerializer(splits, many=True)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=FALSE, methods=['get'])
    def profits(self, request):
        """
        Get fund profits/dividends for a specific fund
        """
        fund_id = request.query_params.get('fund_id', None)
        if not fund_id:
            Response(
                {'error': 'fund_id query parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            with get_grpc_client() as client:
                profits = client.get_profits(fund_id=int(fund_id))
                serializer = ProfitSerializer(profits, many=True)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def prices(self, request, pk=None):
        """
        Get ETF close prices for a specific fund
        """
        try:
            with get_grpc_client() as client:
                prices = client.get_prices(fund_id=int(pk))
                serializer = PriceSerializer(prices, many=True)
                return Response(serializer.data)
        except grpc.RpcError as e:
            return Response(
                {'error': f'gRPC Error: {e.code()} - {e.details()}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )