from django.contrib import admin
from drf.models import Balance, Transactions, Categories


@admin.register(Balance)
class ServiceAdmin(admin.ModelAdmin):
    list_display = 'username', 'balance', 'id'
    list_filter = []


@admin.register(Transactions)
class ServiceAdmin(admin.ModelAdmin):
    list_display = 'username', 'amount', 'time', 'category', 'organisation'
    list_filter = []

@admin.register(Categories)
class ServiceAdmin(admin.ModelAdmin):
    list_display = 'username', 'category_list',
    list_filter = []
# Register your models here.
