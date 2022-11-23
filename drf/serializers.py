from django.contrib.auth.models import User
from rest_framework import serializers

from drf.models import Balance, Categories, Transactions


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'username_id', 'category_list']


class UserSerializer(serializers.ModelSerializer):
    balance = serializers.PrimaryKeyRelatedField(many=False, source='balance.balance', queryset=Balance.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'balance']
        write_only_fields = ['password', ]


class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = ['id', 'username', 'amount', 'time', 'category', 'organisation']
        read_only_fields = ['username']
