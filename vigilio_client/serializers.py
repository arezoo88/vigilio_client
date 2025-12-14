from rest_framework import serializers


class FundTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ShareHolderListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ShareHolderHistorySerializer(serializers.Serializer):
    fund_id = serializers.IntegerField()
    fund = serializers.CharField()
    share_count = serializers.FloatField()
    value = serializers.FloatField()
    date = serializers.CharField()
    fund_type = serializers.CharField()
    pct_of_shares = serializers.FloatField()


class ShareHolderSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    num_funds = serializers.IntegerField()
    total_value = serializers.FloatField()


class ShareHolderForDateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    shareholder_name = serializers.CharField()
    share_holder_histories = ShareHolderHistorySerializer(many=True)


class ChartDataSerializer(serializers.Serializer):
    dates = serializers.ListField(child=serializers.CharField())
    share_counts = serializers.ListField(child=serializers.FloatField())


class ShareHolderDetailHistorySerializer(serializers.Serializer):
    fund_id = serializers.IntegerField()
    fund = serializers.CharField()
    fund_type = serializers.CharField()
    share_count = serializers.FloatField()
    value = serializers.FloatField()
    pct_of_shares = serializers.FloatField()
    date = serializers.CharField()


class ShareHolderDetailSerializer(serializers.Serializer):
    shareholder_name = serializers.CharField()
    share_holder_histories = ShareHolderDetailHistorySerializer(many=True)
    chart_data = ChartDataSerializer(many=True)


# Cash Flow Serializers
class CashFlowSerializer(serializers.Serializer):
    cash_flow = serializers.FloatField()
    in_flow = serializers.FloatField()
    out_flow = serializers.FloatField()
    profits = serializers.FloatField()
    fund_name = serializers.CharField()
    fund_type = serializers.CharField()
    fund_id = serializers.IntegerField()
    symbol = serializers.CharField()
    institute_kind = serializers.CharField()


class CashFlowDetailSerializer(serializers.Serializer):
    cash_flow = serializers.FloatField()
    in_flow = serializers.FloatField()
    out_flow = serializers.FloatField()
    total_units = serializers.FloatField()
    purchase = serializers.FloatField()
    redemption = serializers.FloatField()
    issued_units = serializers.FloatField()
    revoked_units = serializers.FloatField()
    fund_name = serializers.CharField()
    fund_type = serializers.CharField()
    fund_id = serializers.IntegerField()
    symbol = serializers.CharField()
    date = serializers.CharField()


# Returns Serializers
class TotalReturnSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    date = serializers.CharField()
    fund_id = serializers.IntegerField()
    fund_name = serializers.CharField()
    fund_type = serializers.CharField()
    institute_kind = serializers.CharField()
    last_nav = serializers.FloatField()
    last_nav_date = serializers.CharField()
    last_price = serializers.FloatField()
    last_price_date = serializers.CharField()
    has_profit = serializers.BooleanField()
    has_split = serializers.BooleanField()
    total_units = serializers.FloatField()
    bubble = serializers.FloatField()
    thirty = serializers.FloatField()
    ninety = serializers.FloatField()
    one_eighty = serializers.FloatField()
    three_sixty = serializers.FloatField()


class EtfReturnSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    date = serializers.CharField()
    fund_id = serializers.IntegerField()
    fund_name = serializers.CharField()
    fund_type = serializers.CharField()
    institute_kind = serializers.CharField()
    last_nav = serializers.FloatField()
    last_nav_date = serializers.CharField()
    last_price = serializers.FloatField()
    last_price_date = serializers.CharField()
    has_profit = serializers.BooleanField()
    has_split = serializers.BooleanField()
    total_units = serializers.FloatField()
    bubble = serializers.FloatField()
    thirty = serializers.FloatField()
    ninety = serializers.FloatField()
    one_eighty = serializers.FloatField()
    three_sixty = serializers.FloatField()


# NAV Trend Serializers
class NavDataSerializer(serializers.Serializer):
    purchase = serializers.FloatField(allow_null=True)
    redemption = serializers.FloatField(allow_null=True)
    statistical = serializers.FloatField(allow_null=True)
    preferred_purchase = serializers.FloatField(allow_null=True)
    preferred_redemption = serializers.FloatField(allow_null=True)
    common = serializers.FloatField(allow_null=True)


class NavTrendItemSerializer(serializers.Serializer):
    net_asset_value = serializers.FloatField()
    date = serializers.CharField()
    nav_data = NavDataSerializer()


class NavTrendChartDataSerializer(serializers.Serializer):
    dates = serializers.ListField(child=serializers.CharField())
    statisticals = serializers.ListField(child=serializers.FloatField())
    purchases = serializers.ListField(child=serializers.FloatField())
    redemptions = serializers.ListField(child=serializers.FloatField())


class NavTrendSerializer(serializers.Serializer):
    nav_trend = NavTrendItemSerializer(many=True)
    chart_data = NavTrendChartDataSerializer()


# Splits, Profits, Prices Serializers
class SplitSerializer(serializers.Serializer):
    date = serializers.CharField()
    units_ratio = serializers.FloatField()


class ProfitSerializer(serializers.Serializer):
    profit = serializers.FloatField()
    date = serializers.CharField()


class PriceSerializer(serializers.Serializer):
    date = serializers.CharField()
    price = serializers.FloatField()