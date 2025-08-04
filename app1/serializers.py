from rest_framework import serializers
from .models import AccUsers

class AccUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccUsers
        fields = ['id', 'pass_field']
