"""
Vigilio gRPC Client Class

A comprehensive client for interacting with the Vigilio gRPC server.
Provides easy-to-use methods for all available gRPC endpoints.

Usage:
    from vigilio_client.client import VigilioClient

    # Create client
    client = VigilioClient('127.0.0.1:50051')

    # Use methods
    fund_types = client.get_fund_types()
    shareholders = client.list_shareholders()
    detail = client.get_shareholder_detail(5040, fund="ضمان")
    excel_bytes = client.export_shareholder_excel(5040, fund="ضمان")
"""

import grpc
from . import vigilio_pb2
from . import vigilio_pb2_grpc
from typing import Optional, List, Dict, Any
from io import BytesIO


class VigilioClient:
    """
    Client class for Vigilio gRPC service

    Attributes:
        host (str): gRPC server host and port (e.g., '127.0.0.1:50051')
        channel: gRPC channel connection
        stub: gRPC service stub
    """

    def __init__(self, host: str = '127.0.0.1:50051', secure: bool = False,
                 credentials_path: Optional[str] = None):
        """
        Initialize the Vigilio gRPC client

        Args:
            host: Server host and port (default: '127.0.0.1:50051')
            secure: Use secure connection (SSL/TLS) (default: False)
            credentials_path: Path to SSL credentials if secure=True
        """
        self.host = host
        self.secure = secure

        if secure and credentials_path:
            with open(credentials_path, 'rb') as f:
                credentials = grpc.ssl_channel_credentials(f.read())
            self.channel = grpc.secure_channel(host, credentials)
        else:
            self.channel = grpc.insecure_channel(host)

        self.stub = vigilio_pb2_grpc.VigilioServiceStub(self.channel)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close channel"""
        self.close()

    def close(self):
        """Close the gRPC channel"""
        if self.channel:
            self.channel.close()

    # ========================================================================
    # Fund Types Methods
    # ========================================================================

    def get_fund_types(self) -> List[Dict[str, Any]]:
        """
        Get all fund types

        Returns:
            List of fund types with id and name
            Example: [{'id': 1, 'name': 'ETF'}, {'id': 2, 'name': 'اهرمی'}]
        """
        request = vigilio_pb2.GetFundTypesRequest()
        response = self.stub.GetFundTypes(request)

        return [
            {'id': ft.id, 'name': ft.name}
            for ft in response.fund_types
        ]

    # ========================================================================
    # ShareHolder List Methods
    # ========================================================================

    def list_shareholders(self, fund_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of all shareholders (names and IDs only)

        Args:
            fund_type: Optional fund type ID to filter by

        Returns:
            List of shareholders with id and name
            Example: [{'id': 5040, 'name': 'شرکت سرمایه گذاری...'}]
        """
        request = vigilio_pb2.ShareHolderListRequest(
            fund_type=fund_type if fund_type else ""
        )
        response = self.stub.ListShareHolders(request)

        return [
            {'id': sh.id, 'name': sh.name}
            for sh in response.shareholders
        ]

    # ========================================================================
    # ShareHolder Summary Methods
    # ========================================================================

    def get_shareholders_summary(self, date: Optional[str] = None,
                                 fund_type: Optional[str] = None,
                                 search: Optional[str] = None,
                                 ordering: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get shareholders summary with aggregated data

        Args:
            date: Optional date in Jalali format (e.g., '1403/08/15')
            fund_type: Optional fund type ID to filter by
            search: Optional search term for shareholder name
            ordering: Optional ordering field (e.g., '-num_funds', 'total_value')

        Returns:
            List of shareholders with summary data
            Example: [
                {
                    'id': 5040,
                    'name': 'شرکت سرمایه گذاری...',
                    'num_funds': 5,
                    'total_value': 1500000000.0
                }
            ]
        """
        request = vigilio_pb2.ShareHolderSummaryListRequest(
            date=date if date else "",
            fund_type=fund_type if fund_type else "",
            search=search if search else "",
            ordering=ordering if ordering else ""
        )
        response = self.stub.ShareHoldersSummary(request)

        return [
            {
                'id': sh.id,
                'name': sh.name,
                'num_funds': sh.num_funds,
                'total_value': sh.total_value
            }
            for sh in response.shareholders
        ]

    def export_shareholders_summary_excel(self, fund_type: str,
                                         date: Optional[str] = None) -> bytes:
        """
        Export shareholders summary to Excel

        Args:
            fund_type: Fund type ID (required)
            date: Optional date in Jalali format

        Returns:
            Excel file as bytes
        """
        request = vigilio_pb2.ShareHolderSummaryExportRequest(
            fund_type=fund_type,
            date=date if date else ""
        )
        response = self.stub.ExportShareHoldersSummaryExcel(request)

        return response.excel_data

    def save_shareholders_summary_excel(self, fund_type: str,
                                       date: Optional[str] = None,
                                       output_path: Optional[str] = None) -> str:
        """
        Export shareholders summary to Excel and save to file

        Args:
            fund_type: Fund type ID (required)
            date: Optional date in Jalali format
            output_path: Optional output path (default: /tmp/filename)

        Returns:
            Path to saved file
        """
        request = vigilio_pb2.ShareHolderSummaryExportRequest(
            fund_type=fund_type,
            date=date if date else ""
        )
        response = self.stub.ExportShareHoldersSummaryExcel(request)

        if not output_path:
            output_path = f"/tmp/{response.filename}"

        with open(output_path, 'wb') as f:
            f.write(response.excel_data)

        return output_path

    # ========================================================================
    # ShareHolder Detail Methods (for specific date)
    # ========================================================================

    def get_shareholder_for_date(self, shareholder_id: int,
                                 date: Optional[str] = None,
                                 fund_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get shareholder details for a specific date

        Args:
            shareholder_id: Shareholder ID
            date: Optional date in Jalali format
            fund_type: Optional fund type ID to filter by

        Returns:
            Shareholder details with fund histories
        """
        request = vigilio_pb2.ShareHolderForDateRequest(
            shareholder_id=shareholder_id,
            date=date if date else "",
            fund_type=fund_type if fund_type else ""
        )
        response = self.stub.GetShareHolderForDate(request)

        return {
            'id': response.id,
            'shareholder_name': response.shareholder_name,
            'share_holder_histories': [
                {
                    'fund_id': fh.fund_id,
                    'fund': fh.fund,
                    'share_count': fh.share_count,
                    'value': fh.value,
                    'date': fh.date,
                    'fund_type': fh.fund_type,
                    'pct_of_shares': fh.pct_of_shares
                }
                for fh in response.share_holder_histories
            ]
        }

    # ========================================================================
    # ShareHolder Detail Methods (with fund filter and chart data)
    # ========================================================================

    def get_shareholder_detail(self, shareholder_id: int,
                               fund: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed shareholder information with fund filtering and chart data
        Corresponds to: api/v1/vigilio/etf_funds/shareholders/{id}/?fund=...

        Args:
            shareholder_id: Shareholder ID
            fund: Optional fund ticker to filter by (e.g., 'ضمان')

        Returns:
            Shareholder details with histories and chart data
            Example: {
                'shareholder_name': 'شرکت سرمایه گذاری...',
                'share_holder_histories': [...],
                'chart_data': [{'dates': [...], 'share_counts': [...]}]
            }
        """
        request = vigilio_pb2.GetShareHolderDetailRequest(
            shareholder_id=shareholder_id,
            fund=fund if fund else ""
        )
        response = self.stub.GetShareHolderDetail(request)

        return {
            'shareholder_name': response.shareholder_name,
            'share_holder_histories': [
                {
                    'fund_id': fh.fund_id,
                    'fund': fh.fund,
                    'fund_type': fh.fund_type,
                    'share_count': fh.share_count,
                    'value': fh.value,
                    'pct_of_shares': fh.pct_of_shares,
                    'date': fh.date
                }
                for fh in response.share_holder_histories
            ],
            'chart_data': [
                {
                    'dates': list(chart.dates),
                    'share_counts': list(chart.share_counts)
                }
                for chart in response.chart_data
            ]
        }

    def export_shareholder_excel(self, shareholder_id: int,
                                 fund: Optional[str] = None) -> bytes:
        """
        Export specific shareholder data to Excel
        Corresponds to: api/v1/vigilio/etf_funds/shareholders/{id}/export_excel/?fund=...

        Args:
            shareholder_id: Shareholder ID
            fund: Optional fund ticker to filter by

        Returns:
            Excel file as bytes
        """
        request = vigilio_pb2.ExportShareHolderExcelRequest(
            shareholder_id=shareholder_id,
            fund=fund if fund else ""
        )
        response = self.stub.ExportShareHolderExcel(request)

        return response.excel_file

    def save_shareholder_excel(self, shareholder_id: int,
                               fund: Optional[str] = None,
                               output_path: Optional[str] = None) -> str:
        """
        Export specific shareholder data to Excel and save to file

        Args:
            shareholder_id: Shareholder ID
            fund: Optional fund ticker to filter by
            output_path: Optional output path (default: /tmp/filename)

        Returns:
            Path to saved file
        """
        request = vigilio_pb2.ExportShareHolderExcelRequest(
            shareholder_id=shareholder_id,
            fund=fund if fund else ""
        )
        response = self.stub.ExportShareHolderExcel(request)

        if not output_path:
            output_path = f"/tmp/{response.file_name}"

        with open(output_path, 'wb') as f:
            f.write(response.excel_file)

        return output_path

    def read_shareholder_excel(self, shareholder_id: int,
                               fund: Optional[str] = None):
        """
        Export shareholder data to Excel and read it with pandas

        Args:
            shareholder_id: Shareholder ID
            fund: Optional fund ticker to filter by

        Returns:
            pandas DataFrame (requires pandas to be installed)
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for this method. Install with: pip install pandas openpyxl")

        excel_bytes = self.export_shareholder_excel(shareholder_id, fund)
        excel_buffer = BytesIO(excel_bytes)
        df = pd.read_excel(excel_buffer, engine='openpyxl')

        return df

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def ping(self) -> bool:
        """
        Test connection to server

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.get_fund_types()
            return True
        except Exception:
            return False

    def __repr__(self):
        return f"VigilioClient(host='{self.host}', secure={self.secure})"


# ============================================================================
# Example Usage
# ============================================================================

def example_usage():
    """Example usage of VigilioClient"""

    # Create client (use context manager for auto-cleanup)
    with VigilioClient('127.0.0.1:50051') as client:

        # Test connection
        if not client.ping():
            print("Failed to connect to server")
            return

        print("✓ Connected to Vigilio gRPC Server")

        # Get fund types
        print("\n1. Getting fund types...")
        fund_types = client.get_fund_types()
        for ft in fund_types:
            print(f"  - {ft['name']} (ID: {ft['id']})")

        # List shareholders
        print("\n2. Listing shareholders...")
        shareholders = client.list_shareholders()
        print(f"  Total shareholders: {len(shareholders)}")
        for sh in shareholders[:3]:
            print(f"  - {sh['name']} (ID: {sh['id']})")

        # Get shareholders summary
        print("\n3. Getting shareholders summary...")
        summary = client.get_shareholders_summary(fund_type="1")
        for sh in summary[:3]:
            print(f"  - {sh['name']}: {sh['num_funds']} funds, "
                  f"value: {sh['total_value']:,.0f}")

        # Get specific shareholder detail
        print("\n4. Getting shareholder detail...")
        detail = client.get_shareholder_detail(5040, fund="ضمان")
        print(f"  Shareholder: {detail['shareholder_name']}")
        print(f"  Histories: {len(detail['share_holder_histories'])}")
        print(f"  Chart data points: {len(detail['chart_data'][0]['dates']) if detail['chart_data'] else 0}")

        # Export to Excel
        print("\n5. Exporting to Excel...")
        excel_path = client.save_shareholder_excel(5040, fund="ضمان")
        print(f"  Saved to: {excel_path}")

        # Read Excel with pandas
        print("\n6. Reading Excel with pandas...")
        try:
            df = client.read_shareholder_excel(5040, fund="ضمان")
            print(f"  DataFrame shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
        except ImportError:
            print("  (pandas not installed)")

        print("\n✓ All examples completed!")


if __name__ == '__main__':
    print("="*70)
    print("Vigilio gRPC Client Examples")
    print("="*70)

    try:
        example_usage()
    except grpc.RpcError as e:
        print(f"\n✗ gRPC Error: {e.code()} - {e.details()}")
        print("\nMake sure the gRPC server is running:")
        print("  cd core/grpc_server && python grpc.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()