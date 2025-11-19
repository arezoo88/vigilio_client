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
    ShareHolderDetailSerializer
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