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


    def list_cash_flows(self, start_date: str, end_date: str,
                        institute_kind: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get cash flow summary for multiple funds

        Args:
            start_date: Start date (required)
            end_date: End date (required)
            institute_kind: Optional institute kind to filter by

        Returns:
            List of cash flows with aggregated data
        """
        request = vigilio_pb2.ListCashFlowsRequest(
            start_date=start_date,
            end_date=end_date,
            institute_kind=institute_kind if institute_kind else ""
        )
        response = self.stub.ListCashFlows(request)

        return [
            {
                'cash_flow': cf.cash_flow,
                'in_flow': cf.in_flow,
                'out_flow': cf.out_flow,
                'profits': cf.profits,
                'fund_name': cf.fund_name,
                'fund_type': cf.fund_type,
                'fund_id': cf.fund_id,
                'symbol': cf.symbol,
                'institute_kind': cf.institute_kind
            }
            for cf in response.cash_flows
        ]

    def get_cash_flow_detail(self, fund_id: int, start_date: str, end_date: str,
                             fund_type: str, institute_kind: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get detailed cash flow for a specific fund

        Args:
            fund_id: Fund ID (required)
            start_date: Start date (required)
            end_date: End date (required)
            fund_type: Fund type - "ETF" or "CODAL" (required)
            institute_kind: Optional institute kind to filter by

        Returns:
            List of detailed cash flows by date
        """
        request = vigilio_pb2.GetCashFlowDetailRequest(
            fund_id=fund_id,
            start_date=start_date,
            end_date=end_date,
            fund_type=fund_type,
            institute_kind=institute_kind if institute_kind else ""
        )
        response = self.stub.GetCashFlowDetail(request)

        return [
            {
                'cash_flow': cf.cash_flow,
                'in_flow': cf.in_flow,
                'out_flow': cf.out_flow,
                'total_units': cf.total_units,
                'purchase': cf.purchase,
                'redemption': cf.redemption,
                'issued_units': cf.issued_units,
                'revoked_units': cf.revoked_units,
                'fund_name': cf.fund_name,
                'fund_type': cf.fund_type,
                'fund_id': cf.fund_id,
                'symbol': cf.symbol,
                'date': cf.date
            }
            for cf in response.cash_flows
        ]

    def list_total_returns(self, fund_type: Optional[str] = None,
                          fund_id: Optional[int] = None,
                          institute_kind: Optional[str] = None,
                          date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get total returns for all funds

        Args:
            fund_type: Optional fund type - "Codal Fund" or "ETF Fund"
            fund_id: Optional fund ID to filter by
            institute_kind: Optional institute kind to filter by
            date: Optional date in Jalali format

        Returns:
            List of total returns with NAV, price, and return data
        """
        request = vigilio_pb2.ListTotalReturnsRequest(
            fund_type=fund_type if fund_type else "",
            fund_id=fund_id if fund_id else 0,
            institute_kind=institute_kind if institute_kind else "",
            date=date if date else ""
        )
        response = self.stub.ListTotalReturns(request)

        return [
            {
                'id': ret.id,
                'date': ret.date,
                'fund_id': ret.fund_id,
                'fund_name': ret.fund_name,
                'fund_type': ret.fund_type,
                'institute_kind': ret.institute_kind,
                'last_nav': ret.last_nav,
                'last_nav_date': ret.last_nav_date,
                'last_price': ret.last_price,
                'last_price_date': ret.last_price_date,
                'has_profit': ret.has_profit,
                'has_split': ret.has_split,
                'total_units': ret.total_units,
                'bubble': ret.bubble,
                'thirty': ret.thirty,
                'ninety': ret.ninety,
                'one_eighty': ret.one_eighty,
                'three_sixty': ret.three_sixty
            }
            for ret in response.returns
        ]

    def list_etf_returns(self, fund_id: Optional[int] = None,
                        institute_kind: Optional[str] = None,
                        date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get ETF returns

        Args:
            fund_id: Optional fund ID to filter by
            institute_kind: Optional institute kind to filter by
            date: Optional date in Jalali format

        Returns:
            List of ETF returns with NAV, price, and return data
        """
        request = vigilio_pb2.ListEtfReturnsRequest(
            fund_id=fund_id if fund_id else 0,
            institute_kind=institute_kind if institute_kind else "",
            date=date if date else ""
        )
        response = self.stub.ListEtfReturns(request)

        return [
            {
                'id': ret.id,
                'date': ret.date,
                'fund_id': ret.fund_id,
                'fund_name': ret.fund_name,
                'fund_type': ret.fund_type,
                'institute_kind': ret.institute_kind,
                'last_nav': ret.last_nav,
                'last_nav_date': ret.last_nav_date,
                'last_price': ret.last_price,
                'last_price_date': ret.last_price_date,
                'has_profit': ret.has_profit,
                'has_split': ret.has_split,
                'total_units': ret.total_units,
                'bubble': ret.bubble,
                'thirty': ret.thirty,
                'ninety': ret.ninety,
                'one_eighty': ret.one_eighty,
                'three_sixty': ret.three_sixty
            }
            for ret in response.returns
        ]

    def get_nav_trend(self, fund_id: int) -> Dict[str, Any]:
        """
        Get NAV trend data for a specific fund

        Args:
            fund_id: Fund ID (LastFundNavAndDividendDate id)

        Returns:
            NAV trend data with chart data
            Example: {
                'nav_trend': [...],
                'chart_data': {
                    'dates': [...],
                    'statisticals': [...],
                    'purchases': [...],
                    'redemptions': [...]
                }
            }
        """
        request = vigilio_pb2.GetNavTrendRequest(fund_id=fund_id)
        response = self.stub.GetNavTrend(request)

        return {
            'nav_trend': [
                {
                    'net_asset_value': item.net_asset_value,
                    'date': item.date,
                    'nav_data': {
                        'purchase': item.nav_data.purchase if item.nav_data.HasField('purchase') else None,
                        'redemption': item.nav_data.redemption if item.nav_data.HasField('redemption') else None,
                        'statistical': item.nav_data.statistical if item.nav_data.HasField('statistical') else None,
                        'preferred_purchase': item.nav_data.preferred_purchase if item.nav_data.HasField('preferred_purchase') else None,
                        'preferred_redemption': item.nav_data.preferred_redemption if item.nav_data.HasField('preferred_redemption') else None,
                        'common': item.nav_data.common if item.nav_data.HasField('common') else None
                    }
                }
                for item in response.nav_trend
            ],
            'chart_data': {
                'dates': list(response.chart_data.dates),
                'statisticals': list(response.chart_data.statisticals),
                'purchases': list(response.chart_data.purchases),
                'redemptions': list(response.chart_data.redemptions)
            }
        }

    def get_splits(self, fund_id: int) -> List[Dict[str, Any]]:
        """
        Get fund splits for a specific fund

        Args:
            fund_id: Fund ID (LastFundNavAndDividendDate id)

        Returns:
            List of fund splits
        """
        request = vigilio_pb2.GetSplitsRequest(fund_id=fund_id)
        response = self.stub.GetSplits(request)

        return [
            {
                'date': split.date,
                'units_ratio': split.units_ratio
            }
            for split in response.splits
        ]

    def get_profits(self, fund_id: int) -> List[Dict[str, Any]]:
        """
        Get fund profits/dividends for a specific fund

        Args:
            fund_id: Fund ID (LastFundNavAndDividendDate id)

        Returns:
            List of fund profits
        """
        request = vigilio_pb2.GetProfitsRequest(fund_id=fund_id)
        response = self.stub.GetProfits(request)

        return [
            {
                'profit': profit.profit,
                'date': profit.date
            }
            for profit in response.profits
        ]

    def get_prices(self, fund_id: int) -> List[Dict[str, Any]]:
        """
        Get ETF close prices for a specific fund

        Args:
            fund_id: Fund ID (LastFundNavAndDividendDate id)

        Returns:
            List of ETF close prices
        """
        request = vigilio_pb2.GetPricesRequest(fund_id=fund_id)
        response = self.stub.GetPrices(request)

        return [
            {
                'date': price.date,
                'price': price.price
            }
            for price in response.prices
        ]


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