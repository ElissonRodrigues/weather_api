from rest_framework import serializers
from .models import Station, RegistrationData

class RegistrationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationData
        fields = "__all__"

class StationSerializer(serializers.ModelSerializer):
    #historical_data = RegistrationDataSerializer(many=True, read_only=True, source='registrationdata_set')

    class Meta:
        model = Station
        fields = "__all__"

class ResponseTemplateSerializer(serializers.Serializer):
    success = serializers.BooleanField(required=False, read_only=True)
    data = serializers.JSONField(required=False, allow_null=True) #type: ignore
    errors = serializers.DictField(required=False, read_only=True) #type: ignore

class StationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['station_name', 'city', 'owner', 'latitude', 'longitude', 'uf']



