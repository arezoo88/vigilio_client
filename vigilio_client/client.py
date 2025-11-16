import os
import grpc
from .vigilio_pb2_grpc import VigilioServiceStub
from .vigilio_pb2 import (
    ShareHolderSummaryRequest,
    ShareHolderDetailRequest,
    GetFundTypesRequest,
    ShareHolderExcelRequest,
    ShareHolderChartRequest,
    ShareHolderAnalyzeRequest,
    ShareHolderSummaryExcelRequest,
    ShareHolderListRequest

    
)
from django.conf import settings
from google.protobuf.json_format import MessageToDict


class VigilioClient:
    def __init__(self):
        grpc_conf = settings.VIGILIO_GRPC
        self.host = grpc_conf.get("HOST", "localhost")
        self.port = grpc_conf.get("PORT", 50051)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.cert_file = grpc_conf.get("CERT_FILE") or os.path.join(base_dir, "vigilio_cert", "fullchain.pem")
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
    # FundTypes gRPC
    # ---------------------------
    def get_fund_types(self):
        req = GetFundTypesRequest()
        return self._stub.GetFundTypes(req)

    def get_fund_types_json(self):
        resp = self.get_fund_types()
        return MessageToDict(resp, preserving_proto_field_name=True).get("fund_types", [])


    # ---------------------------
    # ShareHolder Summary
    # ---------------------------
    def get_shareholder_summary(self, date=None, fund_type=None):
        req = ShareHolderSummaryRequest(date=date or "", fund_type=fund_type or "")
        return self._stub.GetShareHolderSummary(req)

    def export_shareholder_summary_excel(self, date=None, fund_type=None):
        req = ShareHolderSummaryExcelRequest(date=date or "", fund_type=fund_type or "")
        return self._stub.ExportShareHolderSummaryExcel(req)

    # ---------------------------
    # ShareHolders
    # ---------------------------
    def list_shareholders(self, fund_type=None):
        req = ShareHolderListRequest(fund_type=fund_type or "")
        return self._stub.ListShareHolders(req)

    def get_shareholder_detail(self, shareholder_id, fund=None , date=None):
        req = ShareHolderDetailRequest(shareholder_id=shareholder_id, fund=fund or "")
        return self._stub.GetShareHolderDetail(req)

    def get_shareholder_detail_json(self, shareholder_id, fund=None):
        """
        Get shareholder detail - JSON format با error handling
        """
        try:
            resp = self.get_shareholder_detail(shareholder_id, fund)
            
            result = {
                "shareholder_name": resp.shareholder_name,
                "share_holder_histories": []
            }
            for h in resp.share_holder_histories:
                history_item = {
                    "fund_id": h.fund_id,
                    "fund": h.fund_name,
                    "fund_type":h.fund_type,
                    "ticker": h.ticker,
                    "share_count": h.share_count,
                    "value": h.value,
                    "date": h.date,
                }
                
        
                if hasattr(h, 'pct_of_shares'):
                    history_item["pct_of_shares"] = h.pct_of_shares
                
                if hasattr(h, 'percentage'):
                    history_item["percentage"] = h.percentage
                
                result["share_holder_histories"].append(history_item)
            
            return result
            
        except grpc.RpcError as e:
            # مدیریت خطاهای gRPC
            raise Exception(f"gRPC Error [{e.code()}]: {e.details()}")
        except Exception as e:
            # مدیریت سایر خطاها
            raise Exception(f"Error getting shareholder detail: {str(e)}")

    def export_shareholder_excel(self, shareholder_id):
        req = ShareHolderExcelRequest(shareholder_id=shareholder_id)
        return self._stub.ExportShareHolderExcel(req)

    def get_shareholder_chart(self, shareholder_id, fund=None, start_date=None, end_date=None):
        req = ShareHolderChartRequest(
            shareholder_id=shareholder_id,
            fund=fund,
            start_date=start_date,
            end_date=end_date
        )
        return self._stub.GetShareHolderChartData(req)

