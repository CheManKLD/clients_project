from django.urls import path

from clients.views import UploadFilesDataClientAPIView, ClientListAPIView, BillListAPIView

urlpatterns = [
    path('api/v1/upload-data/xlsx/', UploadFilesDataClientAPIView.as_view(), name='upload-data-xlsx'),
    path('api/v1/client-list/', ClientListAPIView.as_view(), name='client-list'),
    path('api/v1/bill-list/', BillListAPIView.as_view(), name='bill-list'),
]
