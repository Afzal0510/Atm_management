

from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=200,required=True)
    initial_amount = serializers.IntegerField(required=True)


    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'initial_amount')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            initial_amount=validated_data.get('initial_amount'),
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user
