import grpc
from .vigilio_pb2_grpc import VigilioServiceStub
from .vigilio_pb2 import (
    ShareHolderSummaryRequest,
    ShareHolderDetailRequest,
    GetReturnsRequest,
    GetDividendsRequest,
    GetNavsRequest
)
from django.conf import settings

class VigilioClient:
    def __init__(self):
        grpc_conf = settings.VIGILIO_GRPC
        self.host = grpc_conf.get("HOST", "localhost")
        self.port = grpc_conf.get("PORT", 50051)
        self.cert_file = grpc_conf.get("CERT_FILE")
        self._channel = None
        self._stub = None
        self._connect()

    def _connect(self):
        if self.cert_file:
            with open(self.cert_file, "rb") as f:
                trusted_certs = f.read()
            credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
            self._channel = grpc.secure_channel(f"{self.host}:{self.port}", credentials)
        else:
            self._channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self._stub = VigilioServiceStub(self._channel)

    # ---------------------------
    # مثال متد gRPC
    # ---------------------------
    def get_shareholder_summary(self, date=None, fund_type=None, search=None):
        req = ShareHolderSummaryRequest(date=date or "", fund_type=fund_type or "", search=search or "")
        return self._stub.GetShareHolderSummary(req)

    def get_shareholder_detail(self, shareholder_id, date=None, fund_type=None):
        req = ShareHolderDetailRequest(
            shareholder_id=str(shareholder_id),
            date=date or "",
            fund_type=fund_type or ""
        )
        return self._stub.GetShareHolderDetail(req)