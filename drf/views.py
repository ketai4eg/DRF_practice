from rest_framework import viewsets, renderers, permissions
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.reverse import reverse
import json
from .models import Categories, Balance, Transactions
from .serializers import UserSerializer, CategorySerializer, TransactionsSerializer
from .permissions import IsOwner


@api_view(['GET',])
def api_root(request, format=None):
    return Response({
        'new user': reverse('user-create', request=request, format=format),
        'user info': reverse('user-info', request=request, format=format),
        "user's categories list": reverse('categories-list', request=request, format=format),
        'transactions list': reverse('transactions-list', request=request, format=format),
        'get your token here': reverse('token-creation', request=request, format=format),

    })


class UserCreateViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def create(self, request, *args, **kwargs):
        User.objects.create_user(username=request.data['username'],
                                 email=request.data['email'],
                                 password=request.data['password'])

        default_categories_list = ["Забота о себе", "Зарплата", "Здоровье и фитнес", "Кафе и рестораны", "Машина",
                                   "Образование", "Отдых и развлечения", "Платежи, комиссии",
                                   "Покупки: одежда, техника", "Продукты", "Проезд"]
        usr = User.objects.get(username=request.data['username']).pk
        Balance.objects.create(username_id=usr, balance=0)
        for i in default_categories_list:
            Categories.objects.create(username_id=usr, category_list=i)
        return Response(request.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):  # this method is called inside of get
        queryset = User.objects.filter(username=self.request.user)
        return queryset

    def update(self, request, *args, **kwargs):
        amount = json.loads(request.body.decode(encoding='UTF-8'))
        try:
            queryset = Balance.objects.get(username=self.request.user)
            queryset.balance += amount['balance']
            queryset.save()
        except:
            Balance.objects.create(username=self.request.user, balance=amount['balance'])
        return Response(request.data)


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = Categories.objects.filter(username_id=self.request.user.pk)
        return queryset

    def perform_create(self, serializer):
        serializer.save(username_id=self.request.user.pk)

    def perform_update(self, serializer):
        serializer.save(username_id=self.request.user.pk)


class TransactionsViewSet(viewsets.ModelViewSet):
    queryset = Transactions.objects.all()
    serializer_class = TransactionsSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = Transactions.objects.filter(username=self.request.user)
        return queryset

    def perform_create(self, serializer):
        amount = self.request.data
        money = Balance.objects.get(username=self.request.user)
        money.balance -= int(amount['amount'])
        money.save()
        serializer.save(username_id=self.request.user.pk)

    def perform_update(self, serializer):
        money = Balance.objects.get(username=self.request.user)
        instance = self.get_object()
        previous_amount = int(instance.amount)
        money.balance = money.balance + previous_amount - serializer.validated_data['amount']
        money.save()
        serializer.save(username_id=self.request.user.pk)

    def perform_destroy(self, instance):
        money = Balance.objects.get(username=self.request.user)
        previous_amount = int(instance.amount)
        money.balance = money.balance + previous_amount
        money.save()
        instance.delete()


def token_creation(request):
    return render(request, 'get_token.html',)