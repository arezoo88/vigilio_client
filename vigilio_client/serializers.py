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