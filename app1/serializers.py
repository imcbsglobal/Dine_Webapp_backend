from rest_framework import serializers
from .models import AccUsers,DineBill

class AccUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccUsers
        fields = ['id', 'pass_field']



# serializers.py  (append)
from rest_framework import serializers
from .models import TbItemMaster

class TbItemMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TbItemMaster
        fields = [
            'id', 'item_code', 'item_name',
            'rate', 'rate1', 'rate2', 'rate3', 'rate4', 'rate5', 'rate6', 'rate7',
            'kitchen', 'category'
        ]




from rest_framework import serializers
from .models import DineBill

class DineBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = DineBill
        fields = ['billno', 'time_field', 'user_field', 'amount']


class DineBillMonthSerializer(serializers.Serializer):
    """
    Serializer for monthly bill summary
    Shows: month, month_name, total_amount, total_count for each month of current year
    """
    month = serializers.IntegerField()
    month_name = serializers.CharField(max_length=20)
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    total_count = serializers.IntegerField()



from rest_framework import serializers

class DineCancelledBillsSerializer(serializers.Serializer):
    """
    Serializer for combined DineBill and CancelledBills data
    Shows: date, billno, creditcard, colnstatus
    """
    date = serializers.DateField(allow_null=True)
    billno = serializers.DecimalField(max_digits=10, decimal_places=0)
    creditcard = serializers.CharField(max_length=30, allow_null=True, allow_blank=True)
    colnstatus = serializers.CharField(max_length=1, allow_null=True, allow_blank=True)







from rest_framework import serializers

class DineKotSalesDetailSerializer(serializers.Serializer):
    """
    Serializer for dine kot sales detail summary
    Shows: date, item_name, total_qty, total_amount for each day
    """
    date = serializers.DateField(allow_null=True)
    item_name = serializers.CharField(max_length=60, allow_null=True, allow_blank=True)
    total_qty = serializers.DecimalField(max_digits=15, decimal_places=3, allow_null=True)
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=5, allow_null=True)