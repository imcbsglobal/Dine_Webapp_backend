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
