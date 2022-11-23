from django.contrib.auth.models import User
from rest_framework import serializers, fields

from drf.models import Balance, Categories, Transactions


class CategorySerializer(serializers.ModelSerializer):
    # username=serializers.PrimaryKeyRelatedField(many=False, source='username.username', queryset=User.objects.all())
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
    # category = fields.ChoiceField(Categories.category_list)
    class Meta:
        model = Transactions
        fields = ['id', 'username', 'amount', 'time', 'category', 'organisation']
        read_only_fields = ['username']
