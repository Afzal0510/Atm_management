from rest_framework import serializers
from .models import CustomUser, UserTransaction


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=200, required=True)
    initial_amount = serializers.IntegerField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'initial_amount', 'is_login', 'is_active', 'open_balance')
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


class UserTransactionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user_id.username")

    class Meta:
        model = UserTransaction
        fields = ['user_id', 'deposit_amount', 'withdraw', 'transaction_type', 'username']


