from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import UserAccount, TemporaryToken
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ('phone',)
        
class OtpSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[
                    RegexValidator(r'^\d{8}$', 'phone must be 8 digits'),
                ],)
    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        instance.phone = validated_data.get('phone', instance.phone)
        return instance
class OtpCodeSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(source="id")
    otp = serializers.CharField(validators=[
                    RegexValidator(r'^\d{6}$', 'code must be 6 digits'),
                ],)

    class Meta: 
        model= TemporaryToken
        fields = ['otp','phone',]
 