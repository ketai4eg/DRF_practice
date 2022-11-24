from rest_framework import viewsets, renderers, filters
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.reverse import reverse
import json
from .models import Categories, Balance, Transactions
from .serializers import UserSerializer, CategorySerializer, TransactionsSerializer
from .permissions import IsOwner
from django_filters.rest_framework import DjangoFilterBackend
from django_cron import CronJobBase, Schedule
from django.core.mail import send_mail
from DRF_test import settings

# emails treatment and body
def email():
    queryset = User.objects.all()
    for user in queryset:
        print(user.username)
        print(user.email)
        if user.email:
            subject = 'Your statistics'
            message = f' Dear {user.username}, up to now you have available {Balance.objects.get(username=user.id).balance} money \n Have a nice day! '
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail(subject, message, email_from, recipient_list)
    return "done"

#
# # scheduler for e-mails sending
class MyCronJob(CronJobBase):
    schedule = Schedule(run_at_times=["09:00", ], retry_after_failure_mins=1)
    code = 'views.MyCronJob'
email()

# main page with links to other
@api_view(['GET', ])
def api_root(request, format=None):
    """Main page with links to other"""
    email()
    return Response({
        'new user': reverse('user-create', request=request),
        'user info': reverse('user-info', request=request),
        "user's categories list": reverse('categories-list', request=request),
        'transactions list': reverse('transactions-list', request=request),
        'get your token here': reverse('token-creation', request=request),

    })


class UserCreateViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def create(self, request, *args, **kwargs):
        """User creation. List of standard categories will be added automatically. Balance is 0 for new user set
        automatically. """
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


# Getting information about current user. Also balance can be top up here.
class UserViewSet(viewsets.ModelViewSet):
    """Getting information about current user. Also balance can be top up here."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
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


# Full information about categories which user has. Can be updated, created new one, or deleted.
class CategoriesViewSet(viewsets.ModelViewSet):
    """Get full list of categories or detailed info on specific one by id, add new category or update existed one by
    id """
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


# Full information on Transactions which user has. Can be updated, created new one, or deleted. The balance will be
# changed in case of updating of the amount in any Transactions and in case of deleting.
class TransactionsViewSet(viewsets.ModelViewSet):
    """Full information on Transactions which user has. Can be updated, created new one, or deleted. The balance will
    be changed in case of updating of the amount in any Transactions and in case of deleting. Sorting and filtering
    are also available """
    queryset = Transactions.objects.all()
    serializer_class = TransactionsSerializer
    permission_classes = [IsOwner]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['amount', 'time', 'category', ]
    ordering_fields = ['amount', 'time', 'category', ]

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


# simple function providing access to HTML form where token can be obtained.
def token_creation(request):
    return render(request, 'get_token.html', )
