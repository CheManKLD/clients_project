from django.db.models import Sum, F
from rest_framework import serializers

from .models import Client, Organization, Bill


class ClientSerializer(serializers.ModelSerializer):
    total_orgs = serializers.SerializerMethodField()
    debit = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ('name', 'total_orgs', 'debit')

    def get_total_orgs(self, instance):
        return Organization.objects.filter(client_name=instance).count()

    def get_debit(self, instance):
        qs = Bill.objects.filter(client_org__client_name=instance.id).aggregate(sum=Sum('sum'))
        debit = qs['sum']

        if debit is None:
            debit = 0

        return debit


class BillSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    client_org = serializers.CharField(source='client_org.name', read_only=True)

    class Meta:
        model = Bill
        fields = ('client', 'client_org', 'number', 'sum', 'date')

    def get_client(self, instance):
        qs = Bill.objects.filter(pk=instance.id).annotate(client_name=F('client_org__client_name__name'))\
            .values('client_name')

        client = qs[0]['client_name']
        return client
