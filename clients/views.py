import django_filters
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from pyexcel_xlsx import get_data as xlsx_get
from rest_framework import views, status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from clients.models import Client, Organization, Bill
from clients.serializers import ClientSerializer, BillSerializer


class ClientAndBillAPIPagination(PageNumberPagination):
    """
    Пагинация для API списков клиентов и счетов.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10


class BillFilterSet(FilterSet):
    """
    Фильтр по наименованиям организации и клиента для API списка счетов.
    """
    client = django_filters.CharFilter(field_name='client_org__client_name__name')
    org = django_filters.CharFilter(field_name='client_org__name')

    class Meta:
        model = Bill
        fields = ('client', 'org')


class UploadFilesDataClientAPIView(views.APIView):
    """
    Загружает данные из файлов `client_org.xlsx` и `bills.xlsx` в базу данных.
    """
    parser_classes = (MultiPartParser, )

    def post(self, request):
        is_file = {
            'client_org': True,
            'bills': True,
        }

        # проверка существование файлов client_org.xlsx и bills.xlsx
        try:
            client_org_file = request.FILES['client_org']
        except MultiValueDictKeyError:
            is_file['client_org'] = False

        try:
            bills_file = request.FILES['bills']
        except MultiValueDictKeyError:
            is_file['bills'] = False

        if not is_file['client_org'] and not is_file['bills']:
            return Response({'status': 'files not found'}, status.HTTP_400_BAD_REQUEST)

        if is_file['client_org']:

            # проверка формата файла client_org.xlsx
            if str(client_org_file).split('.')[-1] != 'xlsx':
                return Response({'status': 'file "client_org" is not xlsx format'}, status.HTTP_400_BAD_REQUEST)

            # сборка данных из вкладки client файла client_org.xlsx
            client_org_data = xlsx_get(client_org_file, column_limit=2)
            clients = client_org_data['client']

            # проверка на заполненность данных вкладки client
            if len(clients) > 1:
                for i in range(1, len(clients)):
                    if len(clients[i]) > 0:
                        client_name = clients[i][0]

                        # проверка уникальности поля name и запись их в бд
                        c = Client.objects.filter(name=client_name)
                        if c.count() == 0:
                            Client.objects.create(name=client_name)

            # сборка данных из вкладки organization файла client_org.xlsx
            organizations = client_org_data['organization']

            # проверка на заполненность данных вкладки organization и запись их в бд
            if len(organizations) > 1:
                prev_client_name = ''
                prev_client = None
                for i in range(1, len(organizations)):
                    if len(organizations[i]) > 0:
                        client_name = organizations[i][0]
                        org_name = organizations[i][1]

                        # проверка совместной уникальности полей client_name и name
                        org = Organization.objects.filter(client_name__name=client_name, name=org_name)
                        if org.count() == 0:

                            # сравнение имени клиента из предыдущей записи с текущей, чтобы не делать лишний запрос в бд,
                            # и запись данных в бд
                            if client_name == prev_client_name:
                                client = prev_client
                            else:
                                try:
                                    client = Client.objects.get(name=client_name)
                                except ObjectDoesNotExist:
                                    return Response({'status': f"client '{client_name}' does not exist"},
                                                    status.HTTP_400_BAD_REQUEST)

                            Organization.objects.create(client_name=client, name=org_name)
                            prev_client_name = client_name
                            prev_client = client

        if is_file['bills']:

            # проверка формата файла bills.xlsx
            if str(bills_file).split('.')[-1] != 'xlsx':
                return Response({'status': 'file "bills" is not xlsx format'}, status.HTTP_400_BAD_REQUEST)

            # сборка данных из вкладки Лист1 файла bills.xlsx
            bills_data = xlsx_get(bills_file, column_limit=4)
            bills = bills_data['Лист1']

            # проверка на заполненность данных вкладки Лист1
            if len(bills) > 1:
                prev_client_org_name = ''
                prev_client_org = 0
                for i in range(1, len(bills)):
                    if len(bills[i]) > 0:
                        client_org_name = bills[i][0]
                        bill_number = bills[i][1]

                        # проверка совместной уникальности полей client_org и №
                        bill = Bill.objects.filter(client_org__name=client_org_name, number=bill_number)
                        if bill.count() == 0:

                            # сравнение имени организации из предыдущей записи с текущей, чтобы не делать
                            # лишний запрос в бд, и запись данных в бд
                            if client_org_name == prev_client_org_name:
                                client_org = prev_client_org
                            else:
                                try:
                                    client_org = Organization.objects.get(name=client_org_name)
                                except ObjectDoesNotExist:
                                    return Response({'status': f"organization '{client_org_name}' does not exist"},
                                                    status.HTTP_400_BAD_REQUEST)

                            bill_sum = bills[i][2]
                            bill_date = bills[i][3]

                            Bill.objects.create(client_org=client_org, number=bill_number,
                                                sum=bill_sum, date=bill_date)
                            prev_client_org_name = client_org_name
                            prev_client_org = client_org

        return Response({'status': 'data from files uploaded successfully'})


class ClientListAPIView(generics.ListAPIView):
    """
    Возвращает список всех клиентов. Каждый элемент списка выводится с данными:
    - Название клиента;
    - Количество организаций;
    - Приход (сумма по счетам всех организаций клиента)
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    pagination_class = ClientAndBillAPIPagination


class BillListAPIView(generics.ListAPIView):
    """
    Возвращает список счетов с возможностью фильтрации по наименованию организации и/или по наименованию клиента.
    """
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

    filter_backends = (DjangoFilterBackend, )
    filterset_class = BillFilterSet
    filterset_fields = ('client', 'org')

    pagination_class = ClientAndBillAPIPagination
