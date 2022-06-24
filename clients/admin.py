from django.contrib import admin

from clients.models import Client, Organization, Bill


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    pass


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    pass
